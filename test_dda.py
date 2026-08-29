import sys
sys.stdout.reconfigure(encoding='utf-8')
from app.dda_engine import engine

# Simulasi pemain Struggling yang jarang dash dan sering kena Strawberry
t = type('T', (), {
    'avg_hp_remaining_pct': 0.15,
    'total_kills': 8,
    'accuracy_pct': 0.22,
    'dash_frequency': 0.8,
    'avg_time_per_wave_sec': 75,
    'damage_taken_total': 95,
    'near_death_events': 4,
    'hits_taken_from_strawberry': 9,
    'hits_taken_from_jambu': 1,
    'hits_taken_from_pisang': 0,
    'avg_enemies_alive_simultaneously': 7
})()

archetype, prob, params, t_ms, notes = engine.evaluate('FCM', t)
print('=== HASIL EVALUASI ===')
print(f'Archetype  : {archetype}')
print(f'Probs      : {prob}')
print(f'Behavior   : {notes}')
print('--- Parameter Musuh ---')
print(f'  straw_fire_rate : {params["strawberry_fire_rate_mult"]}')
print(f'  spawn_comp      : {params["spawn_composition"]}')
print(f'  enemy_hp        : {params["enemy_hp_mult"]}')
print('--- Parameter Player ---')
print(f'  energy_cost     : {params["energy_cost_mult"]}')
print(f'  player_hp_bonus : {params["player_hp_bonus"]}')
print(f'  heal_drop_rate  : {params["heal_drop_rate_mult"]}')
print(f'Proc Time  : {t_ms:.2f} ms')
