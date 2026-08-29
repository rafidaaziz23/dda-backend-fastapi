from app.dda_engine import engine
from app.schemas import TelemetryData


t = TelemetryData(
    avg_hp_remaining_pct=0.15, total_kills=5, accuracy_pct=0.2,
    dash_frequency=1.0, avg_time_per_wave_sec=55.0, damage_taken_total=120,
    near_death_events=4, hits_taken_from_strawberry=8, hits_taken_from_jambu=6,
    hits_taken_from_pisang=5, avg_enemies_alive_simultaneously=9.0
)
label, probs, params, ms = engine.evaluate("FCM", t)
print("FCM Struggling test => Label:", label)
print("  Probs:", probs)
print("  spawn_interval_mult:", params["spawn_interval_mult"], "(>1.0 = lebih mudah)")
print("  enemy_hp_mult:", params["enemy_hp_mult"], "(<1.0 = musuh lebih lemah)")
print("  Proc:", round(ms, 2), "ms")

t2 = TelemetryData(
    avg_hp_remaining_pct=0.95, total_kills=40, accuracy_pct=0.92,
    dash_frequency=12.0, avg_time_per_wave_sec=12.0, damage_taken_total=5,
    near_death_events=0, hits_taken_from_strawberry=0, hits_taken_from_jambu=0,
    hits_taken_from_pisang=0, avg_enemies_alive_simultaneously=1.5
)
label2, probs2, params2, ms2 = engine.evaluate("GMM", t2)
print("\nGMM Dominant test => Label:", label2)
print("  Probs:", probs2)
print("  spawn_interval_mult:", params2["spawn_interval_mult"], "(<1.0 = lebih cepat spawn)")
print("  enemy_hp_mult:", params2["enemy_hp_mult"], "(>1.0 = musuh lebih kuat)")
print("  Proc:", round(ms2, 2), "ms")
