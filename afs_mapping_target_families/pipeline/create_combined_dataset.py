import pandas as pd
from afs_mapping_target_families.getters.raw.asq import (
    get_q1_21_22,
    get_q2_21_22,
    get_q3_21_22,
    get_q4_21_22,
    get_annual_21_22,
)
from afs_mapping_target_families.getters.raw.population_estimates import get_pop_age_1
from afs_mapping_target_families.getters.raw.eyfsp import get_la_gld
import json
from nesta_ds_utils.loading_saving.S3 import upload_obj
from afs_mapping_target_families import BUCKET_NAME

if __name__ == "__main__":
    raw_dfs = [
        get_q1_21_22(),
        get_q2_21_22(),
        get_q3_21_22(),
        get_q4_21_22(),
        get_annual_21_22(),
    ]
    dates = [
        "April 2021 - June 2021",
        "July 2021 - September 2021",
        "October 2021 - December 2021",
        "January 2022 - March 2022",
        "Annual",
    ]
    cats = ["comms", "gms", "fms", "problem_solving", "personal_social", "overall"]

    # concatenate quarterly data and add date column
    yearly_df = pd.DataFrame()
    for i in range(0, len(dates)):
        date = dates[i]
        raw_dfs[i]["date"] = date
        yearly_df = pd.concat([yearly_df, raw_dfs[i]])

    # remove aggregated rows so each row represents a LA at a given date
    yearly_df = yearly_df[yearly_df["Region"] != "England"]

    # rename columns so they are shorter and easier to work with
    with open(
        "afs_mapping_target_families//config//clean_asq_column_mapping.json", "r"
    ) as f:
        column_map = json.load(f)
    yearly_df = yearly_df.rename(columns=column_map)
    yearly_df = yearly_df.rename(columns={"Area": "la_name"})

    # add a column to indicate the response rate of a given LA
    # response rate is calculated for the entire year based on census population estimates
    pop_data = get_pop_age_1()
    pop_data["Upper Tier Local Authorities"] = (
        pop_data["Upper Tier Local Authorities"]
        .str.replace("-", " ")
        .str.replace(".", "")
    )
    las = yearly_df.la_name.unique()
    yearly_df["response_rate"] = float

    # add in eyfsp gld percentage for the annual data
    yearly_df["eyfsp_score"] = None
    eyfsp_data = get_la_gld()
    eyfsp_data["la_name"] = (
        eyfsp_data["la_name"].str.replace("-", " ").str.replace(".", "")
    )
    eyfsp_data["la_name"] = eyfsp_data["la_name"].str.replace(
        "Bristol, City of", "Bristol"
    )
    eyfsp_data["la_name"] = eyfsp_data["la_name"].str.replace(
        "Kingston upon Hull, City of", "Kingston upon Hull"
    )
    eyfsp_data["la_name"] = eyfsp_data["la_name"].str.replace(
        "Herefordshire, County of", "Herefordshire"
    )

    for la in las:
        # Response rate: total number of children who responded to all 5 categories in the year / Total number of 1 year olds as of March 2021
        try:
            response_rate = (
                yearly_df.loc[
                    (yearly_df["la_name"] == la) & (yearly_df["date"] == "Annual")
                ]["total_overall"].iloc[0]
            ) / (
                pop_data.loc[pop_data["Upper Tier Local Authorities"] == la][
                    "Population"
                ].iloc[0]
            )
        except:
            response_rate = "Could Not Calculate Response Rate"

        yearly_df.loc[yearly_df["la_name"] == la, "response_rate"] = response_rate

        try:
            eyfsp_score = eyfsp_data.loc[eyfsp_data["la_name"] == la][
                "gld_percentage"
            ].values[0]
        except:
            eyfsp_score = None

        yearly_df.loc[
            (yearly_df["la_name"] == la) & (yearly_df["date"] == "Annual"),
            "eyfsp_score",
        ] = eyfsp_score

    # save compiled data to S3
    upload_obj(yearly_df, BUCKET_NAME, "processed/2021_2022_compiled.csv")
