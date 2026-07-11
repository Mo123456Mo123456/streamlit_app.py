# DermaView

فحص حي لبشرة الوجه والجسم — يعالج بث الكاميرا محليًا على الجهاز دون التقاط أو حفظ أو رفع أي صورة، ويرسل مؤشرات رقمية فقط (بموافقة صريحة) للحصول على ترشيحات المنتجات.

A live face & body skin scanner. All camera frames are analyzed on-device —
no image is ever captured, stored, or uploaded. Only numeric indicators are
sent (with explicit consent) to the product recommendation API.

## Structure

```
dermaview/
├── app/        # Flutter app (camera scanning, on-device analysis, Arabic RTL UI)
│   ├── pubspec.yaml
│   └── lib/main.dart
└── server/     # FastAPI product recommendation backend
    ├── server.py
    ├── requirements.txt
    └── examples/partner_catalog.json   # sample partner catalog feed
```

## Flutter app (`app/`)

Requires Flutter with Dart SDK >= 3.9.0. The app targets Android and iOS
(it uses `camera`, Google ML Kit face detection, and platform-specific
image formats — NV21 on Android, BGRA8888 on iOS).

```bash
cd dermaview/app
flutter create . --platforms=android,ios   # generate platform folders (first time only)
flutter pub get
flutter run --dart-define=DERMAVIEW_API_BASE_URL=http://10.0.2.2:8000
```

`DERMAVIEW_API_BASE_URL` defaults to `http://10.0.2.2:8000` (the Android
emulator's alias for the host machine). Point it at your deployed API for
real devices.

Platform notes:

- **Android**: add the camera permission to `android/app/src/main/AndroidManifest.xml`
  (`<uses-permission android:name="android.permission.CAMERA" />`) and set
  `minSdkVersion` to at least 21 (ML Kit requirement).
- **iOS**: add `NSCameraUsageDescription` to `ios/Runner/Info.plist`.

## Backend (`server/`)

Requires Python 3.10+.

```bash
cd dermaview/server
pip install -r requirements.txt
export DERMAVIEW_ADMIN_API_KEY=your-secret-key   # defaults to "change-me"
python server.py                                  # serves on 0.0.0.0:8000
```

Endpoints:

| Method | Path                          | Auth          | Purpose                              |
|--------|-------------------------------|---------------|--------------------------------------|
| GET    | `/health`                     | —             | Health check                         |
| POST   | `/v1/recommendations`         | —             | Product matching from numeric metrics |
| POST   | `/v1/admin/companies`         | `X-Admin-Key` | Register a partner company           |
| PUT    | `/v1/admin/products`          | `X-Admin-Key` | Upsert a product                     |
| POST   | `/v1/admin/sync/{company_id}` | `X-Admin-Key` | Pull a partner's catalog feed        |

The SQLite database (`dermaview.db` by default, override with
`DERMAVIEW_DATABASE_PATH`) is created and seeded with demo products on
startup. `/v1/recommendations` rejects any request carrying image, video,
or multipart content — it accepts JSON numeric indicators only.

Partner catalog feeds must return JSON in the shape of
`examples/partner_catalog.json`.

## Privacy model

- Frames are processed in memory on-device; no image file is ever created.
- Face scans exclude eye and mouth regions from analysis.
- Only numeric metrics (0–100 indicators + quality/confidence) leave the device, and only after an explicit consent checkbox.
- Results are cosmetic visual indicators, not a medical diagnosis.
- Scan history is stored locally in encrypted secure storage and can be wiped from the privacy center.
