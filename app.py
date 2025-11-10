import numpy as np
import streamlit as st
import hashlib
import pandas as pd

from charts.dose_intervall_table.dose_intervall import intervalls_dataframe
from charts.lpm_chart.lpm_chart import lpm_chart
from get_structured_data import get_structured_data, convert_bounds
from lpm_calculations import lpm_calculations
from dose_calculation import dose_calc_fast
from histogram import dose_histogram

st.set_page_config(page_title="3D Scatter (ECharts)", page_icon="📈", layout="wide")

ss = st.session_state
ss.setdefault("dij_cache", {})
ss.setdefault("opt_cache", {})

col1, col2 = st.columns([1, 9]) # ugly solution i dont like, but you cant adjust the width in a clean fashion
with col1:
    patient = st.selectbox(
        "Choose a patient",
        ("patient1", "patient2", "patient3", "patient4", "patient5"),
    )
    df_all, P, J, a_df, df_points_original, df_dwell_original = get_structured_data(patient)

if patient in ss["dij_cache"]:
    dij, dose, P_cached = ss["dij_cache"][patient]
else:
    dij, dose = dose_calc_fast(a_df, df_points_original, df_dwell_original)
    ss["dij_cache"][patient] = (dij, dose, P)
    dij, dose, P_cached = ss["dij_cache"][patient]

df_dose_intervall = intervalls_dataframe()

if "last_dose_intervall" not in st.session_state:
    st.session_state.last_dose_intervall = None
if "opt_cache" not in st.session_state:
    st.session_state.opt_cache = {}

changed = not df_dose_intervall.equals(st.session_state.last_dose_intervall)

opt_key = patient
if changed or opt_key not in st.session_state.opt_cache:
    df_dose_intervall_si = convert_bounds(df_dose_intervall, "mGy/h", "Gy/s")
    tj, Dose_opt = lpm_calculations(dij, df_dose_intervall_si, P)
    st.session_state.opt_cache[opt_key] = (tj, Dose_opt)
    st.session_state.last_dose_intervall = df_dose_intervall.copy()
else:
    tj, Dose_opt = st.session_state.opt_cache[opt_key]

P_opt = P_cached.copy()
P_opt["Dose"] = np.asarray(Dose_opt).reshape(-1) * 3600.0

#points_chart(df_all)

lpm_chart(P_opt)

dose_histogram(P_opt)