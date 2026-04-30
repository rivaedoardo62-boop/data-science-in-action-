"""
clustering_model.py
───────────────────
Preprocessing, dimensionality reduction, GMM clustering, evaluation, and
model persistence for the Jakala × LUISS Customer Segmentation project.

Consumed by:
  - master_segmentation.ipynb
"""

import pickle
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.preprocessing import RobustScaler
from sklearn.mixture import GaussianMixture
from sklearn.metrics import silhouette_score, davies_bouldin_score, calinski_harabasz_score


# Fixed number of clusters — UMAP + GMM with K=6 is the locked-in configuration
# for the production segmentation. The K-sweep / bootstrap diagnostics in the
# master notebook (cells 23–24) are advisory only; they do not change FIXED_K.
FIXED_K: int = 6


# ── 1. Preprocessing ──────────────────────────────────────────────────────────

def winsorize(df: pd.DataFrame, cols: list[str], quantile: float = 0.99) -> pd.DataFrame:
    """Cap values at the given quantile (default 99th) to reduce outlier impact."""
    df = df.copy()
    for col in cols:
        if col in df.columns:
            cap = df[col].quantile(quantile)
            df[col] = df[col].clip(upper=cap)
    return df


def scale_features(X: np.ndarray) -> tuple[np.ndarray, RobustScaler]:
    """
    Apply RobustScaler (robust to residual outliers after winsorization).

    Returns
    -------
    X_scaled : np.ndarray
    scaler   : fitted RobustScaler (save to transform new data)
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
    Dimensionality reduction with UMAP.

    Parameters
    ----------
    n_components : 2 for visualisation, 3 for clustering (default)

    Returns
    -------
    X_umap  : np.ndarray of shape (n_samples, n_components)
    reducer : fitted UMAP object (save to transform new data)
    """
    try:
        from umap import UMAP
    except ImportError:
        raise ImportError("Install umap-learn: pip install umap-learn")

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
                 k_range: range = range(2, 11),
                 n_init: int = 5,
                 seed: int = 42) -> tuple[int, list[float], list[float]]:
    """
    Diagnostic only — sweep BIC/AIC across a range of GMM component counts.

    The production K is FIXED_K (=6); this helper exists to support the K-sweep
    validation cells of the master notebook and to expose the BIC elbow that
    motivates the production choice. The returned `k_opt` is informational
    (the K that minimises BIC) and is NOT used to override FIXED_K.

    Returns
    -------
    k_opt      : K minimising BIC over k_range (informational)
    bic_scores : BIC for each K in k_range
    aic_scores : AIC for each K in k_range
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


def fit_gmm(X: np.ndarray,
            k: int = FIXED_K,
            n_init: int = 10,
            seed: int = 42) -> GaussianMixture:
    """Fit the final GMM with the given number of components (default: FIXED_K=6)."""
    gmm = GaussianMixture(n_components=k, covariance_type="full",
                          n_init=n_init, random_state=seed)
    gmm.fit(X)
    return gmm


# ── 3. Evaluation ─────────────────────────────────────────────────────────────

def evaluate_clustering(X: np.ndarray,
                        labels: np.ndarray,
                        sample_size: int = 5000,
                        seed: int = 42) -> dict:
    """
    Compute Silhouette Score, Davies-Bouldin Index, and Calinski-Harabasz Score.

    Returns
    -------
    dict with keys: silhouette, davies_bouldin, calinski_harabasz
    """
    sil = silhouette_score(X, labels, sample_size=sample_size, random_state=seed)
    dbi = davies_bouldin_score(X, labels)
    chi = calinski_harabasz_score(X, labels)

    print("=== CLUSTERING EVALUATION ===")
    print(f"Silhouette Score     : {sil:.4f}  (higher is better, range [-1, 1])")
    print(f"Davies-Bouldin Index : {dbi:.4f}  (lower is better)")
    print(f"Calinski-Harabasz    : {chi:.1f}  (higher is better)")

    return {"silhouette": sil, "davies_bouldin": dbi, "calinski_harabasz": chi}


# ── 4. Persistence ────────────────────────────────────────────────────────────

def save_model(obj: object, path: str | Path) -> None:
    """Serialize an object (scaler, reducer, gmm) with pickle.

    path must be inside src/io/ — all pipeline outputs go there.
    """
    resolved = Path(path)
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(resolved, "wb") as f:
        pickle.dump(obj, f)
    print(f"Saved: {resolved}")


def load_model(path: str | Path) -> object:
    """Load a pickle-serialized object."""
    with open(path, "rb") as f:
        return pickle.load(f)
