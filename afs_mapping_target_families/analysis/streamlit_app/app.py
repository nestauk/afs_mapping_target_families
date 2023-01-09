import streamlit as st
import time
import pandas as pd
import numpy as np
import altair as alt
import utils
from PIL import Image
from itertools import chain

import os
from afs_mapping_target_families.getters.processed.combined_data import (
    get_combined_data,
)

# -


@st.cache
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode("utf-8")


current_dir = os.getcwd()
alt.themes.register("nestafont", utils.nestafont)
alt.themes.enable("nestafont")

colours = utils.NESTA_COLOURS

# here we load the favicon and we set the page config (so what appears in the tab on your web browser)
im = Image.open(f"{current_dir}/images/favicon.ico")
st.set_page_config(page_title="2021-2022 ASQ-3 Results", layout="wide", page_icon=im)

# this creates a separate container for us to put the header in
header = st.container()

with header:
    nesta_logo = Image.open(f"{current_dir}/images/nesta_logo.png")
    st.image(nesta_logo, width=250)
    # This creates a title and adds some markdown for the second column
    st.title("Results of the 2021-2022 ASQ-3 Survey Across England")
    st.markdown(
        "  **website:** https://www.nesta.org/ **| email:** emily.bicks@nesta.org.uk"
    )

# As it's password protected, we've created a function here which means the app can only run if you've typed the password in.
def streamlit_asq():
    # This sets a spinner so we know that the report is updating as we change the user selections.
    with st.spinner("Updating Report..."):
        data = get_combined_data()

    # This radio button lets you pick a larger group so you're not overwhelmed by all the possible categories
    major_grouping_column_data = st.radio(
        "Pick a metric to visualise",
        [
            "Response Rate",
            "% Positive Responses - Overall",
            "% Positive Responses - Communication Skills",
            "% Positive Responses - Gross Motor Skills",
            "% Positive Responses - Fine Motor Skills",
            "% Positive Responses - Problem Solving Skills",
            "% Positive Responses - Personal/Social Skills",
        ],
    )
    # Once a user has picked a subgroup it assigns it to the variable major_grouping_column_data.
    if major_grouping_column_data == "Response Rate":
        column_data_to_plot = ["response_rate"]
    elif major_grouping_column_data == "% Positive Responses - Overall":
        column_data_to_plot = ["p_above_avg_overall"]
    elif major_grouping_column_data == "% Positive Responses - Communication Skills":
        column_data_to_plot = ["p_above_avg_comms"]
    elif major_grouping_column_data == "% Positive Responses - Gross Motor Skills":
        column_data_to_plot = ["p_above_avg_gms"]
    elif major_grouping_column_data == "% Positive Responses - Fine Motor Skills":
        column_data_to_plot = ["p_above_avg_fms"]
    elif major_grouping_column_data == "% Positive Responses - Problem Solving Skills":
        column_data_to_plot = ["p_above_avg_problem_solving"]
    elif major_grouping_column_data == "% Positive Responses - Personal/Social Skills":
        column_data_to_plot = ["p_above_avg_personal_social"]

    date_filter = data["date"].unique()
    date_selections = st.multiselect("Choose Quarters", date_filter)

    # This lets you select multiple regions. So you can choose North and Mid Wales for example at the same time.
    region_filter = data["Region"].unique()
    region_selections = st.multiselect(
        "Choose Region, leave blank to view all of England", region_filter
    )
    # We still want the map to plot, so if they haven't chosen a region selection, we want the lsoas_to_plot dataframe to be just all LSOAs.
    if len(region_selections) != 0:
        lsoas_to_plot = list(data[data["Region"].isin(region_selections)]["ONS code"])
    else:
        lsoas_to_plot = data["ONS code"].unique()

    regions = alt.topo_feature(
        "https://raw.githubusercontent.com/nestauk/afs_mapping_target_families/2_streamlit_app/afs_mapping_target_families/analysis/streamlit_app/topo_lookup.json",
        "lad",
    )
    map_data = data.copy()
    if len(date_filter) != 0:
        map_data = map_data[map_data["date"].isin(date_selections)]
        if len(region_filter) != 0:
            map_data = map_data[map_data["Region"].isin(region_selections)]
    elif len(region_filter) != 0:
        map_data = map_data[map_data["Region"].isin(region_selections)]

    map = (
        alt.Chart(regions)
        .mark_geoshape(stroke="white")
        .transform_lookup(
            # We want the LAD13CD field to be the linking column in the regions data.
            lookup="properties.LAD13CD",
            # And we want to combine it with the data, using the "lsoa_code" field to link it, and then we want to bring across a number of columns from the WIMD dataset.
            from_=alt.LookupData(
                map_data,
                "ONS code",
                [
                    "Region",
                    "p_above_avg_comms",
                    "p_above_avg_gms",
                    "p_above_avg_fms",
                    "p_above_avg_problem_solving",
                    "p_above_avg_personal_social",
                    "p_above_avg_overall",
                    "date",
                    "response_rate",
                ],
            ),
            # We then can filter the data if you only want to have a selection of LSOAs.
        )
        .encode(
            # As with normal altair functions, we can add a tooltip using any column in the topojson file or one of the columns we've brought across from the other data.
            tooltip=[
                alt.Tooltip(
                    major_grouping_column_data, title=major_grouping_column_data
                ),
                alt.Tooltip("Area:N", title="Area"),
                alt.Tooltip("Region", title="Region"),
                alt.Tooltip(
                    "date",
                    title="Date",
                ),
                alt.Tooltip("response_rate:N", title="Response Rate"),
            ],
            # We've used alt.condition so altair knows to plot every LSOA that's not got a value as "lightgrey", we set the condition as < 0 as we filled the NaNs as -1. Without this line, it would only
            # plot the LSOAs that have a value.
        )
        .properties(width=700, height=650)
    )


# This adds on the password protection
pwd = st.sidebar.text_input("Password:", type="password")
# st.secrets reads it in from the toml folder, and then runs the streamlit_asq function if the password matches.
if pwd == st.secrets["PASSWORD"]:
    streamlit_asq()
elif pwd == "":
    pass
else:
    st.error("Password incorrect. Please try again.")
