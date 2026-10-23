# tv-home

Qatar4u TV Home: Apple TV–style launcher for Android TV, with offline Umm al-Qura prayer times, live weather and Qatar landmark wallpapers.


نسخة معدّلة من [cleanyourtv](https://github.com/Gathin23/cleanyourtv) (رخصة MIT)، جُرّبت على شاشة TCL 55C6US (Percee TV، أندرويد تي في 8).

## الإضافات

- **مواقيت الصلاة** تحت الساعة: طريقة أم القرى (الفجر 18.5°، العشاء بعد المغرب بـ90 دقيقة و120 في رمضان)، تُحسب داخل الجهاز بلا إنترنت. الصلاة القادمة مميّزة ومعها الوقت المتبقي، والتاريخ الهجري تحتها. الكود: `launcher/.../PrayerTimes.java`.
- **الطقس الحالي** من Open-Meteo بلا مفتاح، كل 30 دقيقة، ويُحفظ آخر رد لوقت انقطاع الإنترنت. الكود: `InfoPanel.java`.
- **خلفية لكل تطبيق**: `wallpapers/apps.txt` يربط اسم الحزمة بصورة، وأي تطبيق غير مذكور يأخذ صورة ثابتة من المجموعة. الكود: `WallpaperPlayer.showApp`.
- **ثيم `themes/qatar4u`**: عشر رسومات لمعالم قطر، رُسمت بالكود في `tools/qatar4u/qatar_scenes.py`.

## الإعداد

في `launcher/app/src/main/res/values/config.xml`:

```xml
<bool name="info_panel">true</bool>
<string name="info_city">دخان</string>
<string name="info_lat">25.4250</string>
<string name="info_lon">50.7850</string>
```

## البناء والتثبيت

البناء بنفس طريقة المشروع الأصلي (`launcher/build-and-install.ps1`). بعده انسخ الثيم إلى التلفزيون:

```
adb push themes/qatar4u/config.json /sdcard/Android/data/com.gathin.tvhome/files/config.json
adb push themes/qatar4u/wallpapers /sdcard/Android/data/com.gathin.tvhome/files/
```

## ملاحظات عن TCL 55C6US

- منفذ ADB الشبكي يُفتح من قائمة المصنع: الصورة ← إعدادات متقدمة ← قف على التباين واكتب 1950 ← Other ← ADB. ويلزم معه "تصحيح أخطاء USB" من خيارات المطوّر.
- الواجهة الأصلية `tvlauncher` تبقى الافتراضية حتى بعد `set-home-activity`، لذلك يلزم تعطيلها.
- أي تطبيق آخر يعلن نفسه واجهةً رئيسية (مثل App Starter) يجعل الشاشة تسأل عن الواجهة بعد كل إعادة تشغيل.

## الفحص التلقائي (GitHub Actions)

ملف `.github/workflows/qatar4u.yml` يعمل مع كل رفع:
- **فحص الثيم**: يتأكد أن `config.json` سليم، وأن كل تطبيق في `apps.txt` مربوط بصورة موجودة، وأن حجم كل صورة أقل من 300 كيلوبايت.
- **الواجهة**: اختبارات الوحدة (ومنها اختبارات مواقيت الصلاة مقارنة بمواقيت الدوحة)، وفحص lint، وبناء نسخة الإصدار، وحدّ أقصى لحجم الـ APK قدره 512 كيلوبايت.
- **ملف APK جاهز**: يُحفظ 30 يومًا في صفحة الفحص باسم `Qatar4u-TV-Home`.
- **إصدار رسمي**: عند إنشاء وسم (tag) يبدأ بـ `v`، مثل `v2.6-q4u.1`، يُرفق الـ APK بصفحة Release لتثبيته على الشاشة دون بناء.

## الفرق عن المشروع الأصلي

المشروع الأصلي يمنع الإنترنت داخل الواجهة. هذه النسخة تضيف صلاحية `INTERNET` من أجل الطقس فقط.

## المشروع الأصلي

شرح المشروع الأصلي كاملًا في [README.upstream.md](README.upstream.md).
