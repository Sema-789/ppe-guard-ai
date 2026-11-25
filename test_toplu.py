import os
import pathlib
import pandas as pd
from test_erisim import model   # test_erisim.py ilə eyni qovluqda olmalıdır

dataset_dir = "Helmet and Vest.v1i.yolov8"
test_img = os.path.join(dataset_dir, "test", "images")
test_lbl = os.path.join(dataset_dir, "test", "labels")
extra_dir = "test_cases"          # helmet_only/ vest_only/ none/ alt qovluqları
THRESHOLDS = [0.3, 0.4, 0.5, 0.6, 0.7]
EXTS = (".png", ".jpg", ".jpeg")


def qrup_ve_gozlenen(h, v):
    grup = "both" if h and v else "helmet_only" if h else "vest_only" if v else "none"
    return grup, ("APPROVED" if h and v else "DENIED")


# ---- nümunələri topla: (yol, mənbə, qrup, gözlənilən) ----
samples = []

# 1) Dataset test bölməsi (qrup label fayllarından çıxarılır)
for f in os.listdir(test_img):
    if f.lower().endswith(EXTS):
        lbl = os.path.join(test_lbl, os.path.splitext(f)[0] + ".txt")
        found = set()
        if os.path.exists(lbl):
            with open(lbl) as fh:
                found = {model.names[int(float(l.split()[0]))] for l in fh if l.strip()}
        grup, exp = qrup_ve_gozlenen("helmet" in found, "vest" in found)
        samples.append((os.path.join(test_img, f), "dataset", grup, exp))

# 2) Öz şəkilləriniz (qrup qovluq adından oxunur)
if os.path.isdir(extra_dir):
    for grup in ["both", "helmet_only", "vest_only", "none"]:
        exp = "APPROVED" if grup == "both" else "DENIED"
        folder = pathlib.Path(extra_dir, grup)
        if not folder.is_dir():
            continue
        for p in folder.iterdir():
            if p.suffix.lower() in EXTS:
                samples.append((str(p), "oz_sekiller", grup, exp))
else:
    print(f"DİQQƏT: '{extra_dir}' qovluğu tapılmadı. Skriptlə eyni yerdə olmalıdır.")

# ---- hər şəkil üçün modeli BİR dəfə işlət (aşağı conf ilə), sonra hədləri süz ----
raw = {}
unreadable = []
for path, *_ in samples:
    try:
        r = model.predict(source=path, conf=0.1, imgsz=640, device="cpu",
                          workers=0, verbose=False)[0]
        raw[path] = [(model.names[int(b.cls[0])], float(b.conf[0])) for b in r.boxes]
    except Exception as e:
        unreadable.append(path)
        print(f"OXUNMADI: {path} ({type(e).__name__})")

samples = [s for s in samples if s[0] in raw]


def karar(path, thr):
    found = {n for n, c in raw[path] if c >= thr}
    return "APPROVED" if ("helmet" in found and "vest" in found) else "DENIED"


# ---- nəticələr ----
rows = []
for thr in THRESHOLDS:
    for path, src, grup, exp in samples:
        pred = karar(path, thr)
        rows.append({"thr": thr, "file": path, "source": src,
                     "group": grup, "expected": exp, "predicted": pred,
                     "correct": pred == exp})
df = pd.DataFrame(rows)

print("\n=== Qrup sayları ===")
print(pd.DataFrame(samples, columns=["path", "source", "group", "exp"])
        .groupby(["source", "group"]).size())

print("\n=== Hədd üzrə ümumi nəticə ===")
summary = pd.DataFrame({
    "dəqiqlik": df.groupby("thr")["correct"].mean().round(3),
    "false_approve": df[(df.expected == "DENIED") & (df.predicted == "APPROVED")].groupby("thr").size(),
    "false_deny": df[(df.expected == "APPROVED") & (df.predicted == "DENIED")].groupby("thr").size(),
}).fillna(0).astype({"false_approve": int, "false_deny": int})
print(summary)

print("\n=== conf=0.5: qrup üzrə dəqiqlik ===")
d05 = df[df.thr == 0.5]
print(d05.groupby(["source", "group"])["correct"].agg(["mean", "count"]).round(3))
print("\n", pd.crosstab(d05["expected"], d05["predicted"]))

# hər şəkil üçün aşkarlanan siniflər və etibar dəyərləri (xəta analizi üçün)
d05 = d05.copy()
d05["detections"] = d05["file"].map(
    lambda p: "; ".join(f"{n}:{c:.2f}" for n, c in raw[p]) or "heç nə"
)
d05[~d05["correct"]].to_csv("errors.csv", index=False, encoding="utf-8-sig")

print("\n=== Səhv edilən şəkillər (conf=0.5) ===")
errs = d05[~d05["correct"]]
if errs.empty:
    print("Səhv yoxdur.")
else:
    print(errs[["file", "group", "expected", "predicted", "detections"]].to_string(index=False))
print("\nSəhvlər errors.csv faylına yazıldı.")