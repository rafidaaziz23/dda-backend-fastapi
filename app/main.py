from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

from app.schemas import EvaluateRequest, EvaluateResponse, TelemetryData, CycleRange
from app.dda_engine import engine
from app.research_logger import log_evaluation

app = FastAPI(
    title="Garden Rampage — DDA Engine API",
    description="Backend inferensi FCM/GMM untuk Dynamic Difficulty Adjustment.",
    version="1.2.0",
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
    return {"status": "ok", "service": "Garden Rampage DDA Engine", "version": "1.2.0"}


@app.post("/dda/evaluate", response_model=EvaluateResponse)
async def evaluate_player(request: Optional[EvaluateRequest] = None):
    try:
        if request is None:
            request = get_static_dummy_request()

        archetype, prob_dict, next_params, proc_time = engine.evaluate(
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
            processing_time_ms=proc_time,
        )

        print("\n[ DDA EVALUATION LOG ]")
        print(f"  Session      : {request.session_id}")
        print(f"  Algorithm    : {request.algorithm_mode}  |  Wave: {request.current_wave}")
        print(f"  HP Remaining : {request.telemetry.avg_hp_remaining_pct * 100:.1f}%  |  Kills: {request.telemetry.total_kills}")
        print(f"  Archetype    : {archetype}")
        print(f"  Probabilities: {prob_dict}")
        print(f"  Proc Time    : {proc_time:.2f} ms")
        print(f"  Next Params  : {next_params}")

        return EvaluateResponse(
            session_id=request.session_id,
            algorithm_used=request.algorithm_mode,
            difficulty_label=archetype,
            cluster_probabilities=prob_dict,
            next_enemy_params=next_params,
            meta={
                "processing_time_ms": round(proc_time, 2),
                "model_version": "1.2.scaler_fix",
                "evaluated_at_wave": request.current_wave,
                "cycle_range": {
                    "from_wave": request.cycle_range.from_wave,
                    "to_wave": request.cycle_range.to_wave,
                },
            },
        )

    except ValueError as ve:
        # Tangani error validasi ilmiah (mis. sum(u) ≠ 1.0)
        print(f"[VALIDATION ERROR] {ve}")
        raise HTTPException(status_code=422, detail=str(ve))

    except Exception as e:
        print(f"[ERROR] {e}")
        raise HTTPException(status_code=500, detail=str(e))