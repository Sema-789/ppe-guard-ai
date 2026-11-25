# Hafta 3 Ozet - Veri + AI Baseline (PPE Guard AI)

## 1. Veri Hazirligi ve EDA
- **Veri Seti:** Roboflow `Helmet and Vest.v1i.yolov8` (168 gorsel; 283 `helmet`, 272 `vest` etiketi; `train` / `valid` / `test` bolunmesi).
- **EDA & Dogrulama:** `eda.ipynb` icerisinde sinif dagilimi, etiket formati ve dosya tutarliligi dogrulandi; harici test senaryolarindaki bozuk 4 gorsel temizlendi.

## 2. Ilk AI Prototipi (Baseline)
- **Model:** YOLOv8n (`runs/detect/ppe_yolov8n_baseline/weights/best.pt`), `imgsz=640`, `25 epoch`, CPU.
- **Karar Mantigi:** `test_erisim.py` ve `test_toplu.py` ile `helmet` + `vest` zorunluluguna gore `APPROVED` / `DENIED` erisim karari ve `errors.csv` hata kaydi olusturuldu.

## 3. Ilk Metriklerin Oneri Formundaki Nicel Hedeflerle Karsilastirilmasi

| Oneri Formu Nicel Hedefi | Hedef Deger | Baseline Olcumu | Durum & Degerlendirme |
| :--- | :--- | :--- | :--- |
| **1. Test kumesi mAP@0.5** | `>= 0.80` | **0.995** (`helmet`: 0.995, `vest`: 0.995; `Precision`: 0.988, `Recall`: 1.000) | **Karsilandi** (Ayrilmis test setinde hedefin uzerinde) |
| **2. Uctan uca yanit suresi** | `< 1000 ms` (1 sn) | **~87.3 ms** (`5.4 ms` preprocess + `81.0 ms` inference + `0.9 ms` postprocess) | **Karsilandi** (Model cikarim suresi 1 sn sinirinin cok altinda; arayuz gecikmesi Hafta 5-6'da olculecek) |
| **3. Farkli senaryolarda karar basarisi** | `>= %95` | Duzgun testlerde calisiyor; harici `oz_sekiller` setinde (`conf=0.50`) **11 yanlis pozitif** (`errors.csv`) | **Gelistirilecek** (Ekipmansiz kiyafetlerde false positive var; negatif ornek ekleme ve fine-tuning ile iyilestirilecek) |

## Sonraki Adimlar
- Negatif (bos etiketli) gorseller ekleyerek ve `conf` esigini optimize ederek false positive oranini dusurmek.
- Hafta 4'te Backend iskeletini ve veritabani/kimlik dogrulama yapisini kurmak.