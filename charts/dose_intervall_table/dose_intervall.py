import altair as alt
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
        hide_index=False,
        key="dose_table",
    )

    model_df = edited.copy()
    model_df["StructureID"] = model_df["Structure"].map(name_to_id_ui)

    chart_df = model_df.dropna(subset=["Lower", "Upper", "Structure"]).copy()
    chart_df["StructureOrder"] = chart_df["Structure"].astype("category")

    st.subheader("Charts")

    with st.expander("Intervals & penalties", expanded=False):
        interval = alt.Chart(chart_df).mark_rule(size=6).encode(
            y=alt.Y("StructureOrder:N", title="Structure", sort=list(name_to_id_ui.keys())),
            x=alt.X("Lower:Q", title="Dose"),
            x2="Upper:Q",
            tooltip=[
                alt.Tooltip("Structure:N"),
                alt.Tooltip("Lower:Q", format=".2f"),
                alt.Tooltip("Upper:Q", format=".2f"),
                alt.Tooltip("Lower Penalty:Q", format=".2f"),
                alt.Tooltip("Upper Penalty:Q", format=".2f"),
            ],
        )
        points = (
                alt.Chart(chart_df).mark_point(size=60).encode(y="StructureOrder:N", x="Lower:Q",
                                                               tooltip=["Structure", "Lower"])
                + alt.Chart(chart_df).mark_point(size=60).encode(y="StructureOrder:N", x="Upper:Q",
                                                                 tooltip=["Structure", "Upper"])
        )
        st.altair_chart((interval + points).properties(height=280), use_container_width=True)
        st.caption("Tip: add/remove rows or tweak numbers above — the chart updates instantly.")

    with st.expander("Penalties", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            st.write("Lower")
            st.altair_chart(alt.Chart(chart_df).mark_bar().encode(
                x="Lower Penalty:Q", y=alt.Y("Structure:N", sort="-x")
            ).properties(height=240), use_container_width=True)
        with col2:
            st.write("Upper")
            st.altair_chart(alt.Chart(chart_df).mark_bar().encode(
                x="Upper Penalty:Q", y=alt.Y("Structure:N", sort="-x")
            ).properties(height=240), use_container_width=True)

    return edited
