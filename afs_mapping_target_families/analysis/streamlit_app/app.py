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

# As it's password protected, we've created a function here which means the app can only run if you've typed the password in.
def streamlit_asq():

    # This sets a spinner so we know that the report is updating as we change the user selections.
    with st.spinner("Updating Report..."):
        data = get_combined_data()
        click = alt.selection_multi(fields=["ONS code"])
        # data = pd.read_csv("{PROJECT_DIR}/afs_mapping_target_families/analysis/streamlit_app/datasets/2021_2022_compiled.csv")
        # This radio button lets you pick a larger group so you're not overwhelmed by all the possible categories
        header = st.container()
        with header:
            nesta_logo = Image.open(
                f"{PROJECT_DIR}/afs_mapping_target_families/analysis/streamlit_app/images/nesta_logo.png"
            )
            # This creates a title and adds some markdown for the second column
            st.title("Results of the 2021-2022 ASQ-3 Survey Across England")
            col1, col2 = st.columns([1, 10])
            with col1:
                st.image(nesta_logo, width=100)
            with col2:
                st.markdown(
                    "           **website:** https://www.nesta.org/ **| email:** emily.bicks@nesta.org.uk"
                )
            st.markdown("""----""")
        with st.container():
            # st.header("Select Date Range and Region to Filter Plots")
            col1, col2 = st.columns(2, gap="large")
            with col1:
                date_filter = data["date"].unique()
                date_selections = st.selectbox(
                    "Choose Date Range", date_filter, index=len(date_filter) - 1
                )
            ## Alternative if you want multiple quarters
            # date_selections = st.multiselect("Choose Quarters", date_filter, "April 2021 - June 2021")

            # This lets you select multiple regions. So you can choose North and Mid Wales for example at the same time.
            with col2:
                region_filter = data["Region"].unique()
                region_selections = st.multiselect(
                    "Choose Region, leave blank to view all of England", region_filter
                )
        with st.container():
            col1, col2 = st.columns(2, gap="large")
            with col1:
                st.subheader("Distribution of ASQ across England")

                major_grouping_column_data = st.selectbox(
                    "Pick a metric to view on the map and filter the ASQ bars chart",
                    [
                        "Response Rate",
                        "% Positive Responses - All Categories",
                        "% Positive Responses - Communication Skills",
                        "% Positive Responses - Gross Motor Skills",
                        "% Positive Responses - Fine Motor Skills",
                        "% Positive Responses - Problem Solving Skills",
                        "% Positive Responses - Personal/Social Skills",
                    ],
                )

                COLUMN_NAME_MAPPINGS = {
                    "Response Rate": "response_rate",
                    "% Positive Responses - All Categories": "p_above_avg_overall",
                    "% Positive Responses - Communication Skills": "p_above_avg_comms",
                    "% Positive Responses - Gross Motor Skills": "p_above_avg_gms",
                    "% Positive Responses - Fine Motor Skills": "p_above_avg_fms",
                    "% Positive Responses - Problem Solving Skills": "p_above_avg_problem_solving",
                    "% Positive Responses - Personal/Social Skills": "p_above_avg_personal_social",
                }

                column_selection_actual_column_name = COLUMN_NAME_MAPPINGS[
                    major_grouping_column_data
                ]

                # We still want the map to plot, so if they haven't chosen a region selection, we want the lsoas_to_plot dataframe to be just all LSOAs.
                if len(region_selections) != 0:
                    cuas_to_plot = list(
                        data[data["Region"].isin(region_selections)]["ONS code"]
                    )
                else:
                    cuas_to_plot = data["ONS code"].unique()

                geojson_url = "https://raw.githubusercontent.com/VolcanoBlue13/uk_geojson_topojson_datasets/main/geojson/UK/County_Unitary_Authority/C_UA_UK_2021_boundaries_ultra_generalised.geojson"
                regions = alt.Data(
                    url=geojson_url,
                    format=alt.DataFormat(property="features", type="json"),
                )

                map_data = data.copy()
                ## Replace missing values with a -1
                map_data[column_selection_actual_column_name] = map_data[
                    column_selection_actual_column_name
                ].replace(
                    {
                        "-": -1,
                        "DK": -1,
                        "Could Not Calculate Response Rate": -1,
                        "Could not compute": -1,
                    }
                )
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
                    map_data["response_rate"] = map_data["response_rate"].astype(
                        "float64"
                    )
                    map_data["response_rate"] = map_data["response_rate"] * 100
                ## If you wanted to group the date selections (i.e. select multiple dates), you'll need this bit of code below.
                # if len(date_selections) != 0:
                # map_data = map_data[map_data["dates"].isin(date_selections)]
                # map_data = map_data.groupby(["ONS code"])[column_selection_actual_column_name].mean()

                encoding_type = ":Q"
                specified_feature_to_plot = (
                    column_selection_actual_column_name + encoding_type
                )

                # value_to_plot = mean("datum." + specified_feature_to_plot)

                # This is an alternative condition that I've set up so it plots the C/UAs where there is no value. Earlier on I set the C/UAs which didn't have data to be -100,
                # so anything that is above 0 we want it to plot normally (i.e. with a colour scale), but if it's got no value, we want it to be a light grey. This sets up the query for later
                # on.

                alternative_condition = (
                    "datum." + column_selection_actual_column_name + " > 0"
                )

                data_for_barchart = data.copy()
                # only have eyfsp scores annually
                data_for_barchart = data_for_barchart[
                    data_for_barchart["date"] == date_selections
                ]

                data_for_barchart["eyfsp_score"] = data_for_barchart[
                    "eyfsp_score"
                ].apply(lambda x: x / 100)

                if column_selection_actual_column_name == "response_rate":
                    data_for_barchart = data_for_barchart.loc[
                        data_for_barchart[column_selection_actual_column_name]
                        != "Could Not Calculate Response Rate"
                    ]

                else:
                    data_for_barchart = data_for_barchart.loc[
                        data_for_barchart[column_selection_actual_column_name]
                        != "Could not compute"
                    ]

                tab1, tab2 = st.tabs(["Map", "Bar"])

                with tab1:
                    header = "Map"
                    map = (
                        alt.Chart(regions)
                        .configure(
                            padding={"left": 3, "top": 0, "right": 5, "bottom": 0}
                        )
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
                                    "la_name",
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
                                alt.Tooltip("la_name:N", title="Local Authority"),
                                alt.Tooltip("Region:N", title="Region"),
                                alt.Tooltip(
                                    "date:N",
                                    title="Date",
                                ),
                                alt.Tooltip(
                                    "response_rate:N",
                                    title="Response Rate (%)",
                                    format=".2f",
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
                                        direction="vertical",
                                        legendX=-1,
                                        orient="left",
                                        gradientLength=500,
                                        title=None,
                                    ),
                                    scale=alt.Scale(
                                        scheme="yellowgreenblue", domain=[0, 100]
                                    ),
                                ),
                                alt.value("lightgrey"),
                            ),
                        )
                        .properties(width=600, height=500)
                        .configure_view(strokeWidth=0)
                    )

                    st.altair_chart(map)
                with tab2:
                    header = "Bar"
                    bar_sort_order = list(
                        data_for_barchart.sort_values(
                            by=column_selection_actual_column_name, ascending=False
                        )["la_name"]
                    )

                    base = (
                        alt.Chart(data_for_barchart)
                        .transform_filter(
                            alt.FieldOneOfPredicate(
                                field="ONS code", oneOf=cuas_to_plot
                            )
                        )
                        .encode(alt.Y("la_name:N", sort=bar_sort_order, title=None))
                    )

                    asq_chart = (
                        base.mark_bar()
                        .encode(
                            alt.Y("la_name:N", sort=bar_sort_order, title=None),
                            alt.X(specified_feature_to_plot),
                            tooltip=[
                                alt.Tooltip("la_name:N", title="Local Authority"),
                                alt.Tooltip(specified_feature_to_plot, title="ASQ"),
                            ],
                        )
                        .properties(width=600)
                    )

                    eyfsp_chart = (
                        base.mark_tick(
                            color="red",
                            thickness=4,
                        )
                        .encode(
                            alt.Y("la_name:N", sort=bar_sort_order, title=None),
                            alt.X(
                                "eyfsp_score:Q",
                                title="Fraction of Students Above Average (%)",
                            ),
                            tooltip=[
                                alt.Tooltip("la_name:N", title="Local Authority"),
                                alt.Tooltip("eyfsp_score:Q", title="EYFSP"),
                            ],
                        )
                        .properties(width=600)
                    )

                    bar_chart = (
                        alt.layer(asq_chart, eyfsp_chart)
                        .resolve_scale()
                        .configure_axis(labelLimit=0)
                    )

                    st.altair_chart(bar_chart)

            with col2:
                st.subheader("Distribution of ASQ Scores by Category")
                data_for_boxplot = data.copy()

                data_for_boxplot = data_for_boxplot.rename(
                    columns={
                        "p_above_avg_comms": "Communication Skills",
                        "p_above_avg_gms": "Gross Motor Skills",
                        "p_above_avg_fms": "Fine Motor Skills",
                        "p_above_avg_problem_solving": "Problem Solving Skills",
                        "p_above_avg_personal_social": "Personal Social Skills",
                        "p_above_avg_overall": "All Categories",
                    }
                )

                data_for_boxplot = (
                    pd.DataFrame(
                        data_for_boxplot[
                            [
                                "la_name",
                                "Region",
                                "ONS code",
                                "date",
                                "Communication Skills",
                                "Gross Motor Skills",
                                "Fine Motor Skills",
                                "Problem Solving Skills",
                                "Personal Social Skills",
                                "All Categories",
                            ]
                        ]
                        .set_index(["la_name", "Region", "ONS code", "date"])
                        .stack()
                    )
                    .reset_index()
                    .rename(columns={"level_4": "category", 0: "percent_above_avg"})
                )

                data_for_boxplot = data_for_boxplot.loc[
                    (data_for_boxplot["percent_above_avg"] != "-")
                    & (data_for_boxplot["percent_above_avg"] != "Could not compute")
                ]
                data_for_boxplot["percent_above_avg"] = round(
                    data_for_boxplot["percent_above_avg"].astype("float64") * 100, 2
                )
                # data_for_boxplot['category'] = data_for_boxplot['category'].apply(wrap)

                data_for_boxplot = data_for_boxplot[
                    data_for_boxplot["date"] == date_selections
                ]

                if len(region_selections) != 0:
                    cuas_to_plot = list(
                        data[data["Region"].isin(region_selections)]["ONS code"]
                    )
                else:
                    cuas_to_plot = data["ONS code"].unique()

                boxplot = (
                    alt.Chart(data_for_boxplot)
                    .mark_boxplot(size=50, extent=0.5)
                    .transform_filter(
                        alt.FieldOneOfPredicate(field="ONS code", oneOf=cuas_to_plot)
                    )
                    .configure_axis(labelLimit=0)
                    .encode(
                        x=alt.X(
                            "percent_above_avg:Q",
                            title="Percent of Students Above Average (%)",
                        ),
                        y=alt.Y("category:N", title=None),
                        tooltip=[
                            alt.Tooltip("la_name:N"),
                            alt.Tooltip("date:N"),
                            alt.Tooltip("percent_above_avg:Q", title="% Above Average"),
                        ],
                        color=alt.value("#0000FF"),
                        stroke=alt.value("white"),
                    )
                    .properties(width=550, height=600)
                )

                st.altair_chart(boxplot)


streamlit_asq()
