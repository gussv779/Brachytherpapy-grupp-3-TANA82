import streamlit as st

st.set_page_config(page_title="Dose Intervals — Live Editor", layout="wide")
from get_structured_data import format_dose_intervall

def intervalls_dataframe():
    st.subheader("Dose intervals")

    dose_intervall_df = format_dose_intervall()

    name_to_id_ui = {"Urethra": 1, "Prostata": 2, "Rectum": 3, "Normalvävnad": 4}
    id_to_name = {1: "Urethra", 2: "Prostata", 3: "Rectum", 4: "Normalvävnad"}
    dose_intervall_df["Structure"] = dose_intervall_df["StructureID"].map(id_to_name)

    shown_cols = ["Structure", "Lower", "Upper", "Lower Penalty", "Upper Penalty"]

    edited = st.data_editor(
        dose_intervall_df,
        column_config={
            "Structure": st.column_config.SelectboxColumn(
                "Structure", options=list(name_to_id_ui.keys())
            ),
            "Lower": st.column_config.NumberColumn("Lower", min_value=0.0),
            "Upper": st.column_config.NumberColumn("Upper", min_value=0.0),
            "Lower Penalty": st.column_config.NumberColumn("Lower Penalty", min_value=0.0),
            "Upper Penalty": st.column_config.NumberColumn("Upper Penalty", min_value=0.0),
        },
        column_order=shown_cols,
        hide_index=True,
        key="dose_table",
    )

    model_df = edited.copy()
    model_df["StructureID"] = model_df["Structure"].map(name_to_id_ui)

    chart_df = model_df.dropna(subset=["Lower", "Upper", "Structure"]).copy()
    chart_df["StructureOrder"] = chart_df["Structure"].astype("category")

    return edited
