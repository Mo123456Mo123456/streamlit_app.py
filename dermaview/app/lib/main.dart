import 'dart:async';
import 'dart:convert';
import 'dart:io';
import 'dart:math';
import 'dart:typed_data';
import 'dart:ui' as ui;

import 'package:camera/camera.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:google_mlkit_commons/google_mlkit_commons.dart';
import 'package:google_mlkit_face_detection/google_mlkit_face_detection.dart';
import 'package:http/http.dart' as http;
import 'package:uuid/uuid.dart';

const apiBase = String.fromEnvironment(
  'DERMAVIEW_API_BASE_URL',
  defaultValue: 'http://10.0.2.2:8000',
);

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const DermaViewApp());
}

enum BodyRegion {
  face,
  neck,
  chest,
  abdomen,
  upperBack,
  lowerBack,
  leftUpperArm,
  rightUpperArm,
  leftForearm,
  rightForearm,
  leftElbow,
  rightElbow,
  leftHand,
  rightHand,
  leftThigh,
  rightThigh,
  leftKnee,
  rightKnee,
  leftShin,
  rightShin,
  leftFoot,
  rightFoot,
  leftHeel,
  rightHeel,
}

extension BodyRegionX on BodyRegion {
  String get wireName => name.replaceAllMapped(
        RegExp(r'([A-Z])'),
        (m) => '_${m.group(1)!.toLowerCase()}',
      );

  String get label => const {
        BodyRegion.face: 'الوجه',
        BodyRegion.neck: 'الرقبة',
        BodyRegion.chest: 'الصدر',
        BodyRegion.abdomen: 'البطن',
        BodyRegion.upperBack: 'أعلى الظهر',
        BodyRegion.lowerBack: 'أسفل الظهر',
        BodyRegion.leftUpperArm: 'أعلى الذراع الأيسر',
        BodyRegion.rightUpperArm: 'أعلى الذراع الأيمن',
        BodyRegion.leftForearm: 'الساعد الأيسر',
        BodyRegion.rightForearm: 'الساعد الأيمن',
        BodyRegion.leftElbow: 'الكوع الأيسر',
        BodyRegion.rightElbow: 'الكوع الأيمن',
        BodyRegion.leftHand: 'اليد اليسرى',
        BodyRegion.rightHand: 'اليد اليمنى',
        BodyRegion.leftThigh: 'الفخذ الأيسر',
        BodyRegion.rightThigh: 'الفخذ الأيمن',
        BodyRegion.leftKnee: 'الركبة اليسرى',
        BodyRegion.rightKnee: 'الركبة اليمنى',
        BodyRegion.leftShin: 'الساق اليسرى',
        BodyRegion.rightShin: 'الساق اليمنى',
        BodyRegion.leftFoot: 'القدم اليسرى',
        BodyRegion.rightFoot: 'القدم اليمنى',
        BodyRegion.leftHeel: 'الكعب الأيسر',
        BodyRegion.rightHeel: 'الكعب الأيمن',
      }[this]!;

  bool get useFront => this == BodyRegion.face || this == BodyRegion.neck;

  List<String> get concerns {
    if (this == BodyRegion.face) {
      return const [
        'visible_dryness',
        'redness',
        'tone_uniformity',
        'texture',
        'fine_lines',
        'oiliness',
      ];
    }

    if ({
      BodyRegion.leftElbow,
      BodyRegion.rightElbow,
      BodyRegion.leftKnee,
      BodyRegion.rightKnee,
      BodyRegion.leftHeel,
      BodyRegion.rightHeel,
    }.contains(this)) {
      return const [
        'visible_dryness',
        'texture',
        'tone_uniformity',
      ];
    }

    return const [
      'visible_dryness',
      'redness',
      'tone_uniformity',
      'texture',
      'oiliness',
    ];
  }
}

class SkinMetrics {
  const SkinMetrics({
    required this.visibleDryness,
    required this.redness,
    required this.toneUniformity,
    required this.texture,
    required this.fineLines,
    required this.oiliness,
    required this.quality,
    required this.confidence,
  });

  final double visibleDryness;
  final double redness;
  final double toneUniformity;
  final double texture;
  final double fineLines;
  final double oiliness;
  final double quality;
  final double confidence;

  double value(String key) => switch (key) {
        'visible_dryness' => visibleDryness,
        'redness' => redness,
        'tone_uniformity' => toneUniformity,
        'texture' => texture,
        'fine_lines' => fineLines,
        'oiliness' => oiliness,
        _ => 0,
      };

  Map<String, dynamic> toJson() => {
        'visible_dryness': visibleDryness,
        'redness': redness,
        'tone_uniformity': toneUniformity,
        'texture': texture,
        'fine_lines': fineLines,
        'oiliness': oiliness,
        'quality': quality,
        'confidence': confidence,
        'model_version': 'visual-proxy-1.0.0',
      };

  factory SkinMetrics.fromJson(Map<String, dynamic> json) {
    return SkinMetrics(
      visibleDryness: (json['visible_dryness'] as num).toDouble(),
      redness: (json['redness'] as num).toDouble(),
      toneUniformity: (json['tone_uniformity'] as num).toDouble(),
      texture: (json['texture'] as num).toDouble(),
      fineLines: (json['fine_lines'] as num).toDouble(),
      oiliness: (json['oiliness'] as num).toDouble(),
      quality: (json['quality'] as num).toDouble(),
      confidence: (json['confidence'] as num).toDouble(),
    );
  }

  static SkinMetrics average(List<SkinMetrics> list) {
    double avg(double Function(SkinMetrics metrics) pick) {
      return list.map(pick).reduce((a, b) => a + b) / list.length;
    }

    return SkinMetrics(
      visibleDryness: avg((m) => m.visibleDryness),
      redness: avg((m) => m.redness),
      toneUniformity: avg((m) => m.toneUniformity),
      texture: avg((m) => m.texture),
      fineLines: avg((m) => m.fineLines),
      oiliness: avg((m) => m.oiliness),
      quality: avg((m) => m.quality),
      confidence: avg((m) => m.confidence),
    );
  }
}

class DermaViewApp extends StatelessWidget {
  const DermaViewApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'DermaView',
      theme: ThemeData(
        useMaterial3: true,
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF087C73),
        ),
      ),
      builder: (context, child) {
        return Directionality(
          textDirection: TextDirection.rtl,
          child: child!,
        );
      },
      home: const ConsentScreen(),
    );
  }
}

class ConsentScreen extends StatefulWidget {
  const ConsentScreen({super.key});

  @override
  State<ConsentScreen> createState() => _ConsentScreenState();
}

class _ConsentScreenState extends State<ConsentScreen> {
  bool accepted = false;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('DermaView')),
      body: ListView(
        padding: const EdgeInsets.all(22),
        children: [
          const Icon(
            Icons.privacy_tip_outlined,
            size: 88,
          ),
          const SizedBox(height: 16),
          Text(
            'شاهد احتياج بشرتك، لا صورتك.',
            textAlign: TextAlign.center,
            style: Theme.of(context).textTheme.headlineSmall,
          ),
          const SizedBox(height: 18),
          const Card(
            child: Padding(
              padding: EdgeInsets.all(18),
              child: Text(
                'يعالج التطبيق بث الكاميرا محليًا دون التقاط صورة أو حفظها. '
                'النتائج مؤشرات تجميلية مرئية وليست تشخيصًا طبيًا.',
              ),
            ),
          ),
          CheckboxListTile(
            value: accepted,
            contentPadding: EdgeInsets.zero,
            title: const Text(
              'أوافق على الفحص المحلي واستخدام الكاميرا.',
            ),
            onChanged: (value) {
              setState(() => accepted = value ?? false);
            },
          ),
          FilledButton(
            onPressed: accepted
                ? () {
                    Navigator.pushReplacement(
                      context,
                      MaterialPageRoute(
                        builder: (_) => const HomeScreen(),
                      ),
                    );
                  }
                : null,
            child: const Text('متابعة'),
          ),
        ],
      ),
    );
  }
}

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('DermaView'),
        actions: [
          IconButton(
            tooltip: 'مركز الخصوصية',
            onPressed: () {
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (_) => const PrivacyScreen(),
                ),
              );
            },
            icon: const Icon(Icons.shield_outlined),
          ),
        ],
      ),
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          Text(
            'فحص حي لبشرة الوجه والجسم',
            style: Theme.of(context).textTheme.headlineSmall,
          ),
          const SizedBox(height: 8),
          const Text('لا تصوير • لا رفع صور • لا تخزين صور'),
          const SizedBox(height: 22),
          FilledButton.icon(
            onPressed: () {
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (_) => const RegionScreen(),
                ),
              );
            },
            icon: const Icon(Icons.document_scanner_outlined),
            label: const Text('ابدأ الفحص'),
          ),
          const SizedBox(height: 10),
          OutlinedButton.icon(
            onPressed: () {
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (_) => const HistoryScreen(),
                ),
              );
            },
            icon: const Icon(Icons.history),
            label: const Text('سجل الفحوص'),
          ),
        ],
      ),
    );
  }
}

class RegionScreen extends StatelessWidget {
  const RegionScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('اختر منطقة الفحص'),
      ),
      body: GridView.builder(
        padding: const EdgeInsets.all(14),
        gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
          crossAxisCount: 2,
          childAspectRatio: 2.5,
          crossAxisSpacing: 8,
          mainAxisSpacing: 8,
        ),
        itemCount: BodyRegion.values.length,
        itemBuilder: (context, index) {
          final region = BodyRegion.values[index];

          return FilledButton.tonal(
            onPressed: () {
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (_) => ScannerScreen(region: region),
                ),
              );
            },
            child: Text(
              region.label,
              textAlign: TextAlign.center,
            ),
          );
        },
      ),
    );
  }
}

class ScannerScreen extends StatefulWidget {
  const ScannerScreen({
    required this.region,
    super.key,
  });

  final BodyRegion region;

  @override
  State<ScannerScreen> createState() => _ScannerScreenState();
}

class _ScannerScreenState extends State<ScannerScreen>
    with WidgetsBindingObserver {
  CameraController? controller;
  CameraDescription? cameraInfo;

  final FaceDetector detector = FaceDetector(
    options: FaceDetectorOptions(
      performanceMode: FaceDetectorMode.fast,
      enableContours: true,
      minFaceSize: 0.18,
    ),
  );

  final VisualAnalyzer analyzer = VisualAnalyzer();
  final List<SkinMetrics> samples = [];

  bool busy = false;
  bool completed = false;
  DateTime? lastRun;

  String message = 'وجّه الكاميرا للمنطقة داخل الإطار.';
  String? error;

  static const int requiredFrames = 8;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);
    initialize();
  }

  Future<void> initialize() async {
    try {
      final cameras = await availableCameras();

      if (cameras.isEmpty) {
        throw StateError('لم يتم العثور على كاميرا في الجهاز.');
      }

      final direction = widget.region.useFront
          ? CameraLensDirection.front
          : CameraLensDirection.back;

      final matches = cameras.where(
        (camera) => camera.lensDirection == direction,
      );

      cameraInfo = matches.isNotEmpty ? matches.first : cameras.first;

      final newController = CameraController(
        cameraInfo!,
        ResolutionPreset.medium,
        enableAudio: false,
        imageFormatGroup: Platform.isAndroid
            ? ImageFormatGroup.nv21
            : ImageFormatGroup.bgra8888,
      );

      await newController.initialize();

      await newController.startImageStream(
        (image) => unawaited(process(image)),
      );

      if (!mounted) {
        await newController.dispose();
        return;
      }

      setState(() => controller = newController);
    } catch (exception) {
      if (mounted) {
        setState(() => error = exception.toString());
      }
    }
  }

  Future<void> process(CameraImage image) async {
    if (busy || completed || controller == null || cameraInfo == null) {
      return;
    }

    final now = DateTime.now();

    if (lastRun != null &&
        now.difference(lastRun!).inMilliseconds < 330) {
      return;
    }

    lastRun = now;
    busy = true;

    try {
      ui.Rect regionOfInterest;
      double detectionConfidence;
      List<ui.Rect> exclusions = const [];

      if (widget.region == BodyRegion.face) {
        final input = createInputImage(
          image,
          cameraInfo!,
          controller!.value.deviceOrientation,
        );

        if (input == null) {
          updateMessage('تنسيق الكاميرا غير مدعوم.');
          return;
        }

        final faces = await detector.processImage(input);

        if (faces.length != 1) {
          updateMessage('ضع وجهًا واحدًا فقط داخل الإطار.');
          return;
        }

        regionOfInterest = clampRect(
          faces.first.boundingBox,
          image.width,
          image.height,
        );

        detectionConfidence = 0.92;

        exclusions = const [
          ui.Rect.fromLTWH(0.10, 0.18, 0.35, 0.26),
          ui.Rect.fromLTWH(0.55, 0.18, 0.35, 0.26),
          ui.Rect.fromLTWH(0.27, 0.62, 0.46, 0.25),
        ];
      } else {
        /*
         * في النسخة الأولى للجسم، يضع المستخدم المنطقة داخل الإطار.
         * لاحقًا يمكن استبدال هذا الجزء بـ MediaPipe Pose.
         */
        regionOfInterest = ui.Rect.fromLTWH(
          image.width * 0.18,
          image.height * 0.18,
          image.width * 0.64,
          image.height * 0.64,
        );

        detectionConfidence = 0.80;
      }

      final metrics = analyzer.analyze(
        image: image,
        region: widget.region,
        roi: regionOfInterest,
        exclusions: exclusions,
        detectionConfidence: detectionConfidence,
      );

      if (metrics == null) {
        updateMessage(
          'حسّن الإضاءة وثبّت الهاتف واقترب قليلًا.',
        );
        return;
      }

      samples.add(metrics);

      updateMessage(
        'جارٍ جمع إطارات صالحة '
        '${samples.length}/$requiredFrames',
      );

      if (samples.length >= requiredFrames) {
        completed = true;

        await stopStream();

        if (!mounted) return;

        Navigator.pushReplacement(
          context,
          MaterialPageRoute(
            builder: (_) => ResultScreen(
              region: widget.region,
              metrics: SkinMetrics.average(samples),
            ),
          ),
        );
      }
    } catch (exception) {
      updateMessage('تعذر تحليل الإطار: $exception');
    } finally {
      busy = false;
    }
  }

  InputImage? createInputImage(
    CameraImage image,
    CameraDescription camera,
    DeviceOrientation orientation,
  ) {
    const orientations = <DeviceOrientation, int>{
      DeviceOrientation.portraitUp: 0,
      DeviceOrientation.landscapeLeft: 90,
      DeviceOrientation.portraitDown: 180,
      DeviceOrientation.landscapeRight: 270,
    };

    InputImageRotation? rotation;

    if (Platform.isIOS) {
      rotation = InputImageRotationValue.fromRawValue(
        camera.sensorOrientation,
      );
    } else {
      final compensation = orientations[orientation];

      if (compensation == null) return null;

      final degrees = camera.lensDirection ==
              CameraLensDirection.front
          ? (camera.sensorOrientation + compensation) % 360
          : (camera.sensorOrientation - compensation + 360) %
              360;

      rotation = InputImageRotationValue.fromRawValue(degrees);
    }

    final format = InputImageFormatValue.fromRawValue(
      image.format.raw,
    );

    if (rotation == null ||
        format == null ||
        image.planes.length != 1) {
      return null;
    }

    final plane = image.planes.first;

    return InputImage.fromBytes(
      bytes: Uint8List.fromList(plane.bytes),
      metadata: InputImageMetadata(
        size: ui.Size(
          image.width.toDouble(),
          image.height.toDouble(),
        ),
        rotation: rotation,
        format: format,
        bytesPerRow: plane.bytesPerRow,
      ),
    );
  }

  ui.Rect clampRect(ui.Rect rect, int width, int height) {
    return ui.Rect.fromLTRB(
      rect.left.clamp(0, width - 1),
      rect.top.clamp(0, height - 1),
      rect.right.clamp(1, width),
      rect.bottom.clamp(1, height),
    );
  }

  void updateMessage(String value) {
    if (mounted) {
      setState(() => message = value);
    }
  }

  Future<void> stopStream() async {
    final currentController = controller;

    if (currentController != null &&
        currentController.value.isStreamingImages) {
      await currentController.stopImageStream();
    }
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    if (state == AppLifecycleState.paused ||
        state == AppLifecycleState.inactive ||
        state == AppLifecycleState.detached) {
      unawaited(stopStream());
    }
  }

  @override
  void dispose() {
    WidgetsBinding.instance.removeObserver(this);
    unawaited(stopStream());
    controller?.dispose();
    detector.close();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    if (error != null) {
      return Scaffold(
        body: Center(
          child: Padding(
            padding: const EdgeInsets.all(20),
            child: Text(error!),
          ),
        ),
      );
    }

    final currentController = controller;

    if (currentController == null ||
        !currentController.value.isInitialized) {
      return const Scaffold(
        body: Center(
          child: CircularProgressIndicator(),
        ),
      );
    }

    return Scaffold(
      backgroundColor: Colors.black,
      appBar: AppBar(
        title: Text(widget.region.label),
        backgroundColor: Colors.black,
        foregroundColor: Colors.white,
      ),
      body: Stack(
        fit: StackFit.expand,
        children: [
          CameraPreview(currentController),
          CustomPaint(
            painter: GuidePainter(
              progress: samples.length / requiredFrames,
            ),
          ),
          Positioned(
            left: 16,
            right: 16,
            bottom: 24,
            child: Card(
              color: Colors.black.withValues(alpha: 0.78),
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Text(
                      message,
                      textAlign: TextAlign.center,
                      style: const TextStyle(
                        color: Colors.white,
                      ),
                    ),
                    const SizedBox(height: 10),
                    LinearProgressIndicator(
                      value: samples.length / requiredFrames,
                    ),
                    const SizedBox(height: 8),
                    const Text(
                      'لا يتم إنشاء ملف صورة',
                      style: TextStyle(
                        color: Colors.greenAccent,
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class Rgb {
  const Rgb(this.r, this.g, this.b);

  final int r;
  final int g;
  final int b;

  double get luminance {
    return 0.2126 * r + 0.7152 * g + 0.0722 * b;
  }

  double get saturation {
    final highest = [r, g, b].reduce(max).toDouble();
    final lowest = [r, g, b].reduce(min).toDouble();

    if (highest == 0) return 0;

    return (highest - lowest) / highest;
  }
}

class PixelReader {
  Rgb? read(CameraImage image, int x, int y) {
    if (x < 0 ||
        y < 0 ||
        x >= image.width ||
        y >= image.height) {
      return null;
    }

    if (Platform.isIOS) {
      return readBgra(image, x, y);
    }

    return readNv21(image, x, y);
  }

  Rgb? readBgra(CameraImage image, int x, int y) {
    final plane = image.planes.first;
    final index = y * plane.bytesPerRow + x * 4;

    if (index + 2 >= plane.bytes.length) {
      return null;
    }

    return Rgb(
      plane.bytes[index + 2],
      plane.bytes[index + 1],
      plane.bytes[index],
    );
  }

  Rgb? readNv21(CameraImage image, int x, int y) {
    final plane = image.planes.first;
    final bytes = plane.bytes;
    final rowStride = plane.bytesPerRow;

    final yIndex = y * rowStride + x;
    final uvStart = rowStride * image.height;
    final uvIndex = uvStart +
        (y ~/ 2) * rowStride +
        (x ~/ 2) * 2;

    if (yIndex >= bytes.length ||
        uvIndex + 1 >= bytes.length) {
      return null;
    }

    final luminance = bytes[yIndex].toDouble();
    final v = bytes[uvIndex].toDouble() - 128;
    final u = bytes[uvIndex + 1].toDouble() - 128;

    return Rgb(
      (luminance + 1.402 * v).round().clamp(0, 255),
      (luminance - 0.344136 * u - 0.714136 * v)
          .round()
          .clamp(0, 255),
      (luminance + 1.772 * u).round().clamp(0, 255),
    );
  }
}

class VisualAnalyzer {
  final PixelReader reader = PixelReader();

  SkinMetrics? analyze({
    required CameraImage image,
    required BodyRegion region,
    required ui.Rect roi,
    required List<ui.Rect> exclusions,
    required double detectionConfidence,
  }) {
    final step = max(
      4,
      (min(roi.width, roi.height) / 34).round(),
    );

    final grid = <List<Rgb?>>[];

    int count = 0;
    int shine = 0;

    double luminance = 0;
    double luminanceSquared = 0;
    double redness = 0;

    for (int y = roi.top.round();
        y < roi.bottom;
        y += step) {
      final row = <Rgb?>[];

      for (int x = roi.left.round();
          x < roi.right;
          x += step) {
        final normalizedX = (x - roi.left) / roi.width;
        final normalizedY = (y - roi.top) / roi.height;

        final excluded = exclusions.any(
          (rect) => rect.contains(
            ui.Offset(normalizedX, normalizedY),
          ),
        );

        if (excluded) {
          row.add(null);
          continue;
        }

        final pixel = reader.read(image, x, y);
        row.add(pixel);

        if (pixel == null) continue;

        count++;

        luminance += pixel.luminance;
        luminanceSquared +=
            pixel.luminance * pixel.luminance;

        redness += max(
          0,
          pixel.r - (pixel.g + pixel.b) / 2,
        );

        if (pixel.luminance > 205 &&
            pixel.saturation < 0.18) {
          shine++;
        }
      }

      grid.add(row);
    }

    if (count < 80) return null;

    final mean = luminance / count;

    final standardDeviation = sqrt(
      max(
        0,
        luminanceSquared / count - mean * mean,
      ),
    );

    double gradient = 0;
    int edges = 0;
    int pairs = 0;

    for (int y = 0; y < grid.length; y++) {
      for (int x = 0; x < grid[y].length; x++) {
        final current = grid[y][x];

        if (current == null) continue;

        if (x + 1 < grid[y].length &&
            grid[y][x + 1] != null) {
          final difference = (
            current.luminance -
            grid[y][x + 1]!.luminance
          ).abs();

          gradient += difference;
          pairs++;

          if (difference > 28) {
            edges++;
          }
        }
      }
    }

    if (pairs == 0) return null;

    final brightnessQuality = (
      1 - (mean - 135).abs() / 95
    ).clamp(0.0, 1.0);

    final contrastQuality = (
      1 - (standardDeviation - 35).abs() / 32
    ).clamp(0.0, 1.0);

    final quality = (
      100 *
      (
        0.65 * brightnessQuality +
        0.35 * contrastQuality
      )
    ).clamp(0.0, 100.0);

    if (quality < 42) return null;

    final texture = (
      gradient / pairs * 3
    ).clamp(0.0, 100.0);

    final oiliness = (
      shine / count * 750
    ).clamp(0.0, 100.0);

    final toneUniformity = (
      100 - standardDeviation * 1.75
    ).clamp(0.0, 100.0);

    final visibleDryness = (
      0.55 * texture +
      0.25 * (100 - oiliness) +
      0.20 * (100 - toneUniformity)
    ).clamp(0.0, 100.0);

    return SkinMetrics(
      visibleDryness: visibleDryness,
      redness: (
        redness / count * 2.6
      ).clamp(0.0, 100.0),
      toneUniformity: toneUniformity,
      texture: texture,
      fineLines: region == BodyRegion.face
          ? (
              edges / pairs * 210
            ).clamp(0.0, 100.0)
          : 0,
      oiliness: region.concerns.contains('oiliness')
          ? oiliness
          : 0,
      quality: quality,
      confidence: (
        quality * detectionConfidence
      ).clamp(0.0, 100.0),
    );
  }
}

class ResultScreen extends StatefulWidget {
  const ResultScreen({
    required this.region,
    required this.metrics,
    super.key,
  });

  final BodyRegion region;
  final SkinMetrics metrics;

  @override
  State<ResultScreen> createState() => _ResultScreenState();
}

class _ResultScreenState extends State<ResultScreen> {
  bool saved = false;

  String title(String key) => switch (key) {
        'visible_dryness' => 'الجفاف الظاهر',
        'redness' => 'الاحمرار المرئي',
        'tone_uniformity' => 'تجانس اللون',
        'texture' => 'عدم تجانس الملمس',
        'fine_lines' => 'الخطوط الدقيقة الظاهرة',
        'oiliness' => 'الدهون واللمعان الظاهر',
        _ => key,
      };

  Future<void> save() async {
    await ScanStore.save(
      widget.region,
      widget.metrics,
    );

    if (mounted) {
      setState(() => saved = true);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('النتيجة')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          Text(
            widget.region.label,
            style: Theme.of(context).textTheme.headlineSmall,
          ),
          const Text(
            'مؤشرات تجميلية مرئية وليست تشخيصًا طبيًا.',
          ),
          const SizedBox(height: 12),
          MetricCard(
            title: 'جودة الالتقاط',
            value: widget.metrics.quality,
          ),
          const SizedBox(height: 8),
          MetricCard(
            title: 'الثقة',
            value: widget.metrics.confidence,
          ),
          const SizedBox(height: 8),
          for (final concern in widget.region.concerns) ...[
            MetricCard(
              title: title(concern),
              value: widget.metrics.value(concern),
            ),
            const SizedBox(height: 8),
          ],
          FilledButton.icon(
            onPressed: saved ? null : save,
            icon: const Icon(Icons.lock_outline),
            label: Text(
              saved
                  ? 'تم الحفظ'
                  : 'حفظ النتيجة الرقمية',
            ),
          ),
          const SizedBox(height: 8),
          OutlinedButton.icon(
            onPressed: () {
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (_) => ProductsScreen(
                    region: widget.region,
                    metrics: widget.metrics,
                  ),
                ),
              );
            },
            icon: const Icon(
              Icons.shopping_bag_outlined,
            ),
            label: const Text(
              'اعرض المنتجات الأنسب',
            ),
          ),
        ],
      ),
    );
  }
}

class ProductsScreen extends StatefulWidget {
  const ProductsScreen({
    required this.region,
    required this.metrics,
    super.key,
  });

  final BodyRegion region;
  final SkinMetrics metrics;

  @override
  State<ProductsScreen> createState() => _ProductsScreenState();
}

class _ProductsScreenState extends State<ProductsScreen> {
  bool consent = false;
  bool loading = false;

  String? error;
  List<Map<String, dynamic>> products = const [];

  Future<void> loadProducts() async {
    setState(() {
      loading = true;
      error = null;
    });

    try {
      final response = await http
          .post(
            Uri.parse(
              '$apiBase/v1/recommendations',
            ),
            headers: const {
              'Content-Type': 'application/json',
              'X-DermaView-Data-Class':
                  'numeric-indicators-only',
            },
            body: jsonEncode({
              'consent': consent,
              'body_region': widget.region.wireName,
              'metrics': widget.metrics.toJson(),
              'profile': {
                'sensitive_skin': false,
                'pregnant': false,
                'breastfeeding': false,
                'under_dermatology_treatment': false,
                'known_allergies': <String>[],
              },
              'language': 'ar',
            }),
          )
          .timeout(const Duration(seconds: 12));

      if (response.statusCode != 200) {
        throw StateError(
          '${response.statusCode}: ${response.body}',
        );
      }

      final decoded = jsonDecode(
        response.body,
      ) as Map<String, dynamic>;

      products = List<Map<String, dynamic>>.from(
        (decoded['items'] as List).map(
          (item) => Map<String, dynamic>.from(
            item as Map,
          ),
        ),
      );
    } catch (exception) {
      error = exception.toString();
    } finally {
      if (mounted) {
        setState(() => loading = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('المنتجات المناسبة'),
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          CheckboxListTile(
            value: consent,
            contentPadding: EdgeInsets.zero,
            title: const Text(
              'أوافق على إرسال المؤشرات الرقمية فقط.',
            ),
            subtitle: const Text(
              'لا تُرسل أي صورة أو هوية أو معالم وجه.',
            ),
            onChanged: (value) {
              setState(() => consent = value ?? false);
            },
          ),
          FilledButton(
            onPressed: consent && !loading
                ? loadProducts
                : null,
            child: loading
                ? const SizedBox.square(
                    dimension: 20,
                    child: CircularProgressIndicator(
                      strokeWidth: 2,
                    ),
                  )
                : const Text('ترشيح المنتجات'),
          ),
          if (error != null) ...[
            const SizedBox(height: 10),
            Text(error!),
          ],
          const SizedBox(height: 12),
          for (final product in products)
            Card(
              child: ListTile(
                title: Text(
                  product['name_ar'] as String,
                ),
                subtitle: Text(
                  '${product['company_name']}\n'
                  '${(product['reasons'] as List).join(' • ')}'
                  '${product['price_sar'] == null ? '' : '\n${product['price_sar']} ريال'}',
                ),
                trailing: Text(
                  '${(product['score'] as num).round()}%',
                ),
                isThreeLine: true,
              ),
            ),
        ],
      ),
    );
  }
}

class ScanStore {
  static const FlutterSecureStorage storage =
      FlutterSecureStorage();

  static const String key =
      'dermaview_scan_history_v1';

  static Future<List<Map<String, dynamic>>> read() async {
    final raw = await storage.read(key: key);

    if (raw == null) return [];

    return List<Map<String, dynamic>>.from(
      (jsonDecode(raw) as List).map(
        (item) => Map<String, dynamic>.from(
          item as Map,
        ),
      ),
    );
  }

  static Future<void> save(
    BodyRegion region,
    SkinMetrics metrics,
  ) async {
    final list = await read();

    list.insert(0, {
      'id': const Uuid().v7(),
      'created_at': DateTime.now().toIso8601String(),
      'region': region.wireName,
      'metrics': metrics.toJson(),
    });

    await storage.write(
      key: key,
      value: jsonEncode(list),
    );
  }

  static Future<void> deleteAll() {
    return storage.delete(key: key);
  }
}

class HistoryScreen extends StatelessWidget {
  const HistoryScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('سجل الفحوص'),
      ),
      body: FutureBuilder<List<Map<String, dynamic>>>(
        future: ScanStore.read(),
        builder: (context, snapshot) {
          if (!snapshot.hasData) {
            return const Center(
              child: CircularProgressIndicator(),
            );
          }

          final list = snapshot.data!;

          if (list.isEmpty) {
            return const Center(
              child: Text('لا توجد نتائج محفوظة.'),
            );
          }

          return ListView.builder(
            padding: const EdgeInsets.all(16),
            itemCount: list.length,
            itemBuilder: (context, index) {
              final item = list[index];

              final region = BodyRegion.values.firstWhere(
                (value) =>
                    value.wireName == item['region'],
              );

              final metrics = SkinMetrics.fromJson(
                Map<String, dynamic>.from(
                  item['metrics'] as Map,
                ),
              );

              return Card(
                child: ListTile(
                  title: Text(region.label),
                  subtitle: Text(
                    '${item['created_at']}\n'
                    'الجودة ${metrics.quality.round()}% • '
                    'الثقة ${metrics.confidence.round()}%',
                  ),
                ),
              );
            },
          );
        },
      ),
    );
  }
}

class PrivacyScreen extends StatelessWidget {
  const PrivacyScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('مركز الخصوصية'),
      ),
      body: ListView(
        padding: const EdgeInsets.all(18),
        children: [
          const ListTile(
            leading: Icon(
              Icons.photo_camera_outlined,
            ),
            title: Text('ملفات الصور المنشأة'),
            trailing: Text('0'),
          ),
          const ListTile(
            leading: Icon(
              Icons.cloud_off_outlined,
            ),
            title: Text(
              'إطارات الصور المرسلة للخادم',
            ),
            trailing: Text('0'),
          ),
          FilledButton.tonalIcon(
            onPressed: ScanStore.deleteAll,
            icon: const Icon(
              Icons.delete_forever_outlined,
            ),
            label: const Text(
              'حذف جميع النتائج الرقمية',
            ),
          ),
        ],
      ),
    );
  }
}

class MetricCard extends StatelessWidget {
  const MetricCard({
    required this.title,
    required this.value,
    super.key,
  });

  final String title;
  final double value;

  @override
  Widget build(BuildContext context) {
    final level = value < 34
        ? 'منخفض'
        : value < 67
            ? 'متوسط'
            : 'مرتفع';

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(14),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(title),
            const SizedBox(height: 8),
            LinearProgressIndicator(
              value: value / 100,
            ),
            const SizedBox(height: 6),
            Text(
              '${value.round()}/100 • $level',
            ),
          ],
        ),
      ),
    );
  }
}

class GuidePainter extends CustomPainter {
  GuidePainter({
    required this.progress,
  });

  final double progress;

  @override
  void paint(Canvas canvas, ui.Size size) {
    final paint = Paint()
      ..style = PaintingStyle.stroke
      ..strokeWidth = 3
      ..color = Colors.greenAccent;

    final rect = ui.Rect.fromCenter(
      center: size.center(ui.Offset.zero),
      width: size.width * 0.64,
      height: size.height * 0.58,
    );

    canvas.drawRRect(
      RRect.fromRectAndRadius(
        rect,
        const Radius.circular(24),
      ),
      paint,
    );

    final y = rect.top +
        rect.height * progress.clamp(0, 1);

    canvas.drawLine(
      ui.Offset(rect.left, y),
      ui.Offset(rect.right, y),
      paint,
    );
  }

  @override
  bool shouldRepaint(
    covariant GuidePainter oldDelegate,
  ) {
    return oldDelegate.progress != progress;
  }
}
