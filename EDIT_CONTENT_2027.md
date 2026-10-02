# ویرایش محتوای CSF Research 2027 / Editing content

## فارسی

متن‌های نسخه مستقل وب در فایل **content.js در ریشه مخزن** قرار دارند؛ فایل قدیمی `csf_mobile/ui_texts.json` مربوط به نسخه Streamlit است.

1. در گیت‌هاب فایل `content.js` را باز کنید و دکمه مداد (Edit) را بزنید.
2. فقط متن داخل کوتیشن‌ها را تغییر دهید. نام کلیدها، ویرگول‌ها و ساختار فایل را حفظ کنید. برای کوتیشن داخل متن از `\"` و برای خط جدید از `\n` استفاده کنید.
3. تغییر را با **Commit changes** روی شاخه `main` ذخیره کنید.
4. پس از موفق‌شدن اجرای **pages build and deployment** در بخش Actions، صفحه سایت را دوباره بارگذاری کنید. اگر متن قبلی دیده می‌شود، مرورگر را با Ctrl+Shift+R تازه کنید.

| کلید | کاربرد |
|---|---|
| pageTitle | عنوان تب مرورگر |
| fuzzySetName | نام کامل مجموعه فازی در سربرگ |
| developerCredit | معرفی توسعه‌دهنده تکنیک و نرم‌افزار در سربرگ |
| authorName / affiliation / footerCredit | نام، وابستگی دانشگاهی و متن پایین صفحه |
| labels | متن دکمه‌ها، عنوان‌ها و توضیحات عمومی |
| methods.swara / methods.cocoso | عنوان، معرفی، نام روش و متن دکمه محاسبه هر روش |
| sections | بخش‌های توضیحی دلخواه زیر فضای محاسبات |
| helpSections | بخش‌های توضیحی اضافی در پنجره راهنما |

برای افزودن محتوا، به‌جای آرایه خالی `sections` بنویسید:

```javascript
"sections": [
  {"title": "About this project", "body": "Your introduction here.", "enabled": true},
  {"title": "راهنمای پژوهش", "body": "متن فارسی شما", "enabled": true}
]
```

برای پنهان‌کردن یک بخش `enabled` را `false` کنید؛ برای حذف آن، کل شیء مربوط را از آرایه بردارید و ویرگول‌ها را مرتب کنید. متن‌ها به‌صورت متن ساده نمایش داده می‌شوند؛ HTML اجرا نمی‌شود. رشته خالی `""` متن قابل تنظیم را خالی می‌کند. حذف کلیدهای اصلی باعث استفاده از متن پیش‌فرض می‌شود؛ حذف یک بخش از آرایه، آن بخش را حذف می‌کند.

این فایل برای **محتوا** است. تغییر فرمول‌ها، افزودن روش محاسباتی یا تغییر ساختار فایل ورودی نیاز به تغییر برنامه و آزمون دارد. راهنمای فنی اصلی و پیام‌های خطای محاسبات عمداً در کد برنامه باقی مانده‌اند.

### اعمال تغییر در اپ اندروید

اپ آفلاین نسخه بسته‌بندی‌شده همین فایل‌ها را استفاده می‌کند؛ تغییر گیت‌هاب خودکار روی APK نصب‌شده اعمال نمی‌شود.

1. بسته **Full Source** مربوط به آخرین انتشار را دریافت و باز کنید.
2. فایل‌های وب جدید را در `csf-site/dist/` و `android/app/src/main/assets/web/` قرار دهید.
3. `versionCode` را در `android/app/build.gradle` و `android/app/src/main/AndroidManifest.xml` افزایش دهید و نسخه را هماهنگ کنید.
4. طبق `android/README.md` فایل APK را با **کلید امضای اصلی خودتان** بسازید و به‌صورت به‌روزرسانی نصب کنید. کلید امضا و رمز آن را روی گیت‌هاب بارگذاری نکنید.

## English

Edit **content.js at the repository root** to customize the standalone web edition. `csf_mobile/ui_texts.json` belongs to the older Streamlit edition.

Change text values, preserve JavaScript syntax, and commit to `main`. After the Pages deployment succeeds, reload the website. The configuration covers the header, developer credit, affiliation, main labels, method titles/descriptions, and optional information sections.

Add or remove objects in `sections` (below the workspace) or `helpSections` (in the help dialog). Each object supports `title`, `body`, and `enabled`. Set `enabled: false` to hide a section. Content is rendered as plain text, not HTML. Missing main keys use defaults; an empty string clears a configured label.

The Android app bundles these files for offline use. Website edits do not update an installed APK automatically. Copy the updated web files into both source locations listed above, increment the Android version code, and rebuild using the original private signing key, following `android/README.md`. Changes to calculations or input formats require code changes and appropriate tests.
