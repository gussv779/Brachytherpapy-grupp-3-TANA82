import numpy as np
import streamlit as st

from charts.lpm_chart.lpm_chart import lpm_chart
from charts.dose_intervall_table.dose_intervall import intervalls_dataframe
from get_structured_data import get_structured_data
from lpm_calculations import lpm_calculations
from mock_dose_data import dose_for_each_point

st.set_page_config(page_title="3D Scatter (ECharts)", page_icon="📈", layout="wide")

patient = "patient1"
df_all, P, J, S = get_structured_data(patient)

dij, t, Dose = dose_for_each_point(P, S, J, method="distance", seed=42)
P_baseline = P.copy()
P_baseline["Dose"] = Dose

df_dose_intervall = intervalls_dataframe()

tj, Dose_opt = lpm_calculations(dij, df_dose_intervall, P)
P_opt = P.copy()
P_opt["Dose"] = np.asarray(Dose_opt).reshape(-1)

#points_chart(df_all)

lpm_chart(P_opt)
