from get_structured_data import get_structured_data, format_dose_intervall
from lpm_calculations import lpm_calculations, plot_LPM_curve
from mock_dose_data import dose_for_each_point

patient = "patient1"


df_all, dose_intervall, df_points, df_dwell, df_structure = get_structured_data(patient)
df_dose_intervall = format_dose_intervall(dose_intervall)

ptv = "prostata"

P = df_points # Set of all dose points, P=∪s∈SPs
S = df_structure # Set of structures, including PTV and OARs
J = df_dwell # Set of dwell position

#dij = dosberäkningsvärden
# temporary dose data
dij, t, Dose = dose_for_each_point(P, S, J, method="distance", seed=42)

current_structureID = 1
current_structure = df_dose_intervall.loc[df_dose_intervall["StructureID"] == current_structureID]
Ls = current_structure["Lower"].iloc[0] # Upper dose bound for structure s∈S
Us = current_structure["Upper"].iloc[0] # Prescription dose or a lower dose bound for structure s∈S
#Mx = Maximum allowed dose for structure s∈S
wls = current_structure["Lower Penalty"].iloc[0] # Non-negative penalty for dose being too low in structure s∈S
wus = current_structure["Upper Penalty"].iloc[0] # Non-negative penalty for dose being too high in structure s∈S

tj, Dose_opt = lpm_calculations(dij, df_dose_intervall, P)

dose_points = P.index[P["StructureID"] == current_structureID]
plot_LPM_curve(Ls, Us, wls, wus, Dose_opt[dose_points], "Urethra")
