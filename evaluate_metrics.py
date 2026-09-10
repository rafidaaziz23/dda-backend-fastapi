import numpy as np
from sklearn.metrics import silhouette_score, davies_bouldin_score
import skfuzzy as fuzz
from app.dda_engine import engine, FCM_M, FCM_ERROR, FCM_MAXITER, RANDOM_SEED

def evaluate_clustering_metrics(X_scaled: np.ndarray) -> dict:
    # Evaluasi Model Gaussian Mixture Models (GMM)
    gmm_labels = engine.gmm.predict(X_scaled)
    gmm_silhouette = silhouette_score(X_scaled, gmm_labels)
    gmm_dbi = davies_bouldin_score(X_scaled, gmm_labels)

    # Evaluasi Model Fuzzy C-Means (FCM)
    u, _, _, _, _, _ = fuzz.cluster.cmeans_predict(
        X_scaled.T,
        engine.cntr,
        FCM_M,
        error=FCM_ERROR,
        maxiter=FCM_MAXITER,
        seed=RANDOM_SEED,
    )
    fcm_labels = np.argmax(u, axis=0)
    fcm_silhouette = silhouette_score(X_scaled, fcm_labels)
    fcm_dbi = davies_bouldin_score(X_scaled, fcm_labels)

    return {
        "GMM": {
            "silhouette_score": round(float(gmm_silhouette), 4),
            "davies_bouldin_index": round(float(gmm_dbi), 4),
        },
        "FCM": {
            "silhouette_score": round(float(fcm_silhouette), 4),
            "davies_bouldin_index": round(float(fcm_dbi), 4),
        },
    }


if __name__ == "__main__":
    results = evaluate_clustering_metrics(engine.X_scaled)
    print("=== HASIL EVALUASI METRIK KLASTER (DATASET BASELINE) ===")
    print("GMM -> Silhouette:", results["GMM"]["silhouette_score"], "| DBI:", results["GMM"]["davies_bouldin_index"])
    print("FCM -> Silhouette:", results["FCM"]["silhouette_score"], "| DBI:", results["FCM"]["davies_bouldin_index"])
