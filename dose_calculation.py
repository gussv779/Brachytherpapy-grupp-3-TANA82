import numpy as np
import pandas as pd

def dose_calc(a_df, df_points, df_dwell):

    theta_tab = a_df['theta'].values
    a1_tab = a_df['a1'].values
    a2_tab = a_df['a2'].values
    a3_tab = a_df['a3'].values
    b1_tab = a_df['b1'].values
    b2_tab = a_df['b2'].values
    b3_tab = a_df['b3'].values
    b4_tab = a_df['b4'].values

    n_points = df_points.shape[0]
    n_dwell = df_dwell.shape[0]
    dose_matrix = np.zeros((n_points, n_dwell))

    EPS = 1e-12

    for i in range(n_points):
        p = df_points.iloc[i].values
        for j in range(n_dwell):
            d = df_dwell.iloc[j].values
            v = p - d
            r_mm = np.linalg.norm(v)
            if r_mm < EPS:
                theta_deg = 0.0
            else:
                cos_t = v[2] / r_mm
                cos_t = np.clip(cos_t, -1, 1)
                theta_deg = np.degrees(np.arccos(cos_t))
            r_cm = r_mm / 10

            a1 = np.interp(theta_deg, theta_tab, a1_tab)
            a2 = np.interp(theta_deg, theta_tab, a2_tab)
            a3 = np.interp(theta_deg, theta_tab, a3_tab)
            b1 = np.interp(theta_deg, theta_tab, b1_tab)
            b2 = np.interp(theta_deg, theta_tab, b2_tab)
            b3 = np.interp(theta_deg, theta_tab, b3_tab)
            b4 = np.interp(theta_deg, theta_tab, b4_tab)

            D_prim = (1 / (4 * np.pi * r_cm**2)) * a1 * np.exp(-(a2 - a3 * r_cm) * r_cm)
            D_scat = (1 / (4 * np.pi * r_cm**2)) * b1 * ((1 + b2) - np.exp(-b3 * r_cm)) * np.exp(-b4 * r_cm)

            rakr_MC = 2.1e-7
            rakr_SJ = 8.3e-6

            D_tot = D_prim + D_scat
            Dos_SJ = (rakr_SJ / rakr_MC) * D_tot

            dose_matrix[i, j] = Dos_SJ

    dose_total = np.sum(dose_matrix, axis=1)

    return dose_matrix, dose_total

def dose_calc_fast(a_df, df_points, df_dwell):
    # ---- coefficients & tables (as contiguous arrays) ----
    theta_tab = a_df['theta'].to_numpy(np.float64, copy=False)
    a1_tab = a_df['a1'].to_numpy(np.float64, copy=False)
    a2_tab = a_df['a2'].to_numpy(np.float64, copy=False)
    a3_tab = a_df['a3'].to_numpy(np.float64, copy=False)
    b1_tab = a_df['b1'].to_numpy(np.float64, copy=False)
    b2_tab = a_df['b2'].to_numpy(np.float64, copy=False)
    b3_tab = a_df['b3'].to_numpy(np.float64, copy=False)
    b4_tab = a_df['b4'].to_numpy(np.float64, copy=False)

    # ---- point & dwell coordinates (assumes first 3 cols are x,y,z) ----
    P = df_points.iloc[:, :3].to_numpy(np.float64, copy=False)  # (nP, 3)
    D = df_dwell.iloc[:, :3].to_numpy(np.float64, copy=False)   # (nD, 3)

    # ---- pairwise vectors & distances ----
    # diff shape: (nP, nD, 3)
    diff = P[:, None, :] - D[None, :, :]
    r_mm = np.linalg.norm(diff, axis=2)                         # (nP, nD)

    EPS = 1e-12
    safe_r = np.where(r_mm < EPS, 1.0, r_mm)
    cos_t = diff[..., 2] / safe_r
    cos_t = np.clip(cos_t, -1.0, 1.0)
    theta_deg = np.degrees(np.arccos(cos_t))
    theta_deg = np.where(r_mm < EPS, 0.0, theta_deg)            # exact 0 at r≈0

    r_cm = np.maximum(r_mm, EPS) / 10.0

    # ---- interpolate coefficients in bulk ----
    th_flat = theta_deg.ravel()
    a1 = np.interp(th_flat, theta_tab, a1_tab).reshape(theta_deg.shape)
    a2 = np.interp(th_flat, theta_tab, a2_tab).reshape(theta_deg.shape)
    a3 = np.interp(th_flat, theta_tab, a3_tab).reshape(theta_deg.shape)
    b1 = np.interp(th_flat, theta_tab, b1_tab).reshape(theta_deg.shape)
    b2 = np.interp(th_flat, theta_tab, b2_tab).reshape(theta_deg.shape)
    b3 = np.interp(th_flat, theta_tab, b3_tab).reshape(theta_deg.shape)
    b4 = np.interp(th_flat, theta_tab, b4_tab).reshape(theta_deg.shape)

    # ---- dose formulas (all vectorized) ----
    inv4pi = 1.0 / (4.0 * np.pi)
    r2 = r_cm * r_cm

    D_prim = (inv4pi / r2) * a1 * np.exp(-(a2 - a3 * r_cm) * r_cm)
    D_scat = (inv4pi / r2) * b1 * ((1.0 + b2) - np.exp(-b3 * r_cm)) * np.exp(-b4 * r_cm)

    rakr_MC = 2.1e-7
    rakr_SJ = 8.3e-6
    ratio = rakr_SJ / rakr_MC

    dose_matrix = ratio * (D_prim + D_scat)                     # (nP, nD)
    dose_total = dose_matrix.sum(axis=1)                        # (nP,)

    dij = pd.DataFrame(
        dose_matrix,
        index=df_points.index if df_points.index.is_unique else range(len(df_points)),
        columns=df_dwell.index if df_dwell.index.is_unique else range(len(df_dwell)),
    )

    return dij, dose_total