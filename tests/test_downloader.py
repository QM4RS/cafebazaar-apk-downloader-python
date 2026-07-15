import io
import json
import unittest

from cafebazaar_downloader import BazaarError, build_payload, parse_package, resolve_download


class FakeResponse(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


class DownloaderTests(unittest.TestCase):
    def test_parse_package_name(self):
        self.assertEqual(parse_package("com.example.app"), "com.example.app")

    def test_parse_app_url(self):
        self.assertEqual(
            parse_package("https://cafebazaar.ir/app/com.example.app?ref=test"),
            "com.example.app",
        )

    def test_rejects_unrelated_url(self):
        with self.assertRaises(BazaarError):
            parse_package("https://example.com/app/com.example.app")

    def test_payload_matches_client_defaults(self):
        payload = build_payload("com.example.app")
        properties = payload["properties"]
        request = payload["singleRequest"]["appDownloadInfoRequest"]
        self.assertEqual(properties["clientVersion"], "28.1.0")
        self.assertEqual(properties["clientVersionCode"], 2_800_100)
        self.assertEqual(properties["androidClientInfo"]["sdkVersion"], 27)
        self.assertEqual(request["packageName"], "com.example.app")

    def test_resolve_download_builds_direct_url(self):
        body = {
            "singleReply": {
                "appDownloadInfoReply": {
                    "token": "123?expire=999&token=abc&a=",
                    "cdnPrefix": ["https://cdn.example/"],
                    "packageSize": 10_485_760,
                    "versionCode": 42,
                }
            }
        }

        def opener(request, timeout):
            self.assertEqual(request.full_url, "https://api.cafebazaar.ir/rest-v1/process/AppDownloadInfoRequest")
            self.assertEqual(timeout, 12)
            return FakeResponse(json.dumps(body).encode())

        info = resolve_download("com.example.app", timeout=12, opener=opener)
        self.assertEqual(info.url, "https://cdn.example/apks/123?expire=999&token=abc&a=.apk")
        self.assertEqual(info.version_code, 42)
        self.assertEqual(info.size_mib, 10)


if __name__ == "__main__":
    unittest.main()
