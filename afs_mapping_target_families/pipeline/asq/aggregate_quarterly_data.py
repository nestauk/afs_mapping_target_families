import pandas as pd
from afs_mapping_target_families.getters.raw.asq import (
    get_q1_21_22,
    get_q2_21_22,
    get_q3_21_22,
    get_q4_21_22,
)
from afs_mapping_target_families.getters.raw.population_estimates import get_pop_age_1
from afs_mapping_target_families.utils.data_prep.asq_response_rates import (
    get_response_rate,
)
import json
from nesta_ds_utils.loading_saving.S3 import upload_obj
from afs_mapping_target_families import BUCKET_NAME


def get_annual_totals(col_data):
    if "dk" in col_data.values or "DK" in col_data.values or "-" in col_data.values:
        return "Could not compute"
    else:
        return col_data.sum()


def get_annual_avg(above_avg_total, total):
    if (above_avg_total == "Could not compute") or total == "Could not compute":
        return "Could not compute"
    else:
        return above_avg_total / total


def get_aggregated_percentage(df):
    overall_above_avg = int
    total = df.columns.str.contains("n_above_avg")
    percent = df.columns.str.contains("p_above_avg")
    for i, row in df.iterrows():
        overall_above_avg += row[total] * row[percent]

    return overall_above_avg / df[total].sum()


if __name__ == "__main__":
    quarterly_dfs = [get_q1_21_22(), get_q2_21_22(), get_q3_21_22(), get_q4_21_22()]
    dates = [
        "April 2021 - June 2021",
        "July 2021 - September 2021",
        "October 2021 - December 2021",
        "January 2022 - March 2022",
    ]
    cats = ["comms", "gms", "fms", "problem_solving", "personal_social", "overall"]

    # concatenate quarterly data and add date column
    yearly_df = pd.DataFrame()
    for i in range(0, len(dates)):
        date = dates[i]
        quarterly_dfs[i]["date"] = date
        yearly_df = pd.concat([yearly_df, quarterly_dfs[i]])

    # remove aggregated rows so each row represents a LA at a given date
    yearly_df = yearly_df[yearly_df["Region"] != "England"]

    # rename columns so they are shorter and easier to work with
    with open(
        "afs_mapping_target_families//config//clean_asq_column_mapping.json", "r"
    ) as f:
        column_map = json.load(f)
    yearly_df = yearly_df.rename(columns=column_map)
    # yearly_df = yearly_df.replace(to_replace = "DK", value = 0)
    # yearly_df = yearly_df.replace(to_replace = "dk", value = 0)
    # yearly_df = yearly_df.replace(to_replace = "-", value = 0)

    # add a column to indicate the response rate of a given LA
    # response rate is calculated for the entire year based on census population estimates
    pop_data = get_pop_age_1()
    pop_data["Upper Tier Local Authorities"] = pop_data[
        "Upper Tier Local Authorities"
    ].str.replace("[^\w\s]", " ")
    las = yearly_df.Area.unique()
    yearly_df["response_rate"] = float
    for la in las:
        la_data = yearly_df.loc[yearly_df["Area"] == la]

        response_rate = get_response_rate(
            yearly_df[yearly_df["Area"] == la],
            pop_data[pop_data["Upper Tier Local Authorities"] == la],
        )
        yearly_df.loc[yearly_df["Area"] == la, "response_rate"] = response_rate

        region = list(la_data["Region"])[0]
        ons_code = list(la_data["ONS code"])[0]
        total_comms = get_annual_totals(la_data["total_comms"])
        n_above_avg_comms = get_annual_totals(la_data["n_above_avg_comms"])
        p_above_avg_comms = get_annual_avg(n_above_avg_comms, total_comms)
        total_gms = get_annual_totals(la_data["total_gms"])
        n_above_avg_gms = get_annual_totals(la_data["n_above_avg_gms"])
        p_above_avg_gms = get_annual_avg(n_above_avg_gms, total_gms)
        total_fms = get_annual_totals(la_data["total_fms"])
        n_above_avg_fms = get_annual_totals(la_data["n_above_avg_fms"])
        p_above_avg_fms = get_annual_avg(n_above_avg_fms, total_fms)
        total_problem_solving = get_annual_totals(la_data["total_problem_solving"])
        n_above_avg_problem_solving = get_annual_totals(
            la_data["n_above_avg_problem_solving"]
        )
        p_above_avg_problem_solving = get_annual_avg(
            n_above_avg_problem_solving, total_problem_solving
        )
        total_personal_social = get_annual_totals(la_data["total_personal_social"])
        n_above_avg_personal_social = get_annual_totals(
            la_data["n_above_avg_personal_social"]
        )
        p_above_avg_personal_social = get_annual_avg(
            n_above_avg_personal_social, total_personal_social
        )
        total_overall = get_annual_totals(la_data["total_overall"])
        n_above_avg_overall = get_annual_totals(la_data["n_above_avg_overall"])
        p_above_avg_overall = get_annual_avg(n_above_avg_overall, total_overall)
        date = "Annual"

        row = [
            la,
            region,
            ons_code,
            total_comms,
            n_above_avg_comms,
            p_above_avg_comms,
            total_gms,
            n_above_avg_gms,
            p_above_avg_gms,
            total_fms,
            n_above_avg_fms,
            p_above_avg_fms,
            total_problem_solving,
            n_above_avg_problem_solving,
            p_above_avg_problem_solving,
            total_personal_social,
            n_above_avg_personal_social,
            p_above_avg_personal_social,
            total_overall,
            n_above_avg_overall,
            p_above_avg_overall,
            date,
            response_rate,
        ]
        yearly_df.loc[len(yearly_df)] = row
    # save compiled data to S3
    upload_obj(yearly_df, BUCKET_NAME, "processed/2021_2022_compiled.csv")
