# DDA Backend: Dynamic Difficulty Adjustment Engine

Backend service berbasis FastAPI yang mengimplementasikan Dynamic Difficulty Adjustment (DDA) menggunakan algoritma unsupervised learning Fuzzy C-Means (FCM) dan Gaussian Mixture Models (GMM). Sistem ini dirancang untuk menganalisis metrik telemetri performa pemain secara real-time dan mengembalikan parameter penyesuaian kesulitan game dinamis.

Proyek ini merupakan bagian dari implementasi penelitian Tugas Akhir Program Studi Informatika.

---

## Fitur Utama

- Pemrosesan Telemetri Real-Time: Menerima metrik performa wave dari client game melalui REST API asynchronous.
- Segmentasi Arketipe Pemain: Mengelompokkan pemain ke dalam 3 profil adaptif (Struggling, Balanced, Dominant) menggunakan probabilitas keanggotaan FCM dan posterior probability GMM.
- Probabilistic Parameter Blending: Menghasilkan transisi parameter tingkat kesulitan yang halus dan adaptif tanpa perubahan drastis antar wave.
- Behavior-Driven Modifiers: Penyesuaian parameter musuh dan lingkungan berdasarkan pola perilaku spesifik (frekuensi dash, akurasi tembakan, preferensi kerusakan terhadap tipe musuh).
- Benchmark & Evaluasi Metrik: Modul evaluasi internal menggunakan Silhouette Coefficient dan Davies-Bouldin Index.

---

## Struktur Direktori

```text
dda-backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # Endpoint FastAPI dan konfigurasi server
│   ├── dda_engine.py        # Core engine FCM, GMM, dan parameter blending
│   ├── schemas.py           # Validasi skema input/output Pydantic
│   └── research_logger.py   # Pencatatan log sesi evaluasi
├── evaluate_metrics.py      # Script evaluasi metrik clustering (SC dan DBI)
├── generate_charts_bab4.py  # Script visualisasi data hasil pengujian
├── test_dda.py              # Pengujian integrasi endpoint API
├── requirements.txt         # Daftar dependensi library Python
└── README.md
```

---

## Kebutuhan Sistem

- Python 3.10 atau versi yang lebih baru
- PIP package manager
- Virtual environment (direkomendasikan)

---

## Panduan Instalasi dan Menjalankan Server

1. Masuk ke direktori backend:
   ```bash
   cd prototype/dda-backend
   ```

2. Buat dan aktifkan virtual environment:
   - Windows:
     ```powershell
     python -m venv venv
     .\venv\Scripts\activate
     ```
   - Linux / macOS:
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

3. Pasang seluruh dependensi:
   ```bash
   pip install -r requirements.txt
   ```

4. Jalankan server FastAPI menggunakan Uvicorn:
   ```bash
   uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
   ```

5. Server akan aktif di `http://127.0.0.1:8000`. Dokumentasi interaktif Swagger API dapat diakses langsung melalui peramban di `http://127.0.0.1:8000/docs`.

---

## Endpoint API Utama

### 1. Evaluasi Status Server
- Method: `GET`
- URL: `/`
- Deskripsi: Memeriksa ketersediaan layanan backend.

### 2. Evaluasi DDA Wave
- Method: `POST`
- URL: `/dda/evaluate`
- Payload (JSON):
  ```json
  {
    "session_id": "session_001",
    "algorithm_mode": "FCM",
    "current_wave": 3,
    "cycle_range": {
      "from_wave": 1,
      "to_wave": 3
    },
    "telemetry": {
      "avg_hp_remaining_pct": 0.65,
      "total_kills": 12,
      "accuracy_pct": 0.80,
      "dash_frequency": 4.5,
      "avg_time_per_wave_sec": 28.5,
      "damage_taken_total": 35,
      "near_death_events": 0,
      "hits_taken_from_strawberry": 2,
      "hits_taken_from_jambu": 1,
      "avg_enemies_alive_simultaneously": 3.2
    },
    "current_enemy_params": {}
  }
  ```
- Respon (JSON):
  Mengembalikan arketipe dominan, probabilitas arketipe, waktu pemrosesan, dan parameter musuh terkini (`strawberry_fire_rate_mult`, `jambu_windup_time_mult`, `enemy_hp_mult`, `spawn_composition`, dan parameter lainnya).

---

## Evaluasi Kinerja Model

Untuk menjalankan kalkulasi metrik clustering (*Silhouette Coefficient* dan *Davies-Bouldin Index*):
```bash
python evaluate_metrics.py
```
Hasil perhitungan metrik akan ditampilkan pada terminal untuk membandingkan karakteristik pemisahan klaster antara FCM dan GMM.
