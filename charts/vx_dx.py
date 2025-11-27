from __future__ import annotations
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
import streamlit as st
from streamlit_echarts import st_echarts

def _vx_curve_from_sorted(d_sorted: np.ndarray, dose_grid: np.ndarray) -> np.ndarray:
    N = d_sorted.size
    idx = np.searchsorted(d_sorted, dose_grid, side="left")
    vx = (N - idx) * 100.0 / N
    return vx

def _dx_curve_from_sorted(d_sorted: np.ndarray, vol_grid_pct: np.ndarray) -> np.ndarray:
    q = vol_grid_pct / 100.0
    return np.percentile(d_sorted, q * 100.0, method="linear")

def _prep_grids(d_all: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    dmax = float(np.nanmax(d_all)) if d_all.size else 1.0
    dose_grid = np.linspace(0.0, dmax, 256)
    vol_grid = np.linspace(0.0, 100.0, 201)
    return dose_grid, vol_grid

def compute_vx_dx(P):

    all_d = P["Dose"].to_numpy()
    dg, vg = _prep_grids(all_d)
    dose_grid = dg
    vol_grid_pct = vg

    vx_curves: Dict[str, pd.DataFrame] = {}
    dx_curves: Dict[str, pd.DataFrame] = {}

    for s, df_s in P.groupby("StructureName", sort=False):
        d = np.sort(df_s["Dose"].to_numpy().astype(float))
        if d.size == 0:
            continue
        vx = _vx_curve_from_sorted(d, dose_grid)
        dx = _dx_curve_from_sorted(d, vol_grid_pct)
        vx_curves[s] = pd.DataFrame({"dose": dose_grid, "Vx": vx})
        dx_curves[s] = pd.DataFrame({"volume_pct": vol_grid_pct, "Dx": dx})

    return vx_curves, dx_curves


def _make_line_series(data_xy: List[Tuple[float, float]]) -> List[List[float]]:
    return [[float(x), float(y)] for x, y in data_xy]

def vx_dx_diagram(P):

    st.markdown("### Vx/Dx Värden")

    vx_curves, dx_curves = compute_vx_dx(P)

    dmax = float(np.nanmax(P["Dose"].to_numpy()))

    dose_min, dose_max = st.slider(
        "Dose-axel (Gy)", 0.0, dmax, (0.0, dmax), 0.5,
        key="dvh-x-dose"
    )
    vol_min, vol_max = st.slider(
        "Volym-axel (%)", 0.0, 100.0, (0.0, 100.0), 1.0,
        key="dvh-y-vol"
    )

    struct_names = list(vx_curves.keys())

    for i in range(0, len(struct_names), 2):
        row_structs = struct_names[i:i+2]
        row_cols = st.columns(len(row_structs))

        for s, col in zip(row_structs, row_cols):
            vx_df = vx_curves[s]
            dx_df = dx_curves[s]

            vx_val = float(np.interp(dose_max, vx_df["dose"], vx_df["Vx"]))
            dx_val = float(np.interp(vol_max, dx_df["volume_pct"], dx_df["Dx"]))

            with col:
                with st.container(border=True):
                    st.markdown(f"**{s}**")
                    mcol1, mcol2 = st.columns(2)
                    with mcol1:
                        st.metric(
                            label=f"V{dose_max:.1f} Gy",
                            value=f"{vx_val:.1f} %",
                            width="content",
                        )
                    with mcol2:
                        st.metric(
                            label=f"D{vol_max:.0f} %",
                            value=f"{dx_val:.2f} Gy",
                            width="content",
                        )

    series = [{
        "type": "line",
        "name": s,
        "showSymbol": False,
        "smooth": True,
        "emphasis": {"focus": "series"},
        "universalTransition": True,
        "data": _make_line_series(list(zip(df["dose"], df["Vx"]))),
    } for s, df in vx_curves.items()]

    x_axis = {
        "type": "value",
        "name": "Dose (Gy)",
        "nameGap": 22,
        "min": dose_min,
        "max": dose_max,
    }
    y_axis = {
        "type": "value",
        "name": "Volym (%)",
        "min": vol_min,
        "max": vol_max,
    }
    key_chart = "dvh-chart-standard"

    options = {
        "animationDuration": 700,
        "tooltip": {
            "trigger": "axis",
        },
        "legend": {"type": "scroll", "bottom": 0, "selectedMode": "multiple"},
        "grid": {"left": 48, "right": 16, "bottom": 60, "top": 40},
        "xAxis": x_axis,
        "yAxis": y_axis,
        "series": series,
    }
    st_echarts(options=options, height="420px", key=key_chart)
