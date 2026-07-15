#!/usr/bin/env python3
"""Resolve and optionally download APK files from Cafe Bazaar."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, BinaryIO, Callable
from urllib.error import HTTPError, URLError
from urllib.parse import unquote, urlparse
from urllib.request import Request, urlopen


API_URL = "https://api.cafebazaar.ir/rest-v1/process/AppDownloadInfoRequest"
DEFAULT_CLIENT_VERSION = "28.1.0"
DEFAULT_CLIENT_VERSION_CODE = 2_800_100
DEFAULT_CPU = "x86,armeabi-v7a,armeabi"
DEFAULT_SDK = 27
PACKAGE_RE = re.compile(r"^[A-Za-z0-9_]+(?:\.[A-Za-z0-9_]+)+$")


class BazaarError(RuntimeError):
    """Raised when Bazaar cannot provide a usable download response."""


@dataclass(frozen=True)
class DownloadInfo:
    package_name: str
    url: str
    token: str
    cdn_prefix: str
    version_code: int
    package_size: int

    @property
    def size_mib(self) -> float:
        return self.package_size / 1024 / 1024

    @property
    def filename(self) -> str:
        return f"{self.package_name}-{self.version_code}.apk"


def parse_package(value: str) -> str:
    """Accept either an Android package name or a Cafe Bazaar app URL."""
    candidate = value.strip()
    parsed = urlparse(candidate)

    if parsed.scheme or parsed.netloc:
        if parsed.netloc.lower() not in {"cafebazaar.ir", "www.cafebazaar.ir"}:
            raise BazaarError("The URL must belong to cafebazaar.ir.")
        parts = [part for part in parsed.path.split("/") if part]
        if len(parts) < 2 or parts[-2] != "app":
            raise BazaarError("Expected a Cafe Bazaar app URL such as /app/com.example.app.")
        candidate = unquote(parts[-1])

    if not PACKAGE_RE.fullmatch(candidate):
        raise BazaarError(f"Invalid Android package name: {candidate!r}")
    return candidate


def build_payload(
    package_name: str,
    *,
    sdk: int = DEFAULT_SDK,
    cpu: str = DEFAULT_CPU,
) -> dict[str, Any]:
    """Build the request body used by Bazaar's Android client endpoint."""
    return {
        "properties": {
            "language": 2,
            "clientVersionCode": DEFAULT_CLIENT_VERSION_CODE,
            "androidClientInfo": {"sdkVersion": sdk, "cpu": cpu},
            "clientVersion": DEFAULT_CLIENT_VERSION,
            "isKidsEnabled": False,
        },
        "singleRequest": {
            "appDownloadInfoRequest": {
                "downloadStatus": 1,
                "packageName": package_name,
                "referrers": [],
            }
        },
    }


def resolve_download(
    package_name: str,
    *,
    sdk: int = DEFAULT_SDK,
    cpu: str = DEFAULT_CPU,
    timeout: float = 30,
    opener: Callable[..., BinaryIO] = urlopen,
) -> DownloadInfo:
    """Request download metadata and turn it into a direct APK URL."""
    payload = build_payload(package_name, sdk=sdk, cpu=cpu)
    request = Request(
        API_URL,
        data=json.dumps(payload, separators=(",", ":")).encode("utf-8"),
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "cafebazaar-apk-downloader-python/1.0",
        },
        method="POST",
    )

    try:
        with opener(request, timeout=timeout) as response:
            raw = response.read()
    except HTTPError as exc:
        raise BazaarError(f"Bazaar API returned HTTP {exc.code}.") from exc
    except URLError as exc:
        raise BazaarError(f"Could not reach Bazaar API: {exc.reason}") from exc

    try:
        document = json.loads(raw)
        reply = document["singleReply"]["appDownloadInfoReply"]
        token = str(reply["token"])
        prefixes = reply["cdnPrefix"]
        cdn_prefix = prefixes[0] if isinstance(prefixes, list) else prefixes
        version_code = int(reply.get("versionCode") or 0)
        package_size = int(reply.get("packageSize") or 0)
    except (KeyError, IndexError, TypeError, ValueError, json.JSONDecodeError) as exc:
        raise BazaarError("Bazaar returned an unexpected response.") from exc

    if not token or not cdn_prefix:
        raise BazaarError("Bazaar did not return a download token or CDN prefix.")

    url = f"{str(cdn_prefix).rstrip('/')}/apks/{token}.apk"
    return DownloadInfo(
        package_name=package_name,
        url=url,
        token=token,
        cdn_prefix=str(cdn_prefix),
        version_code=version_code,
        package_size=package_size,
    )


def download_apk(info: DownloadInfo, destination: Path, *, timeout: float = 60) -> Path:
    """Stream an APK to disk without keeping the whole file in memory."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    request = Request(info.url, headers={"User-Agent": "cafebazaar-apk-downloader-python/1.0"})
    try:
        with urlopen(request, timeout=timeout) as response, destination.open("wb") as output:
            while chunk := response.read(1024 * 1024):
                output.write(chunk)
    except (HTTPError, URLError, OSError) as exc:
        destination.unlink(missing_ok=True)
        raise BazaarError(f"APK download failed: {exc}") from exc
    return destination


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Resolve a direct APK link from Cafe Bazaar.",
    )
    parser.add_argument("app", help="Android package name or Cafe Bazaar app URL")
    parser.add_argument("--download", action="store_true", help="download the APK after resolving it")
    parser.add_argument("-o", "--output", type=Path, help="output APK path (implies --download)")
    parser.add_argument("--sdk", type=int, default=DEFAULT_SDK, help=f"Android SDK value (default: {DEFAULT_SDK})")
    parser.add_argument("--cpu", default=DEFAULT_CPU, help=f"CPU list (default: {DEFAULT_CPU})")
    parser.add_argument("--timeout", type=float, default=30, help="network timeout in seconds")
    parser.add_argument("--json", action="store_true", help="print metadata as JSON")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = make_parser().parse_args(argv)
    try:
        package_name = parse_package(args.app)
        info = resolve_download(
            package_name,
            sdk=args.sdk,
            cpu=args.cpu,
            timeout=args.timeout,
        )

        if args.json:
            payload = asdict(info) | {"size_mib": round(info.size_mib, 2)}
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            print(info.url)
            print(f"Package: {info.package_name}", file=sys.stderr)
            print(f"Version code: {info.version_code}", file=sys.stderr)
            print(f"Size: {info.size_mib:.2f} MiB", file=sys.stderr)

        if args.download or args.output:
            destination = args.output or Path(info.filename)
            saved = download_apk(info, destination, timeout=max(args.timeout, 60))
            print(f"Saved: {saved.resolve()}", file=sys.stderr)
        return 0
    except BazaarError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
