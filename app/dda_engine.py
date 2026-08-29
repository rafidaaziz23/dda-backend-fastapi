import numpy as np
import skfuzzy as fuzz
from sklearn.mixture import GaussianMixture
from sklearn.preprocessing import StandardScaler
import time

RANDOM_SEED = 42
N_CLUSTERS = 3
FCM_M = 2
FCM_ERROR = 0.005
FCM_MAXITER = 1000

FEATURE_ORDER = [
    "avg_hp_remaining_pct",
    "total_kills",
    "accuracy_pct",
    "dash_frequency",
    "avg_time_per_wave_sec",
    "damage_taken_total",
    "near_death_events",
    "hits_taken_from_strawberry",
    "hits_taken_from_jambu",
    "hits_taken_from_pisang",
    "avg_enemies_alive_simultaneously",
]


class DDAEngine:
    def __init__(self):
        self.scaler = StandardScaler()
        self._init_baseline_data()

    def _init_baseline_data(self):
        np.random.seed(RANDOM_SEED)

        struggling = np.random.normal(
            loc=[0.2, 10, 0.3, 2, 45, 100, 3, 5, 5, 5, 8], scale=0.1, size=(50, 11)
        )
        balanced = np.random.normal(
            loc=[0.5, 20, 0.6, 5, 30, 50, 1, 2, 2, 2, 5], scale=0.1, size=(50, 11)
        )
        dominant = np.random.normal(
            loc=[0.9, 35, 0.9, 10, 15, 10, 0, 0, 0, 0, 2], scale=0.1, size=(50, 11)
        )
        self.X_baseline = np.vstack([struggling, balanced, dominant])
        self.X_scaled = self.scaler.fit_transform(self.X_baseline)

        # ── GMM ──────────────────────────────────────────────────────────────
        self.gmm = GaussianMixture(n_components=N_CLUSTERS, random_state=RANDOM_SEED)
        self.gmm.fit(self.X_scaled)
        gmm_order = np.argsort(self.gmm.means_[:, 0])
        self.gmm_map = {
            gmm_order[0]: "Struggling",
            gmm_order[1]: "Balanced",
            gmm_order[2]: "Dominant",
        }

        # ── FCM ──────────────────────────────────────────────────────────────
        np.random.seed(RANDOM_SEED)
        self.cntr, _, _, _, _, _, _ = fuzz.cluster.cmeans(
            self.X_scaled.T,
            c=N_CLUSTERS,
            m=FCM_M,
            error=FCM_ERROR,
            maxiter=FCM_MAXITER,
            init=None,
            seed=RANDOM_SEED,
        )
        fcm_order = np.argsort(self.cntr[:, 0])
        self.fcm_map = {
            fcm_order[0]: "Struggling",
            fcm_order[1]: "Balanced",
            fcm_order[2]: "Dominant",
        }

        print(
            f"[DDAEngine] Inisialisasi selesai. "
            f"Baseline: {self.X_baseline.shape} | "
            f"Scaler mean: {self.scaler.mean_.round(3)}"
        )

    # ─────────────────────────────────────────────────────────────────────────
    def extract_features(self, telemetry) -> np.ndarray:
        raw = np.array([
            telemetry.avg_hp_remaining_pct,
            telemetry.total_kills,
            telemetry.accuracy_pct,
            telemetry.dash_frequency,
            telemetry.avg_time_per_wave_sec,
            telemetry.damage_taken_total,
            telemetry.near_death_events,
            telemetry.hits_taken_from_strawberry,
            telemetry.hits_taken_from_jambu,
            telemetry.hits_taken_from_pisang,
            telemetry.avg_enemies_alive_simultaneously,
        ]).reshape(1, -1)
        return self.scaler.transform(raw)

    # ─────────────────────────────────────────────────────────────────────────
    def evaluate(self, algorithm_mode: str, telemetry):
        start_time = time.time()
        X_new = self.extract_features(telemetry)
        prob_dict: dict[str, float] = {}

        if algorithm_mode.upper() == "GMM":
            probs = self.gmm.predict_proba(X_new)[0]
            for idx, p in enumerate(probs):
                prob_dict[self.gmm_map[idx]] = round(float(p), 4)
        else:
            np.random.seed(RANDOM_SEED)
            u, _, _, _, _, _ = fuzz.cluster.cmeans_predict(
                X_new.T,
                self.cntr,
                FCM_M,
                error=FCM_ERROR,
                maxiter=FCM_MAXITER,
                seed=RANDOM_SEED,
            )
            probs_fcm = u[:, 0]
            total = float(np.sum(probs_fcm))
            if abs(total - 1.0) > 0.01:
                raise ValueError(
                    f"[FCM] sum(u) = {total:.4f} ≠ 1.0 — kemungkinan bug orientasi array."
                )
            for idx, p in enumerate(probs_fcm):
                prob_dict[self.fcm_map[idx]] = round(float(p), 4)

        dominant_label = max(prob_dict, key=prob_dict.get)

        # Tahap 1: blending berbasis arketipe (FCM/GMM probabilities)
        blended = self._blend_multipliers(prob_dict)

        # Tahap 2: behavior modifier — penyesuaian berbasis pola spesifik pemain
        final_params, behavior_notes = self._apply_behavior_modifiers(blended, telemetry)

        processing_time = (time.time() - start_time) * 1000
        return dominant_label, prob_dict, final_params, processing_time, behavior_notes

    # ─────────────────────────────────────────────────────────────────────────
    def _blend_multipliers(self, probs: dict) -> dict:
        """
        Tahap 1 — Probabilistic Blending:
        Hitung weighted average parameter dari ketiga arketipe
        berdasarkan probabilitas keanggotaan pemain.
        Dua pemain dalam arketipe yang sama bisa mendapat nilai berbeda
        jika probabilitas ke arketipe lain berbeda.
        """
        bases = {
            "Struggling": {
                "strawberry_projectile_speed_mult": 0.75,
                "strawberry_fire_rate_mult":         0.75,
                "jambu_windup_time_mult":            1.25,  # lama = mudah dihindari
                "jambu_aoe_radius_mult":             0.80,
                "pisang_spin_speed_mult":            0.80,
                "pisang_wander_deviation_mult":      0.80,
                "spawn_interval_mult":               1.25,  # lambat = lebih mudah
                "enemy_hp_mult":                     0.70,
                "energy_cost_mult":                  0.80,  # energi lebih murah
                "player_hp_bonus":                   20.0,  # bonus HP awal wave
                "heal_drop_rate_mult":               1.40,  # heal item lebih sering
                "comp_straw":                        0.50,
                "comp_jam":                          0.30,
                "comp_pis":                          0.20,
            },
            "Balanced": {
                "strawberry_projectile_speed_mult": 1.00,
                "strawberry_fire_rate_mult":         1.00,
                "jambu_windup_time_mult":            1.00,
                "jambu_aoe_radius_mult":             1.00,
                "pisang_spin_speed_mult":            1.00,
                "pisang_wander_deviation_mult":      1.00,
                "spawn_interval_mult":               1.00,
                "enemy_hp_mult":                     1.00,
                "energy_cost_mult":                  1.00,
                "player_hp_bonus":                   0.0,
                "heal_drop_rate_mult":               1.00,
                "comp_straw":                        0.40,
                "comp_jam":                          0.30,
                "comp_pis":                          0.30,
            },
            "Dominant": {
                "strawberry_projectile_speed_mult": 1.25,
                "strawberry_fire_rate_mult":         1.25,
                "jambu_windup_time_mult":            0.80,  # cepat = lebih susah
                "jambu_aoe_radius_mult":             1.20,
                "pisang_spin_speed_mult":            1.20,
                "pisang_wander_deviation_mult":      1.20,
                "spawn_interval_mult":               0.80,  # cepat = lebih sulit
                "enemy_hp_mult":                     1.30,
                "energy_cost_mult":                  1.20,  # energi lebih mahal
                "player_hp_bonus":                   0.0,
                "heal_drop_rate_mult":               0.70,  # heal item lebih jarang
                "comp_straw":                        0.20,
                "comp_jam":                          0.40,
                "comp_pis":                          0.40,
            },
        }

        blended: dict[str, float] = {}
        for key in bases["Balanced"].keys():
            val = (
                probs.get("Struggling", 0.0) * bases["Struggling"][key]
                + probs.get("Balanced",   0.0) * bases["Balanced"][key]
                + probs.get("Dominant",   0.0) * bases["Dominant"][key]
            )
            # Tambahkan noise kecil untuk variasi (kecuali player_hp_bonus)
            if key != "player_hp_bonus":
                val += np.random.uniform(-0.02, 0.02)
            blended[key] = val

        return blended

    # ─────────────────────────────────────────────────────────────────────────
    def _apply_behavior_modifiers(self, blended: dict, telemetry) -> tuple[dict, list[str]]:
        """
        Tahap 2 — Behavior-Specific Modifier:

        Setelah blending arketipe, terapkan penyesuaian tambahan berdasarkan
        pola perilaku SPESIFIK pemain. Ini memungkinkan dua pemain dalam
        arketipe yang sama mendapat parameter berbeda berdasarkan gaya bermain.

        Setiap modifier bersifat ADITIF terhadap hasil blending tahap 1.
        """
        notes: list[str] = []
        m = dict(blended)  # salin untuk dimodifikasi

        # ── 1. POLA ENERGI (Dash) ─────────────────────────────────────────
        # Jika pemain sangat hemat energi (jarang dash), naikkan energy_cost
        # agar ada tantangan baru. Jika sering dash, turunkan cost.
        dash_freq = telemetry.dash_frequency
        if dash_freq < 1.5:
            # Sangat hemat: naikkan cost → dorong pemain berani menggunakan dash
            modifier = min(0.20, (1.5 - dash_freq) * 0.10)
            m["energy_cost_mult"] += modifier
            notes.append(f"low_dash({dash_freq:.1f}) -> energy_cost +{modifier:.2f}")
        elif dash_freq > 8.0:
            # Sangat agresif: kurangi cost → reward gaya bermain aktif
            modifier = min(0.15, (dash_freq - 8.0) * 0.05)
            m["energy_cost_mult"] -= modifier
            notes.append(f"high_dash({dash_freq:.1f}) → energy_cost -{modifier:.2f}")

        # ── 2. POLA SERANGAN STRAWBERRY ───────────────────────────────────
        # Jika pemain terlalu sering kena Strawberry, kurangi proporsi spawn-nya
        # dan perpanjang interval tembak (fire_rate lebih rendah).
        total_hits = max(1, telemetry.hits_taken_from_strawberry
                        + telemetry.hits_taken_from_jambu
                        + telemetry.hits_taken_from_pisang)
        straw_ratio = telemetry.hits_taken_from_strawberry / total_hits

        if straw_ratio > 0.60:
            # Strawberry dominan sebagai sumber damage → turunkan komposisinya
            reduction = min(0.12, (straw_ratio - 0.60) * 0.30)
            m["comp_straw"] -= reduction
            m["comp_jam"]   += reduction * 0.5
            m["comp_pis"]   += reduction * 0.5
            m["strawberry_fire_rate_mult"] -= min(0.10, reduction * 0.8)
            notes.append(
                f"straw_dominant({straw_ratio:.0%}) -> comp_straw -{reduction:.2f}, "
                f"fire_rate -{min(0.10, reduction*0.8):.2f}"
            )
        elif straw_ratio < 0.15 and telemetry.hits_taken_from_strawberry == 0:
            # Pemain tidak pernah kena Strawberry -> naikkan fire rate sebagai tantangan
            m["strawberry_fire_rate_mult"] += 0.08
            notes.append("straw_zero_hit -> fire_rate +0.08")

        # ── 3. POLA SERANGAN JAMBU ────────────────────────────────────────
        # Jika pemain sangat sering kena AoE Jambu, beri lebih banyak waktu
        # windup dan kurangi radius AoE agar ada waktu untuk belajar dodge.
        jambu_ratio = telemetry.hits_taken_from_jambu / total_hits
        if jambu_ratio > 0.50:
            windup_help = min(0.15, (jambu_ratio - 0.50) * 0.30)
            radius_help = min(0.10, (jambu_ratio - 0.50) * 0.20)
            m["jambu_windup_time_mult"] += windup_help
            m["jambu_aoe_radius_mult"]  -= radius_help
            notes.append(
                f"jambu_dominant({jambu_ratio:.0%}) -> windup +{windup_help:.2f}, "
                f"aoe_radius -{radius_help:.2f}"
            )
        elif jambu_ratio < 0.05 and telemetry.hits_taken_from_jambu == 0:
            # Pemain sangat mahir menghindari Jambu -> percepat windup & perbesar radius
            m["jambu_windup_time_mult"] -= 0.07
            m["jambu_aoe_radius_mult"]  += 0.07
            notes.append("jambu_zero_hit -> windup -0.07, aoe_radius +0.07")

        # ── 4. POLA AKURASI TEMBAKAN ──────────────────────────────────────
        # Akurasi sangat rendah -> kurangi kecepatan proyektil musuh sedikit
        # (bukan karena "mudah", tapi agar pemain tidak overwhelmed double penalty)
        # Akurasi sangat tinggi -> perkuat musuh
        acc = telemetry.accuracy_pct
        if acc < 0.25:
            speed_help = min(0.08, (0.25 - acc) * 0.20)
            m["strawberry_projectile_speed_mult"] -= speed_help
            notes.append(f"low_accuracy({acc:.0%}) -> proj_speed -{speed_help:.2f}")
        elif acc > 0.85:
            speed_boost = min(0.10, (acc - 0.85) * 0.40)
            m["strawberry_projectile_speed_mult"] += speed_boost
            notes.append(f"high_accuracy({acc:.0%}) -> proj_speed +{speed_boost:.2f}")

        # ── 5. POLA NEAR-DEATH ────────────────────────────────────────────
        # Banyak near-death -> bonus HP di wave berikutnya & drop rate heal naik
        # Tidak pernah near-death -> kurangi bonus HP (sudah terlalu nyaman)
        nd = telemetry.near_death_events
        if nd >= 3:
            hp_bonus = min(15.0, nd * 4.0)
            m["player_hp_bonus"]    += hp_bonus
            m["heal_drop_rate_mult"] += min(0.20, nd * 0.06)
            notes.append(f"near_death({nd}x) -> hp_bonus +{hp_bonus:.0f}, heal_drop +{min(0.20, nd*0.06):.2f}")
        elif nd == 0 and telemetry.avg_hp_remaining_pct > 0.80:
            m["player_hp_bonus"] = max(0.0, m["player_hp_bonus"] - 5.0)
            m["heal_drop_rate_mult"] -= 0.10
            notes.append("no_near_death + high_hp -> hp_bonus -5, heal_drop -0.10")

        # ── Normalisasi spawn composition ─────────────────────────────────
        comp_total = m["comp_straw"] + m["comp_jam"] + m["comp_pis"]

        def _clamp(v: float, lo: float = 0.7, hi: float = 1.4) -> float:
            return round(max(lo, min(hi, v)), 3)

        final = {
            "strawberry_projectile_speed_mult": _clamp(m["strawberry_projectile_speed_mult"]),
            "strawberry_fire_rate_mult":         _clamp(m["strawberry_fire_rate_mult"]),
            "jambu_windup_time_mult":            _clamp(m["jambu_windup_time_mult"]),
            "jambu_aoe_radius_mult":             _clamp(m["jambu_aoe_radius_mult"]),
            "pisang_spin_speed_mult":            _clamp(m["pisang_spin_speed_mult"]),
            "pisang_wander_deviation_mult":      _clamp(m["pisang_wander_deviation_mult"]),
            "spawn_interval_mult":               _clamp(m["spawn_interval_mult"]),
            "enemy_hp_mult":                     _clamp(m["enemy_hp_mult"]),
            "energy_cost_mult":                  _clamp(m["energy_cost_mult"], 0.70, 1.50),
            "player_hp_bonus":                   round(max(0.0, min(25.0, m["player_hp_bonus"])), 1),
            "heal_drop_rate_mult":               _clamp(m["heal_drop_rate_mult"], 0.50, 1.80),
            "spawn_composition": {
                "strawberry": round(m["comp_straw"] / comp_total, 3),
                "jambu":      round(m["comp_jam"]   / comp_total, 3),
                "pisang":     round(m["comp_pis"]   / comp_total, 3),
            },
        }

        return final, notes


engine = DDAEngine()