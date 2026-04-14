"""
clustering_model.py
-------------------
Funzioni per pre-processing, clustering UMAP+GMM, valutazione e
persistenza del modello per il progetto Jakala × LUISS.

Usato da:
  - src/clusters.ipynb
  - jakala_segmentation_advanced.ipynb (opzionale, il notebook è self-contained)
"""

import pickle
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.preprocessing import RobustScaler
from sklearn.mixture import GaussianMixture
from sklearn.metrics import silhouette_score, davies_bouldin_score, calinski_harabasz_score


# ── 1. Preprocessing ─────────────────────────────────────────────────────────

CLUSTERING_FEATURES_DEFAULT = [
    "recency_days", "frequency", "monetary", "avg_basket_value",
    "avg_discount_pct", "pct_items_discounted",
    "nl_open_rate", "nl_click_rate", "engagement_score",
    "return_rate",
]


def winsorize(df: pd.DataFrame, cols: list[str], quantile: float = 0.99) -> pd.DataFrame:
    """Cappa i valori al percentile indicato (default 99°) per ridurre l'impatto degli outlier."""
    df = df.copy()
    for col in cols:
        if col in df.columns:
            cap = df[col].quantile(quantile)
            df[col] = df[col].clip(upper=cap)
    return df


def scale_features(X: np.ndarray) -> tuple[np.ndarray, RobustScaler]:
    """
    Applica RobustScaler (robusto agli outlier residui post-winsorization).

    Returns
    -------
    X_scaled : np.ndarray
    scaler   : RobustScaler fittato (da salvare per transform su nuovi dati)
    """
    scaler   = RobustScaler()
    X_scaled = scaler.fit_transform(X)
    return X_scaled, scaler


def reduce_umap(X_scaled: np.ndarray,
                n_components: int = 3,
                n_neighbors: int = 30,
                min_dist: float = 0.1,
                seed: int = 42) -> tuple[np.ndarray, object]:
    """
    Riduzione dimensionale con UMAP.

    Parameters
    ----------
    n_components : 2 per visualizzazione, 3 per clustering (default)

    Returns
    -------
    X_umap  : np.ndarray di shape (n_samples, n_components)
    reducer : UMAP fittato (da salvare per transform su nuovi dati)
    """
    try:
        from umap import UMAP
    except ImportError:
        raise ImportError("Installa umap-learn: pip install umap-learn")

    reducer = UMAP(
        n_neighbors  = n_neighbors,
        min_dist     = min_dist,
        n_components = n_components,
        metric       = "euclidean",
        random_state = seed,
    )
    X_umap = reducer.fit_transform(X_scaled)
    return X_umap, reducer


# ── 2. Clustering ─────────────────────────────────────────────────────────────

def select_k_bic(X: np.ndarray,
                 k_range: range = range(3, 11),
                 n_init: int = 5,
                 seed: int = 42) -> tuple[int, list[float], list[float]]:
    """
    Seleziona il numero ottimale di componenti GMM minimizzando il BIC.

    Returns
    -------
    k_opt      : numero ottimale di cluster
    bic_scores : lista BIC per ogni K
    aic_scores : lista AIC per ogni K
    """
    bic_scores, aic_scores = [], []
    for k in k_range:
        gmm = GaussianMixture(n_components=k, covariance_type="full",
                              n_init=n_init, random_state=seed)
        gmm.fit(X)
        bic_scores.append(gmm.bic(X))
        aic_scores.append(gmm.aic(X))

    k_opt = list(k_range)[int(np.argmin(bic_scores))]
    return k_opt, bic_scores, aic_scores


def fit_gmm(X: np.ndarray, k: int, n_init: int = 10, seed: int = 42) -> GaussianMixture:
    """Fitta il GMM finale con il K ottimale."""
    gmm = GaussianMixture(n_components=k, covariance_type="full",
                          n_init=n_init, random_state=seed)
    gmm.fit(X)
    return gmm


# ── 3. Valutazione ────────────────────────────────────────────────────────────

def evaluate_clustering(X: np.ndarray,
                        labels: np.ndarray,
                        sample_size: int = 5000,
                        seed: int = 42) -> dict:
    """
    Calcola Silhouette Score, Davies-Bouldin Index e Calinski-Harabasz Score.

    Returns
    -------
    dict con chiavi: silhouette, davies_bouldin, calinski_harabasz
    """
    sil = silhouette_score(X, labels, sample_size=sample_size, random_state=seed)
    dbi = davies_bouldin_score(X, labels)
    chi = calinski_harabasz_score(X, labels)

    print("=== CLUSTERING EVALUATION ===")
    print(f"Silhouette Score     : {sil:.4f}  (↑ meglio, range [-1,1])")
    print(f"Davies-Bouldin Index : {dbi:.4f}  (↓ meglio)")
    print(f"Calinski-Harabasz    : {chi:.1f}  (↑ meglio)")

    return {"silhouette": sil, "davies_bouldin": dbi, "calinski_harabasz": chi}


# ── 4. Persistenza ────────────────────────────────────────────────────────────

def save_model(obj: object, path: str | Path) -> None:
    """Serializza un oggetto (scaler, reducer, gmm) con pickle."""
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f:
        pickle.dump(obj, f)
    print(f"Saved: {path}")


def load_model(path: str | Path) -> object:
    """Carica un oggetto serializzato con pickle."""
    with open(path, "rb") as f:
        return pickle.load(f)
