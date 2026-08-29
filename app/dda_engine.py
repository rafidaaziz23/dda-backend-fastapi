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

        self.gmm = GaussianMixture(
            n_components=N_CLUSTERS, random_state=RANDOM_SEED
        )
        self.gmm.fit(self.X_scaled)

        gmm_order = np.argsort(self.gmm.means_[:, 0])
        self.gmm_map = {
            gmm_order[0]: "Struggling",
            gmm_order[1]: "Balanced",
            gmm_order[2]: "Dominant",
        }

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

    def extract_features(self, telemetry) -> np.ndarray:

        raw = np.array(
            [
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
            ]
        ).reshape(1, -1)

        return self.scaler.transform(raw)

    def evaluate(self, algorithm_mode: str, telemetry):

        start_time = time.time()
        X_new = self.extract_features(telemetry)  # shape (1, 11), sudah discale
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
        next_params = self._blend_multipliers(prob_dict)
        processing_time = (time.time() - start_time) * 1000

        return dominant_label, prob_dict, next_params, processing_time

    def _blend_multipliers(self, probs: dict) -> dict:

        bases = {
            "Struggling": {
                "strawberry_projectile_speed_mult": 0.75,
                "strawberry_fire_rate_mult": 0.75,
                "jambu_windup_time_mult": 1.25, 
                "jambu_aoe_radius_mult": 0.8,
                "pisang_spin_speed_mult": 0.8,
                "pisang_wander_deviation_mult": 0.8,
                "spawn_interval_mult": 1.25, 
                "enemy_hp_mult": 0.7,
                "comp_straw": 0.5,
                "comp_jam": 0.3,
                "comp_pis": 0.2,
            },
            "Balanced": {
                "strawberry_projectile_speed_mult": 1.0,
                "strawberry_fire_rate_mult": 1.0,
                "jambu_windup_time_mult": 1.0,
                "jambu_aoe_radius_mult": 1.0,
                "pisang_spin_speed_mult": 1.0,
                "pisang_wander_deviation_mult": 1.0,
                "spawn_interval_mult": 1.0,
                "enemy_hp_mult": 1.0,
                "comp_straw": 0.4,
                "comp_jam": 0.3,
                "comp_pis": 0.3,
            },
            "Dominant": {
                "strawberry_projectile_speed_mult": 1.25,
                "strawberry_fire_rate_mult": 1.25,
                "jambu_windup_time_mult": 0.8, 
                "jambu_aoe_radius_mult": 1.2,
                "pisang_spin_speed_mult": 1.2,
                "pisang_wander_deviation_mult": 1.2,
                "spawn_interval_mult": 0.8,     
                "enemy_hp_mult": 1.3,
                "comp_straw": 0.2,
                "comp_jam": 0.4,
                "comp_pis": 0.4,
            },
        }

        blended: dict[str, float] = {}
        for key in bases["Balanced"].keys():
            val = (
                probs.get("Struggling", 0.0) * bases["Struggling"][key]
                + probs.get("Balanced", 0.0) * bases["Balanced"][key]
                + probs.get("Dominant", 0.0) * bases["Dominant"][key]
            )

            blended[key] = val + np.random.uniform(-0.02, 0.02)

        comp_total = blended["comp_straw"] + blended["comp_jam"] + blended["comp_pis"]

        def _clamp(v: float) -> float:
            return round(max(0.7, min(1.4, v)), 3)

        return {
            "strawberry_projectile_speed_mult": _clamp(blended["strawberry_projectile_speed_mult"]),
            "strawberry_fire_rate_mult": _clamp(blended["strawberry_fire_rate_mult"]),
            "jambu_windup_time_mult": _clamp(blended["jambu_windup_time_mult"]),
            "jambu_aoe_radius_mult": _clamp(blended["jambu_aoe_radius_mult"]),
            "pisang_spin_speed_mult": _clamp(blended["pisang_spin_speed_mult"]),
            "pisang_wander_deviation_mult": _clamp(blended["pisang_wander_deviation_mult"]),
            "spawn_interval_mult": _clamp(blended["spawn_interval_mult"]),
            "enemy_hp_mult": _clamp(blended["enemy_hp_mult"]),
            "spawn_composition": {
                "strawberry": round(blended["comp_straw"] / comp_total, 3),
                "jambu": round(blended["comp_jam"] / comp_total, 3),
                "pisang": round(blended["comp_pis"] / comp_total, 3),
            },
        }


engine = DDAEngine()