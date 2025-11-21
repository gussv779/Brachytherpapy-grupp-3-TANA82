import numpy as np
import streamlit as st
from streamlit_echarts import st_echarts

def dose_histogram(df, bins=80, clip_pct=0, dose_unit="Gy"):
    col1, col2 = st.columns([2, 5])
    assert {"Dose", "StructureName"}.issubset(df.columns)

    structures = ["Normalvävnad", "Prostata", "Rectum", "Urethra"]

    with col1:
        choice = st.radio("Välj struktur", structures, horizontal=True)

    vals = df.loc[df["StructureName"] == choice, "Dose"].dropna().to_numpy()

    if clip_pct and clip_pct > 0:
        lo, hi = np.percentile(vals, [clip_pct, 100 - clip_pct])
        vals = np.clip(vals, lo, hi)

    total_dose = np.sum(vals)
    mean_dose = np.mean(vals)
    max_dose = np.max(vals)

    with col2:
        st.metric(
            label=f"Total dos för {choice}",
            value=f"{total_dose:.2f}",
            delta=f"Medel: {mean_dose:.2f}, Max: {max_dose:.2f}",
            border = True,
            width="content"
        )

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
