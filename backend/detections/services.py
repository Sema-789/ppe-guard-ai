from pathlib import Path
from django.conf import settings
from .models import Camera, ScanLog, Violation

try:
    from ultralytics import YOLO
except ImportError:
    YOLO = None


_MODEL_CACHE = None


def get_yolo_model():
    global _MODEL_CACHE
    if _MODEL_CACHE is not None:
        return _MODEL_CACHE
    model_path = Path(settings.YOLO_MODEL_PATH)
    if YOLO is None or not model_path.exists():
        return None
    _MODEL_CACHE = YOLO(str(model_path))
    return _MODEL_CACHE


def analyze_image_and_log(camera: Camera, image_file):
    model = get_yolo_model()

    # Əgər .pt modeli hələ qoyulmayıbsa, test üçün nəzarətli fallback nəticə qaytar
    if model is None:
        total_persons = 1
        compliant_persons = 0
        detected_violations = [
            {
                "violation_type": "no_helmet",
                "confidence": 0.85,
            }
        ]
        model_used = "fallback_mock"
    else:
        results = model(image_file, conf=settings.YOLO_CONFIDENCE_THRESHOLD)
        total_persons = 0
        compliant_persons = 0
        detected_violations = []

        for r in results:
            names = r.names or {}
            boxes = r.boxes
            if boxes is None:
                continue
            for box in boxes:
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])
                label = str(names.get(cls_id, "")).lower()

                if "person" in label:
                    total_persons += 1
                elif "no_helmet" in label or "without_helmet" in label:
                    detected_violations.append({
                        "violation_type": "no_helmet",
                        "confidence": round(conf, 4),
                    })
                elif "no_vest" in label or "without_vest" in label:
                    detected_violations.append({
                        "violation_type": "no_vest",
                        "confidence": round(conf, 4),
                    })

        compliant_persons = max(total_persons - len(detected_violations), 0)
        model_used = str(settings.YOLO_MODEL_PATH)

    is_compliant = len(detected_violations) == 0

    scan = ScanLog.objects.create(
        camera=camera,
        total_persons=total_persons,
        compliant_persons=compliant_persons,
        is_compliant=is_compliant,
    )

    created_violations = []
    for item in detected_violations:
        v = Violation.objects.create(
            scan_log=scan,
            camera=camera,
            violation_type=item["violation_type"],
            confidence=item["confidence"],
        )
        created_violations.append(v)

    return {
        "model_used": model_used,
        "scan": scan,
        "violations": created_violations,
    }