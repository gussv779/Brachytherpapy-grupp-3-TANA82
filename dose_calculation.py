from __future__ import annotations

import numpy as np
import pandas as pd
import streamlit as st
from streamlit_echarts import st_echarts


def dose_calc_original(a_df, df_points, df_dwell):

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

def dose_calc(a_df, df_points, df_dwell, rakr_SJ):
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

    d_constant = 1.0 / (4.0 * np.pi)
    r2 = r_cm * r_cm
    D_prim = (d_constant / r2) * a1 * np.exp(-(a2 - a3 * r_cm) * r_cm)
    D_scat = (d_constant / r2) * b1 * ((1.0 + b2) - np.exp(-b3 * r_cm)) * np.exp(-b4 * r_cm)

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


#Det här är bara hitte på värden

def compute_radial_dose_curve(
    a_df: pd.DataFrame,
    rakr_SJ,
    r_min_cm: float = 0.1,
    r_max_cm: float = 10.0,
    n_r: int = 200,
) -> pd.DataFrame:
    r_cm = np.linspace(r_min_cm, r_max_cm, n_r)
    r_mm = r_cm * 10.0

    df_points = pd.DataFrame(
        {"X_mm": r_mm, "Y_mm": 0.0, "Z_mm": 0.0}
    )
    df_dwell = pd.DataFrame(
        {"X_mm": [0.0], "Y_mm": [0.0], "Z_mm": [0.0]}
    )

    dij = dose_calc(a_df, df_points, df_dwell, rakr_SJ)
    dose = dij.to_numpy()[:, 0]  # Gy/s at θ = 90°

    r0_cm = 1.0
    idx_1cm = np.argmin(np.abs(r_cm - r0_cm))
    D0 = dose[idx_1cm]

    g_r = (dose * r_cm**2) / (D0 * r0_cm**2)

    return pd.DataFrame({"r_cm": r_cm, "dose": dose, "g_r": g_r})

def radial_dose_diagram(a_df: pd.DataFrame, rakr_SJ) -> None:

    r_max = st.slider(
        "Maximalt avstånd från källan (cm)",
        min_value=0.5,
        max_value=10.0,
        value=10.0,
        step=0.5,
        key="rdf-r-max",
    )

    mode = st.radio(
        "Visa:",
        ["Normaliserad g_L(r)", "Absolut dos (Gy/s)"],
        horizontal=True,
        key="rdf-mode",
    )

    df_curve = compute_radial_dose_curve(a_df, rakr_SJ, r_min_cm=0.1, r_max_cm=r_max, n_r=200)

    if mode == "Normaliserad g_L(r)":
        y_values = df_curve["g_r"]
        y_name = "g_L(r)"

        # Automatically adjust to meaningful range
        y_min = float(y_values.min() * 0.98)
        y_max = float(y_values.max() * 1.02)

        # Prevent extremely tight axis range
        if (y_max - y_min) < 0.02:
            mid = 0.5 * (y_max + y_min)
            y_min = mid - 0.02
            y_max = mid + 0.02

    else:
        y_values = df_curve["dose"]
        y_name = "Dose rate (Gy/s)"
        y_min, y_max = 0.0, float(y_values.max() * 1.05)

    data = [[float(r), float(v)] for r, v in zip(df_curve["r_cm"], y_values)]

    series = [{
        "type": "line",
        "name": y_name,
        "showSymbol": False,
        "smooth": True,
        "emphasis": {"focus": "series"},
        "universalTransition": True,
        "data": data,
    }]

    x_axis = {
        "type": "value",
        "name": "r (cm)",
        "nameGap": 22,
        "min": 0.0,
        "max": float(r_max),
    }
    y_axis = {
        "type": "value",
        "name": y_name,
        "min": y_min,
        "max": y_max,
    }

    title = "Radial dosfunktion g\u2097(r) (transversalplan, \u03b8 = 90°)"
    options = {
        "title": {"text": title, "left": "center"},
        "animationDuration": 700,
        "tooltip": {
            "trigger": "axis",
            "valueFormatter": {"function": "v => v?.toFixed?.(4)"},
        },
        "legend": {"bottom": 0},
        "grid": {"left": 48, "right": 16, "bottom": 60, "top": 40},
        "xAxis": x_axis,
        "yAxis": y_axis,
        "series": series,
    }

    st_echarts(options=options, height="420px", key="rdf-chart")