import numpy as np
import streamlit as st

from charts.dose_intervall_table.dose_intervall import intervalls_dataframe
from charts.lpm_chart.lpm_chart import lpm_chart
from get_structured_data import get_structured_data
from lpm_calculations import lpm_calculations
from mock_dose_data import dose_for_each_point

st.set_page_config(page_title="3D Scatter (ECharts)", page_icon="📈", layout="wide")

col1, col2 = st.columns([1, 9]) # ugly solution i dont like, but you cant adjust the width in a clean fashion
with col1:
    patient = st.selectbox(
        "Choose a patient",
        ("patient1", "patient2", "patient3", "patient4", "patient5"),
    )
    df_all, P, J = get_structured_data(patient)

dij, t, Dose = dose_for_each_point(P, J, method="distance", seed=42)

df_dose_intervall = intervalls_dataframe()

tj, Dose_opt = lpm_calculations(dij, df_dose_intervall, P)
P_opt = P.copy()

# We're basically just inserting the optimized dose for each point into the points table
P_opt["Dose"] = np.asarray(Dose_opt).reshape(-1)

#points_chart(df_all)

lpm_chart(P_opt)
