import streamlit as st
import time
import pandas as pd
import numpy as np
import altair as alt
import app_utils
from PIL import Image
from itertools import chain

# from afs_mapping_target_families.getters.processed.combined_data import (
#    get_combined_data,
# )
import os
from statistics import mean


@st.cache
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode("utf-8")


current_dir = os.getcwd()
alt.themes.register("nestafont", app_utils.nestafont)
alt.themes.enable("nestafont")

colours = app_utils.NESTA_COLOURS

# here we load the favicon and we set the page config (so what appears in the tab on your web browser)
im = Image.open(
   f"{current_dir}/images/favicon.ico"
)
st.set_page_config(page_title="2021-2022 ASQ-3 Results", layout="wide", page_icon=im)

# this creates a separate container for us to put the header in

# As it's password protected, we've created a function here which means the app can only run if you've typed the password in.
def streamlit_asq():

    # This sets a spinner so we know that the report is updating as we change the user selections.
    with st.spinner("Updating Report..."):
        # data = get_combined_data()
        # FOR NOW, LOAD DATA LOCALLY UNTIL FIGURE OUT A WAY TO CONNECT CLOUD TO AWS
        data = pd.read_csv(
            f"{current_dir}/datasets/DATA.csv"
        )
        click = alt.selection_multi(fields=["ONS code"])
        # data = pd.read_csv("{PROJECT_DIR}/afs_mapping_target_families/analysis/streamlit_app/datasets/2021_2022_compiled.csv")
        # This radio button lets you pick a larger group so you're not overwhelmed by all the possible categories
        header = st.container()
        with header:
            nesta_logo = Image.open(
                f"{current_dir}/images/nesta_logo.png"
            )
            st.title("Results of the 2021-2022 ASQ-3 Survey Across England")
            col1, col2 = st.columns([1, 10])
            with col1:
                st.image(nesta_logo, width=100)
            with col2:
                st.markdown(
                    "           **website:** https://www.nesta.org/ **| email:** emily.bicks@nesta.org.uk"
                )
            st.markdown(
                "**This dashboard is a under active development and plots and metrics should not be interpreted as final**"
            )
        tab1, tab2 = st.tabs(["Dashboard", "About the Data"])
        with tab1:
            with st.container():
                # st.header("Select Date Range and Region to Filter Plots")
                col1, col2, col3 = st.columns(3, gap="large")
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
                        "Choose Region, leave blank to view all of England",
                        region_filter,
                    )

                with col3:
                    response_rate_filter = st.slider(
                        "Choose a minimum response rate", min_value=0
                    )
            with st.container():
                col1, col2 = st.columns(2, gap="large")
                with col1:
                    st.subheader("Distribution of ASQ across England")

                    major_grouping_column_data = st.selectbox(
                        "Pick a metric to view on the map and filter the ASQ bars chart",
                        [
                            "Response Rate",
                            "At or Above Expected - All Categories",
                            "At or Above Expected - Communication Skills",
                            "At or Above Expected - Gross Motor Skills",
                            "At or Above Expected - Fine Motor Skills",
                            "At or Above Expected - Problem Solving Skills",
                            "At or Above Expected - Personal/Social Skills",
                        ],
                    )

                    COLUMN_NAME_MAPPINGS = {
                        "Response Rate": "response_rate",
                        "At or Above Expected - All Categories": "p_above_avg_overall",
                        "At or Above Expected - Communication Skills": "p_above_avg_comms",
                        "At or Above Expected - Gross Motor Skills": "p_above_avg_gms",
                        "At or Above Expected - Fine Motor Skills": "p_above_avg_fms",
                        "At or Above Expected - Problem Solving Skills": "p_above_avg_problem_solving",
                        "At or Above Expected - Personal/Social Skills": "p_above_avg_personal_social",
                    }

                    column_selection_actual_column_name = COLUMN_NAME_MAPPINGS[
                        major_grouping_column_data
                    ]

                    for col in COLUMN_NAME_MAPPINGS.values():
                        data[col] = (
                            data[col]
                            .replace(
                                {
                                    "-": -0.01,
                                    "DK": -0.01,
                                    "dk": -0.01,
                                    "Could not compute": -0.01,
                                    "Could Not Calculate Response Rate": -0.01,
                                }
                            )
                            .astype("float64")
                            * 100
                        )

                    # filter cuas to only include those with response rate within the specified range
                    cuas_to_plot = list(
                        data.loc[(data["response_rate"] >= response_rate_filter)][
                            "ONS code"
                        ]
                    )

                    # if using the region filter, filter the cuas to only be those within the specific region
                    if len(region_selections) != 0:
                        cuas_to_plot = [
                            cua
                            for cua in cuas_to_plot
                            if cua
                            in list(
                                data[data["Region"].isin(region_selections)]["ONS code"]
                            )
                        ]

                    geojson_url = "https://raw.githubusercontent.com/VolcanoBlue13/uk_geojson_topojson_datasets/main/geojson/UK/County_Unitary_Authority/C_UA_UK_2021_boundaries_ultra_generalised.geojson"
                    regions = alt.Data(
                        url=geojson_url,
                        format=alt.DataFormat(property="features", type="json"),
                    )

                    map_data = data.copy()
                    ## Replace missing values with a -1

                    ## Filter the data to the date selection
                    map_data = map_data[map_data["date"] == date_selections]
                    ## Convert the column to a float64 so it will plot correctly

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

                    data_for_barchart = data_for_barchart.loc[
                        data_for_barchart[column_selection_actual_column_name] != -1
                    ]

                    tab3, tab4 = st.tabs(["Map", "Bar"])

                    with tab3:
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
                                            scheme="redyellowblue", domain=[30, 100]
                                        ),
                                    ),
                                    alt.value("lightgrey"),
                                ),
                            )
                            .properties(width=600, height=500)
                            .configure_view(strokeWidth=0)
                        )

                        st.altair_chart(map)
                    with tab4:
                        header = "Bar"
                        st.markdown(
                            "The red line indicates the Percent of Students with a Good Level of Development on the EYFSP"
                        )
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
                                    alt.Tooltip(
                                        specified_feature_to_plot,
                                        title=specified_feature_to_plot,
                                    ),
                                ],
                            )
                            .properties(width=800)
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
                                    title="Fraction of Students At or Above Average (%)",
                                ),
                                tooltip=[
                                    alt.Tooltip("la_name:N", title="Local Authority"),
                                    alt.Tooltip(
                                        "eyfsp_score:Q",
                                        title="EYFSP - Percent of Students Reaching Good Level of Development",
                                    ),
                                ],
                            )
                            .properties(width=800)
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
                        (data_for_boxplot["percent_above_avg"] != -1)
                    ]
                    data_for_boxplot["percent_above_avg"] = round(
                        data_for_boxplot["percent_above_avg"], 2
                    )
                    # data_for_boxplot['category'] = data_for_boxplot['category'].apply(wrap)

                    data_for_boxplot = data_for_boxplot[
                        data_for_boxplot["date"] == date_selections
                    ]

                    boxplot = (
                        alt.Chart(data_for_boxplot)
                        .mark_boxplot(size=50, extent=0.5)
                        .transform_filter(
                            alt.FieldOneOfPredicate(
                                field="ONS code", oneOf=cuas_to_plot
                            )
                        )
                        .configure_axis(labelLimit=0)
                        .encode(
                            x=alt.X(
                                "percent_above_avg:Q",
                                title="Percent of Students At or Above Average (%) on ASQ",
                            ),
                            y=alt.Y("category:N", title=None),
                            tooltip=[
                                alt.Tooltip("la_name:N"),
                                alt.Tooltip("date:N"),
                                alt.Tooltip(
                                    "percent_above_avg:Q", title="% At or Above Average"
                                ),
                            ],
                            color=alt.value("#0000FF"),
                            stroke=alt.value("white"),
                        )
                        .properties(width=800, height=800)
                    )

                    st.altair_chart(boxplot)
        with tab2:
            st.title("About the Datasets")
            st.header("Datasets")
            st.markdown("The plots on this dashboard rely on three datasets:")
            st.markdown(
                "1. [Quarterly outcomes at age 2](https://www.gov.uk/government/statistics/child-development-outcomes-at-2-to-2-and-a-half-years-quarterly-data-for-2021-to-2022): This is the ASQ dataset used for the analysis"
            )
            st.markdown(
                "2. [Annual EYFSP scores from 2021/2022 - Headline measures by characteristics](https://explore-education-statistics.service.gov.uk/data-catalogue/early-years-foundation-stage-profile-results/2021-22): This is used to generate statistics on the % of children reaching a GLD from each county/unitary authority"
            )
            st.markdown(
                "3. [Census 2021 age by single year](https://www.ons.gov.uk/datasets/TS007/editions/2021/versions/1): This is used to estimate the response rate for each county/unitary authority"
            )

            st.header("Metrics")
            st.markdown("The following metrics are reported in this dashboard:")
            st.markdown(
                "**Response Rate**: this is the estimated response rate for each county/unitary authority on all five categories of the ASQ. Response rates are estimated using population estimates from the Census 2021 data. The response rate is calculated as the Total number of students who answered all 5 categories over the year / Total number of 1 year olds when the census was conducted in March 2021."
            )
            st.markdown(
                "**At or Above Expected - All Categories**: This is the total number of children who were at or above the expected level in all five categories in the ASQ / The total number of children for whom all five categories was completed."
            )
            st.markdown(
                "**At or Above Expected - Communication Skills**: This is the total number of children who were at or above the expected level in Communication Skills from the ASQ / The total number of children for whom the ASQ Communication Skills was completed."
            )
            st.markdown(
                "**At or Above Expected - Gross Motor Skills**: This is the total number of children who were at or above the expected level in Gross Motor Skills from the ASQ / The total number of children for whom the ASQ Gross Motor Skills was completed."
            )
            st.markdown(
                "**At or Above Expected - Fine Motor Skills**: This is the total number of children who were at or above the expected level in Fine Motor Skills from the ASQ / The total number of children for whom the ASQ Fine Motor Skills was completed."
            )
            st.markdown(
                "**At or Above Expected - Problem Solving Skills**: This is the total number of children who were at or above the expected level in Problem Solving Skills from the ASQ / The total number of children for whom the ASQ Problem Solving Skills was completed."
            )
            st.markdown(
                "**At or Above Expected - Personal/Social Skills**: This is the total number of children who were at or above the expected level in Personal/Social Skills from the ASQ / The total number of children for whom the ASQ Personal/Social Skills was completed."
            )
            st.markdown(
                "**EYFSP - Percent of Students Reaching Good Level of Development**: This is the percent of students who reached a good level of development as reported by the EYFSP"
            )

            st.header("Data Manipulation")
            st.markdown(
                "The following steps were taken to clean the data before it was presented in the dashboard:"
            )
            st.markdown("**Aggregating Quarterly ASQ Data**")
            st.markdown(
                "The raw ASQ data is broken down quarterly covering the date ranges: April - June 2021; July - September 2021; October - December 2021; January - March 2022. We add an additional date range 'Annual' covering the entire period from April 2021 - March 2022"
            )
            st.markdown(
                "For each local authority, we calculate the total number of students who answered the question for that category and the total number of students who were above average for the category, and use those totals to calculate the annual percent of students who were above average for that category. If an LA submitted 'Don't know' (represented by 'dk' or 'DK' in the raw data) for one of the categories then we do not display the data aggregated annually"
            )

            st.markdown("**Estimating Response Rates**")
            st.markdown(
                "Response rates are estimated using population estimates from the Census 2021 data. The response rate is calculated as the Total number of students who answered all 5 categories over the year / Total number of 1 year olds when the census was conducted in March 2021."
            )


def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["password"] == st.secrets["password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show input for password.
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error.
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        st.error("😕 Password incorrect")
        return False
    else:
        # Password correct.

        return True


if check_password():
    streamlit_asq()
