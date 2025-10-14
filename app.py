import streamlit as st
from charts.lpm_chart.lpm_chart import lpm_chart
from charts.points_chart.points_chart import points_chart
from get_structured_data import get_structured_data
from mock_dose_data import dose_for_each_point

st.set_page_config(page_title="3D Scatter (ECharts)", page_icon="📈", layout="wide")
st.title("3D anatomy points — ECharts")

patient = "patient1"

df_all, dose_intervall, df_points, df_dwell, df_structure = get_structured_data(patient)

S = df_structure
P = df_points
J = df_dwell
dij, t, Dose = dose_for_each_point(P, S, J, method="distance", seed=42)

P_dose = P.copy()
P_dose["Dose"] = Dose

points_chart(df_all)

lpm_chart(P_dose)