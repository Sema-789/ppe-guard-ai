import os
import random
import cv2
from ultralytics import YOLO

model_yolu = r"runs\detect\ppe_yolov8n_baseline\weights\best.pt"
test_klasoru = r"Helmet and Vest.v1i.yolov8\test\images"
cikti_dosyasi = "sonuc_gorsel.jpg"

model = YOLO(model_yolu)


def erisim_karari_ver(gorsel_yolu, guven_esigi=0.5):
    sonuclar = model.predict(
        source=gorsel_yolu,
        conf=guven_esigi,
        imgsz=640,
        device="cpu",
        workers=0,
        verbose=False
    )

    bulunan_siniflar = set()
    kutular = []

    for box in sonuclar[0].boxes:
        cls_id = int(box.cls[0])
        sinif_adi = model.names[cls_id]
        guven = float(box.conf[0])
        x1, y1, x2, y2 = map(int, box.xyxy[0])

        bulunan_siniflar.add(sinif_adi)
        kutular.append((sinif_adi, guven, (x1, y1, x2, y2)))

    baret_var = "helmet" in bulunan_siniflar
    yelek_var = "vest" in bulunan_siniflar

    if baret_var and yelek_var:
        durum = "APPROVED"
        eksikler = []
        mesaj = "Baret ve yelek tespit edildi. Giris onaylandi."
    else:
        durum = "DENIED"
        eksikler = []
        if not baret_var:
            eksikler.append("helmet")
        if not yelek_var:
            eksikler.append("vest")
        mesaj = f"Giris reddedildi. Eksik: {', '.join(eksikler)}."

    return durum, mesaj, sorted(list(bulunan_siniflar)), eksikler, kutular


def gorseli_kaydet_ve_ac(gorsel_yolu, durum, kutular, cikti_yolu):
    img = cv2.imread(gorsel_yolu)
    for sinif_adi, guven, (x1, y1, x2, y2) in kutular:
        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 220, 120), 2)
        cv2.putText(
            img,
            f"{sinif_adi} {guven:.2f}",
            (x1, max(y1 - 8, 15)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            (0, 220, 120),
            2
        )

    # OpenCV BGR formatinda oldugu ucun APPROVED -> yesil, DENIED -> kirmizi
    renk = (0, 200, 100) if durum == "APPROVED" else (50, 50, 220)
    cv2.rectangle(img, (10, 10), (260, 46), renk, -1)
    cv2.putText(img, durum, (20, 36), cv2.FONT_HERSHEY_SIMPLEX, 0.85, (255, 255, 255), 2)

    cv2.imwrite(cikti_yolu, img)
    os.startfile(cikti_yolu)


if __name__ == "__main__":
    gorsel_listesi = [
        f for f in os.listdir(test_klasoru)
        if f.lower().endswith((".png", ".jpg", ".jpeg"))
    ]
    secilen_gorsel = random.choice(gorsel_listesi)
    tam_yol = os.path.join(test_klasoru, secilen_gorsel)

    durum, mesaj, bulunanlar, eksikler, kutular = erisim_karari_ver(tam_yol, guven_esigi=0.5)
    print(f"Gorsel: {secilen_gorsel}")
    print(f"Karar: {durum} | Bulunanlar: {bulunanlar} | Eksikler: {eksikler}")
    print(f"Aciklama: {mesaj}")

    gorseli_kaydet_ve_ac(tam_yol, durum, kutular, cikti_dosyasi)