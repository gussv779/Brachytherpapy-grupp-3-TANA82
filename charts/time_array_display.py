import streamlit as st
import pandas as pd

def time_array(tj: pd.DataFrame):
    total_seconds = tj["Time (s)"].sum()

    total_minutes = total_seconds / 60

    st.metric(label="Total Tid i minuter: ", value=f"{total_minutes:.2f}", border=True)
    st.write(f"Total Tid i sekunder: {total_seconds:.2f}")

    with st.expander("Se data matris"):
        st.table(tj)

