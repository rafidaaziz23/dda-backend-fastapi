import json
import os

BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_DIR = os.path.join(BACKEND_DIR, "..", "garden-rampage", "dataset")

FILE_DDA_OFF = os.path.join(DATASET_DIR, "telemetry_session_2026-08-30_16-27-49.json")
FILE_FCM     = os.path.join(DATASET_DIR, "telemetry_session_2026-08-30_16-36-48.json")
FILE_GMM     = os.path.join(DATASET_DIR, "telemetry_session_2026-08-30_16-43-00.json")

with open(FILE_DDA_OFF, "r") as f:
    data_off = json.load(f)
with open(FILE_FCM, "r") as f:
    data_fcm = json.load(f)
with open(FILE_GMM, "r") as f:
    data_gmm = json.load(f)

lines = []
lines.append("# LAMPIRAN DOKUMEN TUGAS AKHIR")
lines.append("")
lines.append("## Lampiran 1: Tabel Master Data Telemetri Pengujian 32 Gelombang Pertempuran")
lines.append("")
lines.append("Tabel di bawah ini memuat data telemetri lengkap hasil pencatatan skrip TelemetryTracker.gd dari tiga skenario pengujian (DDA OFF, FCM, dan GMM) dengan identitas sesi Session ID: 970962.")
lines.append("")
lines.append("| Skenario | Gelombang | Sisa HP (%) | Kills | Akurasi (%) | Dash (/menit) | Durasi (detik) | Kerusakan | Hit Straw | Hit Jam | Kepadatan Musuh |")
lines.append("|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|")

def append_scenario(data, label):
    for d in data:
        hp = f"{d['avg_hp_remaining_pct'] * 100:.1f}%"
        acc = f"{d['accuracy_pct'] * 100:.1f}%"
        dash = f"{d['dash_frequency']:.1f}"
        dur = f"{d['avg_time_per_wave_sec']:.1f}"
        lines.append(f"| {label} | Wave {d['wave']} | {hp} | {d['total_kills']} | {acc} | {dash} | {dur} | {d['damage_taken_total']} | {d['hits_taken_from_strawberry']} | {d['hits_taken_from_jambu']} | {d['avg_enemies_alive_simultaneously']:.1f} |")

append_scenario(data_off, "DDA OFF")
append_scenario(data_fcm, "FCM")
append_scenario(data_gmm, "GMM")

lines.append("")
lines.append("---")
lines.append("")
lines.append("## Lampiran 2: Struktur Skema Data REST API (schemas.py)")
lines.append("")
lines.append("Berikut adalah skema data validasi permintaan dan respon berbasis Pydantic yang diterapkan pada peladen FastAPI (prototype/dda-backend/app/schemas.py):")
lines.append("")
lines.append("```python")
schemas_path = os.path.join(BACKEND_DIR, "app", "schemas.py")
with open(schemas_path, "r") as f:
    lines.append(f.read().strip())
lines.append("```")
lines.append("")
lines.append("---")
lines.append("")
lines.append("## Lampiran 3: Spesifikasi Lingkungan Pengujian Klien dan Peladen")
lines.append("")
lines.append("1. Spesifikasi Perangkat Keras Pengujian:")
lines.append("- Prosesor: Intel Core i5 / AMD Ryzen setara multi-core")
lines.append("- Memori Utama (RAM): 16 GB DDR4")
lines.append("- Penyimpanan: Solid State Drive (SSD) NVMe")
lines.append("- Kartu Grafis: Dedicated GPU dengan dukungan Vulkan dan OpenGL 3.3+")
lines.append("- Sistem Operasi: Microsoft Windows 11 64-bit")
lines.append("")
lines.append("2. Spesifikasi Perangkat Lunak Sisi Klien:")
lines.append("- Game Engine: Godot Engine versi 4.7 Standard")
lines.append("- Bahasa Pemrograman Klien: GDScript 2.0")
lines.append("- Protokol Jaringan: HTTPRequest Node (Godot Built-in) dengan format payload JSON")
lines.append("- Resolusi Permainan: 1280 x 720 piksel pada target 60 Frames Per Second (FPS)")
lines.append("")
lines.append("3. Spesifikasi Perangkat Lunak Sisi Peladen:")
lines.append("- Lingkungan Eksekusi: Python 3.11 64-bit Virtual Environment")
lines.append("- Kerangka Kerja Web API: FastAPI versi 0.141+ berbasis ASGI Starlette")
lines.append("- Peladen Web: Uvicorn versi 0.52+ (asynchronous worker)")
lines.append("- Pustaka Kecerdasan Buatan: scikit-fuzzy (skfuzzy 0.5.0), scikit-learn (sklearn 1.9.0), NumPy (2.4+)")
lines.append("- Model Validasi Data: Pydantic versi 2.13+")
lines.append("")

content = "\n".join(lines)

out_files = [
    os.path.join(BACKEND_DIR, "..", "..", "laporan", "LAMPIRAN_DOKUMEN_TA.md"),
    os.path.join(BACKEND_DIR, "..", "..", "LAMPIRAN_DOKUMEN_TA.md"),
]
for p in out_files:
    with open(p, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"[GENERATED] {p}")
