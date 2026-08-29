from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

from app.schemas import EvaluateRequest, EvaluateResponse, TelemetryData, CycleRange
from app.dda_engine import engine
from app.research_logger import log_evaluation

app = FastAPI(
    title="Garden Rampage — DDA Engine API",
    description=(
        "Backend inferensi FCM/GMM untuk Dynamic Difficulty Adjustment.\n\n"
        "**Sistem DDA dua lapis:**\n"
        "1. **Probabilistic Blending** — weighted average parameter berdasarkan "
        "probabilitas arketipe (Struggling/Balanced/Dominant) dari FCM atau GMM.\n"
        "2. **Behavior Modifier** — penyesuaian tambahan berbasis pola perilaku "
        "spesifik pemain (pola dash, sumber damage, akurasi, near-death events)."
    ),
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)


def get_static_dummy_request(mode: str = "FCM") -> EvaluateRequest:
    return EvaluateRequest(
        session_id="postman-dummy-session",
        algorithm_mode=mode,
        current_wave=3,
        cycle_range=CycleRange(from_wave=1, to_wave=3),
        telemetry=TelemetryData(
            avg_hp_remaining_pct=0.6,
            total_kills=30,
            accuracy_pct=0.7,
            dash_frequency=5.0,
            avg_time_per_wave_sec=25.0,
            damage_taken_total=30,
            near_death_events=1,
            hits_taken_from_strawberry=2,
            hits_taken_from_jambu=1,
            hits_taken_from_pisang=1,
            avg_enemies_alive_simultaneously=3.0,
        ),
        current_enemy_params={},
    )


@app.get("/")
async def root():
    return {
        "status": "ok",
        "service": "Garden Rampage DDA Engine",
        "version": "2.0.0",
        "dda_stages": [
            "Stage 1: Probabilistic Blending (FCM/GMM archetype probabilities)",
            "Stage 2: Behavior-Specific Modifier (play pattern adjustments)",
        ],
    }


@app.post("/dda/evaluate", response_model=EvaluateResponse)
async def evaluate_player(request: Optional[EvaluateRequest] = None):
    try:
        if request is None:
            request = get_static_dummy_request()

        archetype, prob_dict, next_params, proc_time, behavior_notes = engine.evaluate(
            request.algorithm_mode,
            request.telemetry,
        )

        log_evaluation(
            session_id=request.session_id,
            current_wave=request.current_wave,
            algorithm_used=request.algorithm_mode,
            telemetry=request.telemetry,
            dominant_archetype=archetype,
            prob_dict=prob_dict,
            next_params=next_params,
            behavior_notes=behavior_notes,
            processing_time_ms=proc_time,
        )

        print("\n[ DDA EVALUATION LOG ]")
        print(f"  Session      : {request.session_id}")
        print(f"  Algorithm    : {request.algorithm_mode}  |  Wave: {request.current_wave}")
        print(f"  HP Remaining : {request.telemetry.avg_hp_remaining_pct * 100:.1f}%"
              f"  |  Kills: {request.telemetry.total_kills}"
              f"  |  Accuracy: {request.telemetry.accuracy_pct * 100:.1f}%")
        print(f"  Dash Freq    : {request.telemetry.dash_frequency:.1f}"
              f"  |  Near-Death: {request.telemetry.near_death_events}x")
        print(f"  Archetype    : {archetype}  |  Probs: {prob_dict}")
        print(f"  Behavior     : {behavior_notes if behavior_notes else ['(none)']}")
        print(f"  Energy Cost  : ×{next_params['energy_cost_mult']}"
              f"  |  HP Bonus: +{next_params['player_hp_bonus']}"
              f"  |  Heal Rate: ×{next_params['heal_drop_rate_mult']}")
        print(f"  Proc Time    : {proc_time:.2f} ms")
        print(f"  Next Params  : {next_params}")

        return EvaluateResponse(
            session_id=request.session_id,
            algorithm_used=request.algorithm_mode,
            difficulty_label=archetype,
            cluster_probabilities=prob_dict,
            next_enemy_params=next_params,
            behavior_notes=behavior_notes,
            meta={
                "processing_time_ms": round(proc_time, 2),
                "model_version": "2.0.behavior_modifier",
                "evaluated_at_wave": request.current_wave,
                "cycle_range": {
                    "from_wave": request.cycle_range.from_wave,
                    "to_wave": request.cycle_range.to_wave,
                },
                "dda_stages_applied": 2,
            },
        )

    except ValueError as ve:
        print(f"[VALIDATION ERROR] {ve}")
        raise HTTPException(status_code=422, detail=str(ve))

    except Exception as e:
        print(f"[ERROR] {e}")
        raise HTTPException(status_code=500, detail=str(e))