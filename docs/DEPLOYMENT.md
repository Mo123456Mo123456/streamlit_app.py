# 🚀 Silver — دليل النشر الكامل | Full deployment guide

من الصفر حتى تطبيق على متجري App Store وGoogle Play.

## المرحلة 1: نشر الخادم | Deploy the backend

تحتاج خادمًا (VPS من DigitalOcean/Hetzner/AWS بـ 5-10$ شهريًا يكفي للبداية) مع نطاق (domain).

```bash
# على الخادم
git clone <repo> silver && cd silver
cp .env.example .env
nano .env        # غيّر SILVER_ADMIN_PASSWORD و SILVER_JWT_SECRET إلزاميًا

docker compose up -d --build
# API:  http://SERVER_IP:8000   |   Web + لوحة الإدارة:  http://SERVER_IP:8501
```

### HTTPS (إلزامي للجوال في الإنتاج)

ضع Nginx/Caddy أمام الخدمتين. مثال Caddy (تلقائي الشهادات):

```
api.yourdomain.com {
    reverse_proxy localhost:8000
}
admin.yourdomain.com {
    reverse_proxy localhost:8501
}
```

ملاحظة: أبقِ لوحة الإدارة (8501) خلف جدار ناري أو Basic Auth إضافي.

## المرحلة 2: البث المباشر الحقيقي (صوت وصورة) | Real A/V

1. أنشئ مشروعًا مجانيًا على [LiveKit Cloud](https://cloud.livekit.io) (أو استضفه ذاتيًا).
2. ضع `LIVEKIT_URL` و`LIVEKIT_API_KEY` و`LIVEKIT_API_SECRET` في `.env` وأعد التشغيل.
3. الخادم يصدر توكنات الغرف تلقائيًا من `GET /live/{id}/rtc-token`:
   - المضيف والضيوف المقبولون: نشر واستقبال.
   - المشاهدون: استقبال فقط.
4. في التطبيق أضف `@livekit/react-native` واربطه بالتوكن (الواجهة والصلاحيات جاهزة).

بدون LiveKit يعمل كل شيء عدا نقل الفيديو نفسه (`/health` يبين حالة التهيئة).

## المرحلة 3: إشعارات الدفع | Push notifications

تعمل تلقائيًا عبر Expo:
- التطبيق يسجل توكن الجهاز في `POST /devices` بعد تسجيل الدخول.
- الخادم يرسل عبر Expo Push API عند: رسالة جديدة، متابعة جديدة، بدء بث لمن تتابعه.
- للنشر النهائي على المتاجر أضف بيانات FCM (أندرويد) وAPNs (آبل) في حساب Expo — راجع وثائق EAS.

## المرحلة 4: بناء تطبيقات المتاجر | Store binaries

```bash
cd mobile
# وجّه التطبيق إلى خادمك في app.json:
#   "extra": { "apiUrl": "https://api.yourdomain.com" }

npm install -g eas-cli
eas login                      # حساب Expo مجاني
eas build --platform android --profile production   # AAB لـ Google Play
eas build --platform android --profile preview      # APK للتجربة المباشرة
eas build --platform ios --profile production       # IPA لـ App Store
```

### متطلبات المتاجر (لا يمكن تجاوزها)
| | التكلفة | ملاحظات |
|---|---|---|
| Google Play Console | 25$ مرة واحدة | رفع AAB + مراجعة أيام قليلة |
| Apple Developer | 99$/سنة | مطلوب لأي تطبيق iOS + مراجعة آبل |

`eas submit --platform android|ios` يرفع مباشرة للمتجرين بعد ربط الحسابات.

## المرحلة 5: الترقية للنمو | Scaling path

بالترتيب عند الحاجة، البنية جاهزة لكل خطوة:
1. **PostgreSQL** بدل SQLite: المخطط منقول كما هو (`docs/DATABASE.md`)، استبدل طبقة الاتصال في `silver/db.py`.
2. **تخزين سحابي للوسائط** (S3/R2) بدل القرص المحلي: استبدل `services.save_upload` وقدّم عبر CDN.
3. **Redis pub/sub** للـ WebSocket عند تعدد خوادم الـ API (انظر `backend/realtime.py`).
4. عمال ضغط/تحويل فيديو (ffmpeg workers) للفيديوهات القصيرة.

## قائمة تحقق ما قبل الإطلاق | Pre-launch checklist

- [ ] `SILVER_JWT_SECRET` عشوائي وطويل
- [ ] كلمة مرور المدير مغيّرة
- [ ] HTTPS مفعّل على الـ API ولوحة الإدارة
- [ ] نسخ احتياطي مجدول لمجلد `/data` (قاعدة البيانات + الوسائط)
- [ ] LiveKit مهيأ إن أردت بث الفيديو الفعلي
- [ ] `apiUrl` في `mobile/app.json` يشير إلى نطاق HTTPS
- [ ] اختبار السيناريو الكامل: `python3 -m unittest tests.test_silver_acceptance tests.test_api`
