import numpy as np
import pandas as pd

#Hitte på värden, allt detta är mer eller mindre jox som ska tas bort sen

def make_mock_dij(P: pd.DataFrame,
                  J: pd.DataFrame,
                  method: str = "distance",
                  seed: int = 0,
                  strength: float = 1.0,
                  cutoff_mm: float = 1.0) -> pd.DataFrame:
    """
    Create a mock dij matrix with shape (len(P), len(J)).
    - method="random": iid positive randoms
    - method="distance": ~ 1 / (||p - j||^2 + cutoff^2)
    Returns a DataFrame indexed by P.index, columns J.index.
    """
    rng = np.random.default_rng(seed)
    nP, nJ = len(P), len(J)

    if method == "random":
        # Positive randoms (lognormal gives a nice spread)
        dij = rng.lognormal(mean=0.0, sigma=0.5, size=(nP, nJ))

    elif method == "distance":
        # Coordinates (mm)
        Pxyz = P[["X_mm", "Y_mm", "Z_mm"]].to_numpy(float)[:, None, :]      # (nP,1,3)
        Jxyz = J[["X_mm", "Y_mm", "Z_mm"]].to_numpy(float)[None, :, :]      # (1,nJ,3)
        # Euclidean distance (mm)
        d = np.linalg.norm(Pxyz - Jxyz, axis=2)                              # (nP,nJ)
        # Inverse-square falloff with small cutoff to avoid div-by-zero
        dij = strength / (d**2 + cutoff_mm**2)

        # Optional: normalize each dwell column so columns are comparable
        col_sums = dij.sum(axis=0, keepdims=True)
        col_sums[col_sums == 0] = 1.0
        dij = dij / col_sums

        # Small random jitter so things aren’t perfectly smooth
        dij *= (1.0 + 0.05 * rng.normal(size=dij.shape))
        dij = np.clip(dij, a_min=0, a_max=None)
    else:
        raise ValueError("method must be 'random' or 'distance'")

    return pd.DataFrame(dij, index=P.index, columns=J.index)

def sample_dwell_times(J: pd.DataFrame, seed: int = 0, scale_s: float = 0.5) -> pd.Series:
    """
    Make positive dwell times t_j (seconds). Exponential is convenient.
    """
    rng = np.random.default_rng(seed)
    t = rng.exponential(scale=scale_s, size=len(J))
    return pd.Series(t, index=J.index, name="t_s")

def compute_point_doses(dij: pd.DataFrame, t: pd.Series) -> pd.Series:
    """
    Dose_i = sum_j dij[i,j] * t_j. Units depend on how dij is scaled.
    """
    # Ensure column order align
    t = t.reindex(dij.columns)
    dose = dij.to_numpy() @ t.to_numpy()
    return pd.Series(dose, index=dij.index, name="Dose")

# --------- Your wrapper for quick use ----------
def dose_for_each_point(P, J, method="distance", seed=0):
    dij = make_mock_dij(P, J, method=method, seed=seed)
    t = sample_dwell_times(J, seed=seed)
    Dose = compute_point_doses(dij, t)
    return dij, t, Dose