import csv
import os
import json
from datetime import datetime, timezone
from pathlib import Path

LOG_DIR = Path(__file__).parent.parent / "research_logs"
LOG_FILE = LOG_DIR / "dda_session_log.csv"

CSV_HEADER = [
    "timestamp_utc",
    "session_id",
    "current_wave",
    "algorithm_used",
    "raw_avg_hp_remaining_pct",
    "raw_total_kills",
    "raw_accuracy_pct",
    "raw_dash_frequency",
    "raw_avg_time_per_wave_sec",
    "raw_damage_taken_total",
    "raw_near_death_events",
    "raw_hits_taken_from_strawberry",
    "raw_hits_taken_from_jambu",
    "raw_hits_taken_from_pisang",
    "raw_avg_enemies_alive_simultaneously",
    "dominant_archetype",
    "prob_struggling",
    "prob_balanced",
    "prob_dominant",
    "out_strawberry_projectile_speed_mult",
    "out_strawberry_fire_rate_mult",
    "out_jambu_windup_time_mult",
    "out_jambu_aoe_radius_mult",
    "out_pisang_spin_speed_mult",
    "out_pisang_wander_deviation_mult",
    "out_spawn_interval_mult",
    "out_enemy_hp_mult",
    "out_spawn_comp_strawberry",
    "out_spawn_comp_jambu",
    "out_spawn_comp_pisang",
    "processing_time_ms",
    "random_seed",
    "model_version",
]

MODEL_VERSION = "1.2.scaler_fix"
RANDOM_SEED_LOGGED = 42


def _ensure_log_file():
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    if not LOG_FILE.exists():
        with open(LOG_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(CSV_HEADER)


def log_evaluation(
    session_id: str,
    current_wave: int,
    algorithm_used: str,
    telemetry,
    dominant_archetype: str,
    prob_dict: dict,
    next_params: dict,
    processing_time_ms: float,
) -> None:

    try:
        _ensure_log_file()

        spawn_comp = next_params.get("spawn_composition", {})
        row = [
            datetime.now(timezone.utc).isoformat(),
            session_id,
            current_wave,
            algorithm_used,

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

            dominant_archetype,
            prob_dict.get("Struggling", 0.0),
            prob_dict.get("Balanced", 0.0),
            prob_dict.get("Dominant", 0.0),

            next_params.get("strawberry_projectile_speed_mult"),
            next_params.get("strawberry_fire_rate_mult"),
            next_params.get("jambu_windup_time_mult"),
            next_params.get("jambu_aoe_radius_mult"),
            next_params.get("pisang_spin_speed_mult"),
            next_params.get("pisang_wander_deviation_mult"),
            next_params.get("spawn_interval_mult"),
            next_params.get("enemy_hp_mult"),
            spawn_comp.get("strawberry"),
            spawn_comp.get("jambu"),
            spawn_comp.get("pisang"),

            round(processing_time_ms, 3),
            RANDOM_SEED_LOGGED,
            MODEL_VERSION,
        ]

        with open(LOG_FILE, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(row)

    except Exception as exc:

        print(f"[ResearchLogger][ERROR] Gagal menulis log: {exc}")
