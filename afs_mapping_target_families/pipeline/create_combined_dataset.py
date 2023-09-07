import pandas as pd
from afs_mapping_target_families.getters.raw.asq import (
    get_q1_21_22,
    get_q2_21_22,
    get_q3_21_22,
    get_q4_21_22,
    get_annual_21_22,
)
from afs_mapping_target_families.getters.raw.population_estimates import get_pop_age_1, q1_2yearolds, q2_2yearolds, q3_2yearolds, q4_2yearolds, annual_2yearolds
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

    hv_dfs = [
        q1_2yearolds(),
        q2_2yearolds(),
        q3_2yearolds(),
        q4_2yearolds(),
        annual_2yearolds()
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
        temp_data = raw_dfs[i].copy()
        temp_data = temp_data[temp_data["Region"] != "England"]
        temp_data["date"] = date
        temp_data.set_index("Area", inplace=True)
        hv_data = hv_dfs[i].set_index("Area")
        temp_data = temp_data.join(hv_data, how='left').reset_index()
        yearly_df = pd.concat([yearly_df, temp_data])

    yearly_df.reset_index(inplace=True)

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
        # Response rate census: total number of children who responded to all 5 categories in the year / Total number of 1 year olds as of March 2021
        try:
            response_rate_census = (
                yearly_df.loc[
                    (yearly_df["la_name"] == la) & (yearly_df["date"] == "Annual")
                ]["total_overall"].iloc[0]
            ) / (
                pop_data.loc[pop_data["Upper Tier Local Authorities"] == la][
                    "Population"
                ].iloc[0]
            )
        except:
            response_rate_census = "Could Not Calculate Response Rate"

        yearly_df.loc[yearly_df["la_name"] == la, "response_rate_census"] = response_rate_census

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

    # estimate response rate using the number of 2 1/2 year olds from the health visiting data
    yearly_df['response_rate_hv'] = float
    for i, row in yearly_df.iterrows():
        if (row['total_overall']!= '-') and (row['total_kids_hv']!= '-') and (row['total_overall']!= 'DK') and (row['total_kids_hv']!= 'DK'):
            yearly_df.at[i,'response_rate_hv'] = int(row['total_overall']) / int(row['total_kids_hv'])
        else:
            yearly_df.at[i,'response_rate_hv'] = "Could Not Calculate Response Rate"

    #create a combined estimate of the response rate from both datasets
    #for quarterly data use the health visiting data as that is all that's available
    # for annual data take the average of both estimates
    # if the estimates differ by more between 5 - 10% flag that it is medium confidence
    # if the estimates differ by > 10% flag that it is low confidence
    yearly_df['response_rate_combined'] = float
    yearly_df['response_rate_confidence'] = ""
    for i, row in yearly_df.iterrows():
        if (row["date"]!= "Annual"):
            yearly_df.at[i,'response_rate_combined'] = row['response_rate_hv']
        elif row['response_rate_census'] == "Could Not Calculate Response Rate":
            yearly_df.at[i,'response_rate_combined'] = row['response_rate_hv']
        else:
            yearly_df.at[i,'response_rate_combined'] = (row['response_rate_hv'] + row['response_rate_census'])/2
            if (abs(row['response_rate_hv'] - row['response_rate_census']) > .05) and (abs(row['response_rate_hv'] - row['response_rate_census']) < .1):
                yearly_df.at[i,'response_rate_confidence'] = "Medium"
            elif (abs(row['response_rate_hv'] - row['response_rate_census']) > .1):
                yearly_df.at[i,'response_rate_confidence'] = "Low"
            else:
                yearly_df.at[i,'response_rate_confidence'] = "High"




    # save compiled data to S3
    upload_obj(yearly_df, BUCKET_NAME, "processed/2021_2022_compiled.csv")
