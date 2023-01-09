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

if __name__ == "__main__":
    quarterly_dfs = [get_q1_21_22(), get_q2_21_22(), get_q3_21_22(), get_q4_21_22()]
    dates = [
        "April 2021 - June 2021",
        "July 2021 - September 2021",
        "October 2021 - December 2021",
        "January 2022 - March 2022",
    ]

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

    # add a column to indicate the response rate of a given LA
    # response rate is calculated for the entire year based on census population estimates
    pop_data = get_pop_age_1()
    pop_data["Upper Tier Local Authorities"] = pop_data[
        "Upper Tier Local Authorities"
    ].str.replace("[^\w\s]", " ")
    las = yearly_df.Area.unique()
    yearly_df["response_rate"] = float
    for la in las:
        yearly_df.loc[yearly_df["Area"] == la, "response_rate"] = get_response_rate(
            yearly_df[yearly_df["Area"] == la],
            pop_data[pop_data["Upper Tier Local Authorities"] == la],
        )

    # save compiled data to S3
    upload_obj(yearly_df, BUCKET_NAME, "processed/2021_2022_compiled.csv")
