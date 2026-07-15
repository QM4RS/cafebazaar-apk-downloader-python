# Cafe Bazaar APK Downloader

A small, zero-dependency Python CLI for resolving direct APK links from Cafe Bazaar and optionally downloading the files.

[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Dependencies: zero](https://img.shields.io/badge/dependencies-zero-brightgreen)](pyproject.toml)

## Features

- Accepts an Android package name or a Cafe Bazaar app URL
- Prints a direct APK URL
- Downloads APKs with streaming I/O
- Supports machine-readable JSON output
- Allows custom Android SDK and CPU values
- Uses only the Python standard library

## Requirements

- Python 3.9 or newer

## Quick start

```bash
git clone https://github.com/QM4RS/cafebazaar-apk-downloader-python.git
cd cafebazaar-apk-downloader-python
python cafebazaar_downloader.py com.ziipin.softkeyboard.iran
```

You can also pass a full app URL:

```bash
python cafebazaar_downloader.py \
  https://cafebazaar.ir/app/com.ziipin.softkeyboard.iran
```

## Usage

Resolve and print a direct APK link:

```bash
python cafebazaar_downloader.py com.example.app
```

Download the APK:

```bash
python cafebazaar_downloader.py com.example.app --download
```

Choose the output path:

```bash
python cafebazaar_downloader.py com.example.app --output app.apk
```

Print JSON metadata:

```bash
python cafebazaar_downloader.py com.example.app --json
```

Override the device profile:

```bash
python cafebazaar_downloader.py com.example.app \
  --sdk 33 \
  --cpu "arm64-v8a,armeabi-v7a"
```

Install it as a command:

```bash
python -m pip install .
cafebazaar-apk com.example.app
```

## Default request profile

| Setting | Value |
|---|---:|
| Client version | `28.1.0` |
| Client version code | `2800100` |
| Minimum Android SDK | `27` |
| CPU | `x86,armeabi-v7a,armeabi` |

## Tests

```bash
python -m unittest discover -s tests -v
```

## Notes

- Paid or account-bound apps may not return a download link.
- Generated links may expire.
- The Cafe Bazaar API may change without notice.
- You are responsible for complying with Cafe Bazaar's terms and app publishers' rights.

## License

MIT. See [LICENSE](LICENSE).
