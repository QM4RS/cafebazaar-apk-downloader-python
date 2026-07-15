<div dir="rtl" align="right">

# دانلودر APK کافه‌بازار با پایتون

یک ابزار خط فرمان سبک و بدون وابستگی خارجی برای دریافت لینک مستقیم APK از کافه‌بازار و دانلود اختیاری فایل.

![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Dependencies](https://img.shields.io/badge/dependencies-zero-brightgreen)

</div>

---

## قابلیت‌ها

- دریافت نام پکیج یا لینک صفحهٔ برنامه در کافه‌بازار
- نمایش لینک مستقیم APK
- دانلود مستقیم و جریانی فایل، بدون نگه‌داشتن کل APK در حافظه
- خروجی JSON برای استفاده در ابزارهای دیگر
- امکان انتخاب Android SDK و معماری CPU
- فقط با کتابخانهٔ استاندارد پایتون؛ بدون `requests` یا وابستگی جانبی

## سازوکار

افزونهٔ Chrome با شناسهٔ `imnogedkmanognaahdphhfhgehlfgdoh` این مراحل را انجام می‌دهد:

```text
package name
    │
    ▼
POST /rest-v1/process/AppDownloadInfoRequest
    │
    ├── token
    ├── cdnPrefix[0]
    ├── versionCode
    └── packageSize
    │
    ▼
{cdnPrefix}/apks/{token}.apk
```

این پروژه همان قرارداد درخواست را به پایتون منتقل می‌کند. مقادیر پیش‌فرض برای سازگاری با افزونه حفظ شده‌اند:

| گزینه | مقدار پیش‌فرض |
|---|---|
| نسخهٔ کلاینت | `11.3.1` |
| کد نسخهٔ کلاینت | `1100301` |
| Android SDK | `22` |
| CPU | `x86,armeabi-v7a,armeabi` |

## شروع سریع

نیازمندی: Python 3.9 یا جدیدتر.

```bash
git clone https://github.com/QM4RS/cafebazaar-apk-downloader-python.git
cd cafebazaar-apk-downloader-python
python cafebazaar_downloader.py com.ziipin.softkeyboard.iran
```

ورودی می‌تواند لینک کامل صفحه هم باشد:

```bash
python cafebazaar_downloader.py \
  https://cafebazaar.ir/app/com.ziipin.softkeyboard.iran
```

برای دانلود فایل:

```bash
python cafebazaar_downloader.py com.ziipin.softkeyboard.iran --download
```

تعیین مسیر خروجی:

```bash
python cafebazaar_downloader.py com.ziipin.softkeyboard.iran \
  --output keyboard.apk
```

خروجی ساختاریافته:

```bash
python cafebazaar_downloader.py com.ziipin.softkeyboard.iran --json
```

تغییر مشخصات دستگاه:

```bash
python cafebazaar_downloader.py com.example.app \
  --sdk 33 \
  --cpu "arm64-v8a,armeabi-v7a"
```

نصب به‌عنوان فرمان سیستم:

```bash
python -m pip install .
cafebazaar-apk com.example.app
```

## تست

```bash
python -m unittest discover -s tests -v
```

## محدودیت‌ها

- برنامه‌های پولی یا برنامه‌هایی که نیازمند حساب کاربری/مالکیت هستند ممکن است لینک دانلود ندهند.
- API کافه‌بازار عمومی و نسخه‌بندی‌شده برای توسعه‌دهندگان ثالث نیست و ممکن است در آینده تغییر کند.
- لینک‌های تولیدشده ممکن است زمان انقضا داشته باشند.
- مسئولیت رعایت شرایط استفادهٔ کافه‌بازار و حقوق ناشر برنامه با کاربر است.

## اعتبار و مجوز

منطق درخواست بر اساس افزونهٔ متن‌باز **Cafebazaar APK Downloader** نوشتهٔ Ali Borhani بررسی و به پایتون بازنویسی شده است. افزونهٔ اصلی و این بازنویسی تحت مجوز MIT هستند؛ متن کامل در [LICENSE](LICENSE) قرار دارد.
