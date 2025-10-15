from get_structured_data import get_structured_data, format_dose_intervall
from lpm_calculations import lpm_calculations
from mock_dose_data import dose_for_each_point

patient = "patient1"


df_all, dose_intervall, df_points, df_dwell, df_structure = get_structured_data(patient)
df_dose_intervall = format_dose_intervall(dose_intervall)

P = df_points # Set of all dose points, P=∪s∈SPs
S = df_structure # Set of structures, including PTV and OARs
J = df_dwell # Set of dwell position

#dij = dosberäkningsvärden
# temporary dose data
dij, t, Dose = dose_for_each_point(P, S, J, method="distance", seed=42)

tj, Dose_opt = lpm_calculations(dij, df_dose_intervall, P)

print("hello")
