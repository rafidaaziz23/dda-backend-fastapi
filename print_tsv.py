import json

files = [
    ('DDA OFF', 'prototype/garden-rampage/dataset/telemetry_session_2026-09-11_00-00-48.json'),
    ('FCM DDA', 'prototype/garden-rampage/dataset/telemetry_session_2026-09-11_00-10-46.json'),
    ('GMM DDA', 'prototype/garden-rampage/dataset/telemetry_session_2026-09-11_00-21-28.json')
]

keys = [
    'avg_hp_remaining_pct', 'total_kills', 'accuracy_pct', 'dash_frequency',
    'avg_time_per_wave_sec', 'damage_taken_total', 'near_death_events',
    'hits_taken_from_strawberry', 'hits_taken_from_jambu', 'avg_enemies_alive_simultaneously'
]

print("No\tSkenario\tWave\t1\t2\t3\t4\t5\t6\t7\t8\t9\t10")
row_num = 1
for label, path in files:
    with open(path) as f:
        data = json.load(f)
    for d in data:
        w = d['wave']
        vals = [
            f"{d['avg_hp_remaining_pct']:.2f}",
            str(d['total_kills']),
            f"{d['accuracy_pct']:.2f}",
            f"{d['dash_frequency']:.2f}",
            f"{d['avg_time_per_wave_sec']:.2f}",
            str(d['damage_taken_total']),
            str(d['near_death_events']),
            str(d['hits_taken_from_strawberry']),
            str(d['hits_taken_from_jambu']),
            f"{d['avg_enemies_alive_simultaneously']:.2f}"
        ]
        print(f"{row_num}\t{label}\tWave {w}\t" + "\t".join(vals))
        row_num += 1
