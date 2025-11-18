from __future__ import annotations

import numpy as np
import pandas as pd


def dose_calc(a_df, df_points, df_dwell, rakr_SJ,  rmin_cm=0.2):
    theta_tab = a_df['theta'].values
    a1_tab = a_df['a1'].values
    a2_tab = a_df['a2'].values
    a3_tab = a_df['a3'].values
    b1_tab = a_df['b1'].values
    b2_tab = a_df['b2'].values
    b3_tab = a_df['b3'].values
    b4_tab = a_df['b4'].values

    P = df_points.iloc[:, :3].to_numpy(np.float64, copy=False)
    D = df_dwell.iloc[:, :3].to_numpy(np.float64, copy=False)

    nP = P.shape[0]
    nD = D.shape[0]

    r_cm = np.zeros((nP, nD), dtype=float)
    theta_deg = np.zeros((nP, nD), dtype=float)

    EPS = 1e-12

    for i in range(nP):
        v = P[i] - D
        r = np.linalg.norm(v, axis=1)
        r_cm[i, :] = r / 10

        theta_row = np.zeros(nD, dtype=float)
        for j in range(nD):
            if r[j] < EPS:
                theta_row[j] = 0.0
            else:
                cos_t = v[j, 2] / r[j]
                cos_t = np.clip(cos_t, -1.0, 1.0)
                theta_row[j] = np.degrees(np.arccos(cos_t))
        theta_deg[i, :] = theta_row

    th_flat = theta_deg.ravel()
    a1 = np.interp(th_flat, theta_tab, a1_tab).reshape(theta_deg.shape)
    a2 = np.interp(th_flat, theta_tab, a2_tab).reshape(theta_deg.shape)
    a3 = np.interp(th_flat, theta_tab, a3_tab).reshape(theta_deg.shape)
    b1 = np.interp(th_flat, theta_tab, b1_tab).reshape(theta_deg.shape)
    b2 = np.interp(th_flat, theta_tab, b2_tab).reshape(theta_deg.shape)
    b3 = np.interp(th_flat, theta_tab, b3_tab).reshape(theta_deg.shape)
    b4 = np.interp(th_flat, theta_tab, b4_tab).reshape(theta_deg.shape)

    r_eff = np.maximum(r_cm, rmin_cm)
    r2 = r_eff * r_eff
    d_constant = 1.0 / (4.0 * np.pi)
    D_prim = (d_constant / r2) * a1 * np.exp(-(a2 - a3 * r_eff) * r_eff)
    D_scat = (d_constant / r2) * b1 * ((1.0 + b2) - np.exp(-b3 * r_eff)) * np.exp(-b4 * r_eff)

    rakr_MC = 2.1e-7
    ratio = rakr_SJ / rakr_MC
    D_tot = D_prim + D_scat

    dose_matrix = ratio * D_tot
    dose_total = dose_matrix.sum(axis=1)

    dij = pd.DataFrame(dose_matrix)

    print("median Gy/s:", np.median(dose_total))
    print("95p   Gy/s:", np.quantile(dose_total, 0.95))
    print("median Gy/min:", np.median(dose_total * 60))

    return dij