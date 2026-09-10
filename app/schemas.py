from pydantic import BaseModel, Field
from typing import Dict, List

class CycleRange(BaseModel):
    from_wave: int
    to_wave: int

class TelemetryData(BaseModel):
    avg_hp_remaining_pct: float = Field(..., ge=0.0, le=1.0)
    total_kills: int
    accuracy_pct: float = Field(..., ge=0.0, le=1.0)
    dash_frequency: float
    avg_time_per_wave_sec: float
    damage_taken_total: int
    near_death_events: int
    hits_taken_from_strawberry: int
    hits_taken_from_jambu: int
    avg_enemies_alive_simultaneously: float

class EvaluateRequest(BaseModel):
    session_id: str
    algorithm_mode: str
    current_wave: int
    cycle_range: CycleRange
    telemetry: TelemetryData
    current_enemy_params: Dict[str, float | dict] = {}

class SpawnComposition(BaseModel):
    strawberry: float
    jambu: float

class NextEnemyParams(BaseModel):
    # ── Musuh ──────────────────────────────────────────────────────────────
    strawberry_projectile_speed_mult: float
    strawberry_fire_rate_mult: float
    jambu_windup_time_mult: float
    jambu_aoe_radius_mult: float
    # ── Spawn ──────────────────────────────────────────────────────────────
    spawn_interval_mult: float
    enemy_hp_mult: float
    spawn_composition: SpawnComposition
    # ── Player ─────────────────────────────────────────────────────────────
    energy_cost_mult: float
    player_hp_bonus: float
    heal_drop_rate_mult: float

class EvaluateResponse(BaseModel):
    session_id: str
    algorithm_used: str
    difficulty_label: str
    cluster_probabilities: Dict[str, float]
    next_enemy_params: NextEnemyParams
    behavior_notes: List[str]
    meta: dict