import numpy as np
import streamlit as st
from streamlit_echarts import st_echarts

def dose_histogram(df, bins=20, clip_pct=1, dose_unit="Gy/h"):
    assert {"Dose", "StructureName"}.issubset(df.columns)

    structures = ["Normalvävnad", "Prostata", "Rectum", "Urethra"]

    # 🔹 välj vilken struktur som ska visas (triggar rerun automatiskt)
    choice = st.radio("Välj struktur", structures, horizontal=True)

    vals = df.loc[df["StructureName"] == choice, "Dose"].dropna().to_numpy()
    if vals.size == 0:
        st.info("Inga dosvärden.")
        return

    # (valfritt) klipp bort svansar
    if clip_pct and clip_pct > 0:
        lo, hi = np.percentile(vals, [clip_pct, 100 - clip_pct])
        vals = np.clip(vals, lo, hi)

    # skapa histogram på rå dos-skala
    vmin, vmax = vals.min(), vals.max()
    edges = np.linspace(vmin, vmax, bins + 1)
    counts, _ = np.histogram(vals, bins=edges)
    labels = [f"{edges[i]:.2f}-{edges[i+1]:.2f}" for i in range(len(edges) - 1)]

    options = {
        "title": {"text": choice, "left": "center"},
        "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
        "xAxis": {"type": "category", "data": labels, "name": f"Dose ({dose_unit})"},
        "yAxis": {"type": "value", "name": "Count"},
        "series": [{"type": "bar", "data": counts.tolist()}],
    }

    st_echarts(options=options, height="400px", key=f"hist-{choice}")
