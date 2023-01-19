from afs_mapping_target_families import BUCKET_NAME
from nesta_ds_utils.loading_saving.S3 import download_obj
import pandas as pd


def get_pop_age_1() -> pd.DataFrame:
    """get population estimates of children at age 1 as of March 21, 2021 by upper tier local authorities
    source: https://www.ons.gov.uk/datasets/TS007/editions/2021/versions/1

    Returns:
        pd.DataFrame: population estimates of children at age 1 by upper tier LA
    """
    df = download_obj(
        BUCKET_NAME,
        "raw/population_estimates/age_by_single_year.csv",
        download_as="dataframe",
    )
    return (
        df[df["Age (101 categories)"] == "Aged 1 year"]
        .drop(columns=["Age (101 categories) Code", "Age (101 categories)"])
        .rename(columns={"Observation": "Population"})
    )


def get_pop_age_2() -> pd.DataFrame:
    """get population estimates of children at age 2 as of March 21, 2021 by upper tier local authorities
    source: https://www.ons.gov.uk/datasets/TS007/editions/2021/versions/1

    Returns:
        pd.DataFrame: population estimates of children at age 2 by upper tier LA
    """
    df = download_obj(
        BUCKET_NAME,
        "raw/population_estimates/age_by_single_year.csv",
        download_as="dataframe",
    )
    return (
        df[df["Age (101 categories)"] == "Aged 2 years"]
        .drop(columns=["Age (101 categories) Code", "Age (101 categories)"])
        .rename(columns={"Observation": "Population"})
    )
