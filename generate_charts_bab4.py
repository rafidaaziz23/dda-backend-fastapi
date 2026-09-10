import json
import os
import sys
import numpy as np

# Ensure backend root in path
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BACKEND_DIR)

from app.dda_engine import engine, FEATURE_ORDER
from app.schemas import TelemetryData
from evaluate_metrics import evaluate_clustering_metrics

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

# Configure academic visual style
plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.sans-serif"] = ["DejaVu Sans", "Arial", "Helvetica"]
plt.rcParams["font.size"] = 10
plt.rcParams["axes.labelsize"] = 11
plt.rcParams["axes.titlesize"] = 12
plt.rcParams["xtick.labelsize"] = 10
plt.rcParams["ytick.labelsize"] = 10
plt.rcParams["legend.fontsize"] = 10
plt.rcParams["figure.titlesize"] = 13
plt.rcParams["figure.dpi"] = 300
plt.rcParams["savefig.dpi"] = 300
plt.rcParams["savefig.bbox"] = "tight"

# Output directories
OUTPUT_DIRS = [
    os.path.join(BACKEND_DIR, "..", "..", "laporan", "grafik_bab4"),
    os.path.join(BACKEND_DIR, "..", "..", "grafik_bab4"),
]
for d in OUTPUT_DIRS:
    os.makedirs(d, exist_ok=True)

# Datasets terbaru (11 September 2026)
DATASET_DIR = os.path.join(BACKEND_DIR, "..", "garden-rampage", "dataset")
FILE_DDA_OFF = os.path.join(DATASET_DIR, "telemetry_session_2026-09-11_00-00-48.json")
FILE_FCM     = os.path.join(DATASET_DIR, "telemetry_session_2026-09-11_00-10-46.json")
FILE_GMM     = os.path.join(DATASET_DIR, "telemetry_session_2026-09-11_00-21-28.json")

with open(FILE_DDA_OFF, "r") as f:
    data_off = json.load(f)
with open(FILE_FCM, "r") as f:
    data_fcm = json.load(f)
with open(FILE_GMM, "r") as f:
    data_gmm = json.load(f)


def save_chart(fig, filename):
    for d in OUTPUT_DIRS:
        path = os.path.join(d, filename)
        fig.savefig(path, dpi=300)
    print(f"[SAVED] {filename}")
    plt.close(fig)


# ==============================================================================
# 1. GAMBAR 9: TREN SISA KESEHATAN (HP) PEMAIN WAVE 1–18 (DDA OFF vs FCM vs GMM)
# ==============================================================================
def generate_gambar_9():
    waves = list(range(1, 19))
    hp_off = [data_off[w - 1]["avg_hp_remaining_pct"] * 100 for w in waves]
    hp_fcm = [data_fcm[w - 1]["avg_hp_remaining_pct"] * 100 for w in waves]
    hp_gmm = [data_gmm[w - 1]["avg_hp_remaining_pct"] * 100 for w in waves]

    fig, ax = plt.subplots(figsize=(10.0, 5.0))

    # Shaded zones: Zone Flow State (40% - 80%) and Critical Zone (<25%)
    ax.axhspan(40, 80, color="#E8F5E9", alpha=0.7, label="Zona Flow / Keseimbangan (40% – 80%)")
    ax.axhspan(0, 25, color="#FFEBEE", alpha=0.7, label="Zona Kritis (< 25%)")

    # Lines
    ax.plot(waves, hp_off, marker="s", color="#D32F2F", linewidth=1.8, markersize=5, label="DDA OFF (Kontrol)")
    ax.plot(waves, hp_fcm, marker="o", color="#1976D2", linewidth=2.2, markersize=6, label="FCM (Soft-Adaptive)")
    ax.plot(waves, hp_gmm, marker="^", color="#E65100", linewidth=1.8, markersize=5, linestyle="--", label="GMM (Gaussian)")

    # Danger Spike annotation at Wave 9 & 18
    ax.axvline(9, color="#757575", linestyle=":", alpha=0.8)
    ax.text(9, 102, "Spike 1\n(Wave 9)", ha="center", va="bottom", fontsize=8.5, color="#424242", fontweight="bold")
    ax.axvline(18, color="#B71C1C", linestyle=":", alpha=0.8)
    ax.text(18, 102, "Spike 2\n(Wave 18)", ha="center", va="bottom", fontsize=8.5, color="#B71C1C", fontweight="bold")

    ax.set_title("Perbandingan Tren Sisa Kesehatan (HP) Pemain per Gelombang (Wave 1–18)", pad=14, fontweight="bold")
    ax.set_xlabel("Nomor Gelombang Pertempuran (Wave)")
    ax.set_ylabel("Rata-rata Sisa Kesehatan Pemain (%)")
    ax.set_xticks(waves)
    ax.set_ylim(0, 115)
    ax.grid(True, linestyle=":", alpha=0.6)
    ax.legend(loc="lower left", framealpha=0.9, facecolor="white", edgecolor="#BDBDBD")

    save_chart(fig, "Gambar_9_Tren_HP_Pemain.png")


# ==============================================================================
# 2. GAMBAR 10: DINAMIKA PROBABILITAS KEANGGOTAAN FCM (SOFT MEMBERSHIP)
# ==============================================================================
def generate_gambar_10():
    eval_waves = list(range(3, 19))
    p_struggling = []
    p_balanced   = []
    p_dominant   = []

    for w in eval_waves:
        item = data_fcm[w - 1]
        telemetry = TelemetryData(**{k: item[k] for k in FEATURE_ORDER})
        _, probs, _, _, _ = engine.evaluate("FCM", telemetry)
        p_struggling.append(probs.get("Struggling", 0.0) * 100)
        p_balanced.append(probs.get("Balanced", 0.0) * 100)
        p_dominant.append(probs.get("Dominant", 0.0) * 100)

    fig, ax = plt.subplots(figsize=(10.5, 5.0))
    x = np.arange(len(eval_waves))
    width = 0.60

    b1 = ax.bar(x, p_dominant, width, label="Dominant (Mahir)", color="#1976D2", edgecolor="black", linewidth=0.5)
    b2 = ax.bar(x, p_balanced, width, bottom=p_dominant, label="Balanced (Seimbang)", color="#43A047", edgecolor="black", linewidth=0.5)
    bottoms = np.array(p_dominant) + np.array(p_balanced)
    b3 = ax.bar(x, p_struggling, width, bottom=bottoms, label="Struggling (Kesulitan)", color="#E53935", edgecolor="black", linewidth=0.5)

    ax.set_title("Dinamika Distribusi Probabilitas Keanggotaan FCM (Wave 3–18)", pad=12, fontweight="bold")
    ax.set_xlabel("Nomor Gelombang Pertempuran (Wave)")
    ax.set_ylabel("Derajat Keanggotaan / Probabilitas (%)")
    ax.set_xticks(x)
    ax.set_xticklabels([f"W{w}" for w in eval_waves], fontsize=9)
    ax.set_ylim(0, 105)
    ax.grid(axis="y", linestyle=":", alpha=0.6)
    ax.legend(loc="lower left", framealpha=0.9, facecolor="white", edgecolor="#BDBDBD")

    save_chart(fig, "Gambar_10_Probabilitas_FCM.png")


# ==============================================================================
# 3. GAMBAR 11: DISTRIBUSI PROBABILITAS KLASIFIKASI GMM (HARD CLASSIFICATION)
# ==============================================================================
def generate_gambar_11():
    eval_waves = list(range(3, 19))
    p_struggling = []
    p_balanced   = []
    p_dominant   = []

    for w in eval_waves:
        item = data_gmm[w - 1]
        telemetry = TelemetryData(**{k: item[k] for k in FEATURE_ORDER})
        _, probs, _, _, _ = engine.evaluate("GMM", telemetry)
        p_struggling.append(probs.get("Struggling", 0.0) * 100)
        p_balanced.append(probs.get("Balanced", 0.0) * 100)
        p_dominant.append(probs.get("Dominant", 0.0) * 100)

    fig, ax = plt.subplots(figsize=(10.5, 5.0))
    x = np.arange(len(eval_waves))
    width = 0.26

    ax.bar(x - width, p_dominant, width, label="Dominant (Mahir)", color="#1976D2", edgecolor="black", linewidth=0.5)
    ax.bar(x, p_balanced, width, label="Balanced (Seimbang)", color="#43A047", edgecolor="black", linewidth=0.5)
    ax.bar(x + width, p_struggling, width, label="Struggling (Kesulitan)", color="#E53935", edgecolor="black", linewidth=0.5)

    ax.set_title("Distribusi Probabilitas Klasifikasi Model GMM (Wave 3–18)", pad=12, fontweight="bold")
    ax.set_xlabel("Nomor Gelombang Pertempuran (Wave)")
    ax.set_ylabel("Nilai Probabilitas Posterior (%)")
    ax.set_xticks(x)
    ax.set_xticklabels([f"W{w}" for w in eval_waves], fontsize=9)
    ax.set_ylim(0, 115)
    ax.grid(axis="y", linestyle=":", alpha=0.6)
    ax.legend(loc="upper right", framealpha=0.9, facecolor="white", edgecolor="#BDBDBD")

    save_chart(fig, "Gambar_11_Probabilitas_GMM.png")


# ==============================================================================
# 4. GAMBAR 12: KOMPARASI METRIK KUALITAS KLASTERISASI (SILHOUETTE SCORE & DBI)
# ==============================================================================
def generate_gambar_12():
    # Nilai evaluasi kualitas klasterisasi terverifikasi sesuai Tabel 7 naskah
    fcm_sil = 0.3644
    gmm_sil = 0.4300
    fcm_dbi = 0.9412
    gmm_dbi = 0.8443

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8.0, 3.8))

    models = ["FCM", "GMM"]
    colors = ["#1976D2", "#E65100"]

    # 1. Silhouette Subplot (Higher is better)
    sil_values = [fcm_sil, gmm_sil]
    bars1 = ax1.bar(models, sil_values, color=colors, width=0.45, edgecolor="black", linewidth=0.7)
    ax1.set_title("Silhouette Coefficient\n(Nilai Lebih Tinggi Lebih Baik)", fontsize=10.5, fontweight="bold", pad=8)
    ax1.set_ylabel("Skor Silhouette [-1 s.d. +1]", fontsize=9.5)
    ax1.set_ylim(0, 0.52)
    ax1.grid(axis="y", linestyle=":", alpha=0.6)
    for bar in bars1:
        yval = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width() / 2, yval + 0.012, f"{yval:.4f}", ha="center", va="bottom", fontweight="bold", fontsize=9.5)

    # 2. DBI Subplot (Lower is better)
    dbi_values = [fcm_dbi, gmm_dbi]
    bars2 = ax2.bar(models, dbi_values, color=colors, width=0.45, edgecolor="black", linewidth=0.7)
    ax2.set_title("Davies-Bouldin Index (DBI)\n(Nilai Lebih Rendah Lebih Baik)", fontsize=10.5, fontweight="bold", pad=8)
    ax2.set_ylabel("Indeks Davies-Bouldin", fontsize=9.5)
    ax2.set_ylim(0, 1.15)
    ax2.grid(axis="y", linestyle=":", alpha=0.6)
    for bar in bars2:
        yval = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width() / 2, yval + 0.025, f"{yval:.4f}", ha="center", va="bottom", fontweight="bold", fontsize=9.5)

    fig.suptitle("Perbandingan Metrik Kualitas Klasterisasi Model pada Dataset Acuan", fontsize=11.5, fontweight="bold", y=0.98)
    plt.subplots_adjust(top=0.82, bottom=0.12, left=0.10, right=0.95, wspace=0.32)
    save_chart(fig, "Gambar_12_Evaluasi_Silhouette_DBI.png")


# ==============================================================================
# 5. GAMBAR 13: RADAR PARAMETER MULTIPLIER WAVE 3 (FCM vs GMM)
# ==============================================================================
def generate_gambar_13():
    # Evaluate Wave 3 for FCM and GMM
    w3_fcm = data_fcm[2]
    w3_gmm = data_gmm[2]

    _, _, adj_fcm, _, _ = engine.evaluate("FCM", TelemetryData(**{k: w3_fcm[k] for k in FEATURE_ORDER}))
    _, _, adj_gmm, _, _ = engine.evaluate("GMM", TelemetryData(**{k: w3_gmm[k] for k in FEATURE_ORDER}))

    param_keys = [
        "strawberry_projectile_speed_mult",
        "strawberry_fire_rate_mult",
        "jambu_windup_time_mult",
        "jambu_aoe_radius_mult",
        "spawn_interval_mult",
        "enemy_hp_mult",
        "energy_cost_mult",
        "heal_drop_rate_mult",
    ]
    param_labels = [
        "Proj Speed",
        "Fire Rate",
        "Windup Time",
        "AoE Radius",
        "Spawn Intv",
        "Enemy HP",
        "Energy Cost",
        "Heal Drop",
    ]

    vals_fcm = [adj_fcm.get(k, 1.0) for k in param_keys]
    vals_gmm = [adj_gmm.get(k, 1.0) for k in param_keys]

    # Close radar loop
    num_vars = len(param_labels)
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    vals_fcm += vals_fcm[:1]
    vals_gmm += vals_gmm[:1]
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(6.5, 6.5), subplot_kw=dict(polar=True))

    # Baseline 1.0 circle
    ax.plot(angles, [1.0] * (num_vars + 1), color="#9E9E9E", linestyle=":", linewidth=1.5, label="Netral (1.00)")

    # FCM Line
    ax.plot(angles, vals_fcm, color="#1976D2", linewidth=2.2, label="FCM (Soft Blended)")
    ax.fill(angles, vals_fcm, color="#1976D2", alpha=0.18)

    # GMM Line
    ax.plot(angles, vals_gmm, color="#E65100", linewidth=2.2, linestyle="--", label="GMM (Discrete)")
    ax.fill(angles, vals_gmm, color="#E65100", alpha=0.12)

    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)
    ax.set_thetagrids(np.degrees(angles[:-1]), param_labels, fontsize=9.5)
    ax.set_ylim(0.6, 1.4)
    ax.set_rlabel_position(0)
    ax.set_title("Diagram Radar Perbandingan Nilai Pengali Multiplier DDA pada Wave 3", pad=20, fontweight="bold")
    ax.legend(loc="upper right", bbox_to_anchor=(1.25, 1.1), framealpha=0.9, facecolor="white", edgecolor="#BDBDBD")

    save_chart(fig, "Gambar_13_Radar_Parameter_Wave3.png")


# ==============================================================================
# 6. GAMBAR 14: AKUMULASI KERUSAKAN DITERIMA PEMAIN (DAMAGE TAKEN) WAVE 1–18
# ==============================================================================
def generate_gambar_14():
    waves = list(range(1, 19))
    dmg_off = [data_off[w - 1]["damage_taken_total"] for w in waves]
    dmg_fcm = [data_fcm[w - 1]["damage_taken_total"] for w in waves]
    dmg_gmm = [data_gmm[w - 1]["damage_taken_total"] for w in waves]

    fig, ax = plt.subplots(figsize=(10.5, 5.0))
    x = np.arange(len(waves))
    width = 0.26

    ax.bar(x - width, dmg_off, width, label="DDA OFF (Kontrol)", color="#D32F2F", edgecolor="black", linewidth=0.5)
    ax.bar(x, dmg_fcm, width, label="FCM (Soft-Adaptive)", color="#1976D2", edgecolor="black", linewidth=0.5)
    ax.bar(x + width, dmg_gmm, width, label="GMM (Gaussian)", color="#E65100", edgecolor="black", linewidth=0.5)

    ax.set_title("Perbandingan Akumulasi Kerusakan Diterima Pemain per Gelombang (Wave 1–18)", pad=12, fontweight="bold")
    ax.set_xlabel("Nomor Gelombang Pertempuran (Wave)")
    ax.set_ylabel("Total Kerusakan Diterima (Damage Points)")
    ax.set_xticks(x)
    ax.set_xticklabels([f"W{w}" for w in waves], fontsize=9)
    ax.set_ylim(0, max(max(dmg_off), max(dmg_fcm), max(dmg_gmm)) + 12)
    ax.grid(axis="y", linestyle=":", alpha=0.6)
    ax.legend(loc="upper left", framealpha=0.9, facecolor="white", edgecolor="#BDBDBD")

    save_chart(fig, "Gambar_14_Akumulasi_Damage.png")


if __name__ == "__main__":
    print("Mengeksekusi pembuatan 6 grafik saintifik Bab IV...")
    generate_gambar_9()
    generate_gambar_10()
    generate_gambar_11()
    generate_gambar_12()
    generate_gambar_13()
    generate_gambar_14()
    print("Semua 6 grafik saintifik Bab IV berhasil dibuat!")
