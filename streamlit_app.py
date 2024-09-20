from __future__ import annotations

import pandas as pd
import seaborn as sns
import streamlit as st

from df_summary_stats import dataframe_with_summary_stats

st.set_page_config(
    layout="wide",
)


@st.cache_data
def get_data(data_name: str) -> pd.DataFrame:
    return sns.load_dataset(data_name)


dataset_names = sns.get_dataset_names()
dataset_names += ["Time-series"]

st.title(":material/troubleshoot: Summary stats")

with st.sidebar:
    """ ### Settings """
    data_name: str = st.selectbox(
        "Select dataset", dataset_names, index=len(dataset_names) - 2
    )

    data: pd.DataFrame = get_data(data_name)
    display_type: str = st.radio(
        "Show summary stats in",
        ["dialog", "main", "side-by-side"],
        index=2,
        horizontal=True,
    )


""" This app introduces the `dataframe_with_summary_stats` function that displays 
basic summary statistics of a column when a column is selected in a dataframe.
You can choose to display the summary stats in a dialog, main or side-by-side,
and feel free to try out different datasets from the sidebar."""

st.code(f"""
dataframe_with_summary_stats(
    data,
    display_type="{display_type.lower()}",
    use_container_width=True,
    **kwargs,
) 
""")

dataframe_with_summary_stats(
    data,
    display_type=display_type.lower(),
    use_container_width=True,
    height=400,
)
