import numpy as np
import streamlit as st

from charts.dose_intervall_table.dose_intervall import intervalls_dataframe
from charts.lpm_chart.lpm_chart import lpm_chart
from equations.dose_calculation import dose_calc
from get_structured_data import get_structured_data, convert_bounds
from charts.histogram.histogram import dose_histogram
from equations.lpm_calculations import lpm_calculations
from charts.vx_dx.vx_dx import vx_dx_diagram

st.set_page_config(page_title="3D Scatter (ECharts)", page_icon="📈", layout="wide")

ss = st.session_state
ss.setdefault("dij_cache", {})
ss.setdefault("opt_cache", {})

col1, col2, col3 = st.columns([1, 1, 6])

with col1:
    patient = st.selectbox(
        "Choose a patient",
        ("patient1", "patient2", "patient3", "patient4", "patient5"),
    )

with col2:
    rakr_h = st.number_input(
        "RAKR (Sjukhus) [mGy/h]",
        value=30,
        step=1,
    )
    rakr_SJ = rakr_h * 1e-3 / 3600.0

df_all, P, J, a_df, df_points_original, df_dwell_original = get_structured_data(patient)

dij_key = (patient, rakr_SJ)

if dij_key not in ss["dij_cache"]:
    dij = dose_calc(a_df, df_points_original, df_dwell_original, rakr_SJ)

    ss["dij_cache"][dij_key] = (dij, P)
    dij, P_cached = ss["dij_cache"][dij_key]
else:
    dij, P_cached = ss["dij_cache"][dij_key]

df_dose_intervall = intervalls_dataframe()

if "last_dose_intervall" not in st.session_state:
    st.session_state.last_dose_intervall = None
if "opt_cache" not in st.session_state:
    st.session_state.opt_cache = {}

changed = not df_dose_intervall.equals(st.session_state.last_dose_intervall)

opt_key = (patient, rakr_SJ)

if changed or opt_key not in st.session_state.opt_cache:
    df_dose_intervall_si = convert_bounds(df_dose_intervall)
    tj, Dose_opt = lpm_calculations(dij, df_dose_intervall_si, P)

    st.session_state.opt_cache[opt_key] = (tj, Dose_opt)
    st.session_state.last_dose_intervall = df_dose_intervall.copy()
else:
    tj, Dose_opt = st.session_state.opt_cache[opt_key]

P_opt = P_cached.copy()
P_opt["Dose"] = np.asarray(Dose_opt).reshape(-1)

#points_chart(df_all)

lpm_chart(P_opt)

dose_histogram(P_opt)

vx_dx_diagram(P_opt)