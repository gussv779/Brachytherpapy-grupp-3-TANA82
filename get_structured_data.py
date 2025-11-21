from typing import Dict

import numpy as np
import pandas as pd
from scipy.io import loadmat


def load_penalty_workbook(path, engine) -> Dict[str, pd.DataFrame]:
    xl = pd.ExcelFile(path, engine=engine)
    return {name: xl.parse(name) for name in xl.sheet_names}


def get_structured_data(patient):

    mat = loadmat(f"data/patient_data/raw_data/{patient}.mat", squeeze_me=True, struct_as_record=False)
    mat_a = loadmat("data/dosecalculation/dos_parametrar.mat", squeeze_me=True, struct_as_record=False)

    a_array = mat_a['a']

    columns = ['a1', 'a2', 'a3', 'b1', 'b2', 'b3', 'b4']
    a_df = pd.DataFrame(a_array, columns=columns)
    a_df.insert(0, 'theta', np.arange(0, len(a_df)))

    df_points_original = pd.DataFrame(mat["points"])
    df_dwell_original = pd.DataFrame(mat["dwell"])
    df_points = pd.DataFrame(mat["points"].reshape(-1, 3), columns=["X_mm", "Y_mm", "Z_mm"])
    df_points["StructureID"] = mat["structure"].reshape(-1).astype(int)
    df_dwell = pd.DataFrame(mat["dwell"].reshape(-1, 3), columns=["X_mm", "Y_mm", "Z_mm"])


    id_to_name = {
        1: "Urethra",
        2: "Prostata",
        3: "Rectum",
        4: "Normalvävnad",
    }
    df_points["StructureName"] = df_points["StructureID"].map(id_to_name)

    return df_points, df_dwell, a_df, df_points_original, df_dwell_original

def format_dose_intervall() -> pd.DataFrame:
    dose_intervall_dict = load_penalty_workbook("data/dosecalculation/Dosintervall.xls", engine='xlrd')

    for name, df in dose_intervall_dict.items():
        if not df.empty:
            dose_df = df.copy()
            break
    else:
        raise ValueError("No non-empty sheets found in dose_intervall workbook.")
    dose_df = dose_df.dropna(how="all", axis=0).dropna(how="all", axis=1)
    dose_df.columns = ["StructureID", "Lower", "Upper", "Lower Penalty", "Upper Penalty"]
    dose_df = dose_df[dose_df["StructureID"] != "Struktur"]
    dose_df = dose_df.reset_index(drop=True)
    name_to_id = {
        "Urethra": 1,
        "Prostata": 2,
        "Rectum": 3,
        "Normal": 4
    }
    for col in ["Lower", "Upper", "Lower Penalty", "Upper Penalty"]:
        dose_df[col] = pd.to_numeric(dose_df[col], errors="coerce")

    dose_df["StructureID"] = dose_df["StructureID"].map(name_to_id)
    return dose_df


def convert_bounds(df):

    # Compute factor by converting Lower once
    L = df['Lower'].to_numpy(dtype=float)
    L_out = L * 1e-2

    U = df['Upper'].to_numpy(dtype=float)
    U_out = U * 1e-2

    df = df.copy()
    df['Lower'] = L_out
    df['Upper'] = U_out
    return df

