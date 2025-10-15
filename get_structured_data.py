from pathlib import Path
from typing import Dict, Optional, Tuple
import pandas as pd
from scipy.io import loadmat


def load_penalty_workbook(path, engine) -> Dict[str, pd.DataFrame]:
    xl = pd.ExcelFile(path, engine=engine)
    return {name: xl.parse(name) for name in xl.sheet_names}


def get_structured_data(patient):

    mat = loadmat(f"data/patient_data/raw_data/{patient}.mat", squeeze_me=True, struct_as_record=False)

    dose_intervall = load_penalty_workbook("data/dosecalculation/Dosintervall.xls", engine='xlrd')

    df_points = pd.DataFrame(mat["points"].reshape(-1, 3), columns=["X_mm", "Y_mm", "Z_mm"])
    df_points["StructureID"] = mat["structure"].reshape(-1).astype(int)
    df_dwell = pd.DataFrame(mat["dwell"].reshape(-1, 3), columns=["X_mm", "Y_mm", "Z_mm"])
    df_structure = pd.DataFrame(mat["structure"].reshape(-1))


    id_to_name = {
        1: "Urethra",
        2: "Prostata",
        3: "Rectum",
        4: "Normalvävnad",
    }
    df_points["StructureName"] = df_points["StructureID"].map(id_to_name)
    df_points["Type"] = "point"

    DWELL_ID = 5
    DWELL_NAME = "Dröjpunkt"

    df_dwell["StructureID"] = DWELL_ID
    df_dwell["StructureName"] = DWELL_NAME
    df_dwell["Type"] = "dwell"

    df_all = pd.concat([df_points, df_dwell], ignore_index=True)

    order = ["Urethra", "Prostata", "Rectum", "Normalvävnad", "Dröjpunkt"]
    df_all["StructureName"] = pd.Categorical(df_all["StructureName"], categories=order, ordered=False)

    return df_all, dose_intervall, df_points, df_dwell, df_structure

def format_dose_intervall(dose_intervall_dict: Dict[str, pd.DataFrame]) -> pd.DataFrame:
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
