import streamlit as st
import time
import pandas as pd
import numpy as np
import altair as alt
import utils
from PIL import Image
from itertools import chain
from afs_mapping_target_families.getters.processed.combined_data import (
    get_combined_data,
)
import os
from afs_mapping_target_families import PROJECT_DIR
from statistics import mean

## For some unknown reason, Streamlit won't let you import this. I'm also not sure Streamlit will be able to read from S3, we've got round this by putting the data in
## the same folder as the Streamlit app which is fine for publically available data.
# from afs_mapping_target_families.getters.processed.combined_data import (
#    get_combined_data,
# )

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
im = Image.open(
    f"{PROJECT_DIR}/afs_mapping_target_families/analysis/streamlit_app/images/favicon.ico"
)
st.set_page_config(page_title="2021-2022 ASQ-3 Results", layout="wide", page_icon=im)

# this creates a separate container for us to put the header in
header = st.container()

with header:
    nesta_logo = Image.open(
        f"{PROJECT_DIR}/afs_mapping_target_families/analysis/streamlit_app/images/nesta_logo.png"
    )
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
        # data = pd.read_csv("{PROJECT_DIR}/afs_mapping_target_families/analysis/streamlit_app/datasets/2021_2022_compiled.csv")
        # This radio button lets you pick a larger group so you're not overwhelmed by all the possible categories
        with st.sidebar:

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

            COLUMN_NAME_MAPPINGS = {
                "Response Rate": "response_rate",
                "% Positive Responses - Overall": "p_above_avg_overall",
                "% Positive Responses - Communication Skills": "p_above_avg_comms",
                "% Positive Responses - Gross Motor Skills": "p_above_avg_gms",
                "% Positive Responses - Fine Motor Skills": "p_above_avg_fms",
                "% Positive Responses - Problem Solving Skills": "p_above_avg_problem_solving",
                "% Positive Responses - Personal/Social Skills": "p_above_avg_personal_social",
            }

            column_selection_actual_column_name = COLUMN_NAME_MAPPINGS[
                major_grouping_column_data
            ]
            date_filter = data["date"].unique()
            np.append(date_filter, "All")
            date_selections = st.radio("Choose Quarters", date_filter)
            ## Alternative if you want multiple quarters
            # date_selections = st.multiselect("Choose Quarters", date_filter, "April 2021 - June 2021")

            # This lets you select multiple regions. So you can choose North and Mid Wales for example at the same time.
            region_filter = data["Region"].unique()
            region_selections = st.multiselect(
                "Choose Region, leave blank to view all of England", region_filter
            )

        # We still want the map to plot, so if they haven't chosen a region selection, we want the lsoas_to_plot dataframe to be just all LSOAs.
        if len(region_selections) != 0:
            cuas_to_plot = list(
                data[data["Region"].isin(region_selections)]["ONS code"]
            )
        else:
            cuas_to_plot = data["ONS code"].unique()

        geojson_url = "https://raw.githubusercontent.com/VolcanoBlue13/uk_geojson_topojson_datasets/main/geojson/UK/County_Unitary_Authority/C_UA_UK_2021_boundaries_ultra_generalised.geojson"
        regions = alt.Data(
            url=geojson_url, format=alt.DataFormat(property="features", type="json")
        )

        map_data = data.copy()
        ## Replace missing values with a -1
        map_data[column_selection_actual_column_name] = map_data[
            column_selection_actual_column_name
        ].replace({"-": -1, "DK": -1, "Could Not Calculate Response Rate": -1})
        ## Filter the data to the date selection
        map_data = map_data[map_data["date"] == date_selections]
        ## Convert the column to a float64 so it will plot correctly
        map_data[column_selection_actual_column_name] = map_data[
            column_selection_actual_column_name
        ].astype("float64")
        ## Convert the column selected to a percentage
        map_data[column_selection_actual_column_name] = (
            map_data[column_selection_actual_column_name] * 100
        )
        ## If the column selected isn't the response rate, convert the response rate column to a float64 and a percentage.
        if column_selection_actual_column_name != "response_rate":
            map_data["response_rate"] = map_data["response_rate"].replace(
                {"Could Not Calculate Response Rate": -1}
            )
            map_data["response_rate"] = map_data["response_rate"].astype("float64")
            map_data["response_rate"] = map_data["response_rate"] * 100
        ## If you wanted to group the date selections (i.e. select multiple dates), you'll need this bit of code below.
        # if len(date_selections) != 0:
        # map_data = map_data[map_data["dates"].isin(date_selections)]
        # map_data = map_data.groupby(["ONS code"])[column_selection_actual_column_name].mean()

        encoding_type = ":Q"
        specified_feature_to_plot = column_selection_actual_column_name + encoding_type
        # value_to_plot = mean("datum." + specified_feature_to_plot)

        # This is an alternative condition that I've set up so it plots the C/UAs where there is no value. Earlier on I set the C/UAs which didn't have data to be -100,
        # so anything that is above 0 we want it to plot normally (i.e. with a colour scale), but if it's got no value, we want it to be a light grey. This sets up the query for later
        # on.
        alternative_condition = "datum." + column_selection_actual_column_name + " > 0"

        map = (
            alt.Chart(regions)
            .mark_geoshape(stroke="white")
            .transform_lookup(
                # We want the CTYUA21CD field to be the linking column in the regions data.
                lookup="properties.CTYUA21CD",
                # And we want to combine it with the data, using the "ONS code" field to link it, and then we want to bring across a number of columns from the WIMD dataset.
                from_=alt.LookupData(
                    map_data,
                    "ONS code",
                    [
                        column_selection_actual_column_name,
                        "Area",
                        "Region",
                        "date",
                        "response_rate",
                    ],
                ),
                # We then can filter the data if you only want to have a selection of LSOAs.
            )
            .transform_filter(
                alt.FieldOneOfPredicate(
                    field="properties.CTYUA21CD", oneOf=cuas_to_plot
                )
            )
            .encode(
                # As with normal altair functions, we can add a tooltip using any column in the topojson file or one of the columns we've brought across from the other data.
                tooltip=[
                    alt.Tooltip(
                        specified_feature_to_plot,
                        title=major_grouping_column_data,
                        format=".2f",
                    ),
                    alt.Tooltip("Area:N", title="Area"),
                    alt.Tooltip("Region:N", title="Region"),
                    alt.Tooltip(
                        "date:N",
                        title="Date",
                    ),
                    alt.Tooltip(
                        "response_rate:N", title="Response Rate (%)", format=".2f"
                    ),
                ],
                # We've used alt.condition so altair knows to plot every C/UAs that's not got a value as "lightgrey", we set the condition as < 0 as
                # we filled the "DK", "-" and "Could Not Calculate Response Rate" as -100. Without this line, it would only
                # plot the C/UAs that have a value so there would be lots of boundaries missing.
                color=alt.condition(
                    alternative_condition,
                    alt.Color(
                        specified_feature_to_plot,
                        legend=alt.Legend(
                            orient="none", legendX=-1, title=major_grouping_column_data
                        ),
                        scale=alt.Scale(scheme="yellowgreenblue", domain=[0, 100]),
                    ),
                    alt.value("lightgrey"),
                ),
            )
            .properties(width=700, height=650)
            .configure_view(strokeWidth=0)
        )

        st.altair_chart(map)


streamlit_asq()
"""
# This adds on the password protection

pwd = st.sidebar.text_input("Password:", type="password")
# st.secrets reads it in from the toml folder, and then runs the streamlit_asq function if the password matches.
if pwd == st.secrets["PASSWORD"]:
    streamlit_asq()
elif pwd == "":
    pass
else:
    st.error("Password incorrect. Please try again.")
"""
