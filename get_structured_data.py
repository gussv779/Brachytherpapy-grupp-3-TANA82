from pathlib import Path
from typing import Dict, Optional, Tuple

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
    a_df.insert(0, 'theta', np.arange(1, len(a_df) + 1))

    df_points_original = pd.DataFrame(mat["points"])
    df_dwell_original = pd.DataFrame(mat["dwell"])
    df_points = pd.DataFrame(mat["points"].reshape(-1, 3), columns=["X_mm", "Y_mm", "Z_mm"])
    df_points["StructureID"] = mat["structure"].reshape(-1).astype(int)
    df_dwell = pd.DataFrame(mat["dwell"].reshape(-1, 3), columns=["X_mm", "Y_mm", "Z_mm"])
    #df_structure = pd.DataFrame(mat["structure"].reshape(-1))
    #Since we're incorporating the structure into df_points we don't really need a df_structure


    id_to_name = {
        1: "Urethra",
        2: "Prostata",
        3: "Rectum",
        4: "Normalvävnad",
    }
    df_points["StructureName"] = df_points["StructureID"].map(id_to_name)

    DWELL_ID = 5
    DWELL_NAME = "Dröjpunkt"

    df_dwell["StructureID"] = DWELL_ID
    df_dwell["StructureName"] = DWELL_NAME

    df_all = pd.concat([df_points, df_dwell], ignore_index=True)

    order = ["Urethra", "Prostata", "Rectum", "Normalvävnad", "Dröjpunkt"]
    df_all["StructureName"] = pd.Categorical(df_all["StructureName"], categories=order, ordered=False)

    return df_all, df_points, df_dwell, a_df, df_points_original, df_dwell_original

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


def convert_bounds(df, from_unit: str, to_unit: str, exposure_time_s: float | None = None):
    """
    Convert df['Lower'], df['Upper'] in-place from `from_unit` to `to_unit`.
    Supported units: 'Gy', 'Gy/s', 'mGy/h'.
    If converting between rate and cumulative dose, you must pass exposure_time_s.
    """

    # Compute factor by converting Lower once
    L = df['Lower'].to_numpy(dtype=float)
    L_gys = to_gys(L, from_unit, exposure_time_s)
    L_out = from_gys(L_gys, to_unit, exposure_time_s)

    U = df['Upper'].to_numpy(dtype=float)
    U_gys = to_gys(U, from_unit, exposure_time_s)
    U_out = from_gys(U_gys, to_unit, exposure_time_s)

    df = df.copy()
    df['Lower'] = L_out
    df['Upper'] = U_out
    return df

# Map everything via Gy and Gy/s
def to_gys(x, unit, exposure_time_s):
    if unit == 'Gy/s':
        return x
    if unit == 'mGy/h':
        return (x * 1e-3) / 3600.0
    if unit == 'Gy':
        if exposure_time_s is None:
            raise ValueError("Need exposure_time_s to convert Gy -> Gy/s")
        return x / exposure_time_s
    raise ValueError(f"Unsupported unit {unit}")

def from_gys(x, unit, exposure_time_s):
    if unit == 'Gy/s':
        return x
    if unit == 'mGy/h':
        return x * 3600.0 * 1e3
    if unit == 'Gy':
        if exposure_time_s is None:
            raise ValueError("Need exposure_time_s to convert Gy/s -> Gy")
        return x * exposure_time_s
    raise ValueError(f"Unsupported unit {unit}")

