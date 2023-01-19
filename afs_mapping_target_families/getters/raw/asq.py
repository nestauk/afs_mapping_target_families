from afs_mapping_target_families import BUCKET_NAME
import pandas as pd
from afs_mapping_target_families.utils.S3.download_excel import download


def get_q1_21_22() -> pd.DataFrame:
    """reads the raw Quarter 1 2021-2022 ASQ data. Disregards 95% CI columns.
    Covers the period of
    source: https://www.gov.uk/government/statistics/child-development-outcomes-at-2-to-2-and-a-half-years-quarterly-data-for-2021-to-2022
    ** data was manually converted to xlsx from ods file prior to upload to S3

    Returns:
        pd.DataFrame: dataframe of raw ASQ Q1 2021-2022 data
    """
    df = download(
        BUCKET_NAME,
        "raw/asq/2021-to-2022-Q4-child-development-data.xlsx",
        kwargs={"sheet_name": "Quarter_1_2021_to_2022", "header": 10},
    )
    drop_cols = [col for col in df.columns if "95% confidence interval" in col]
    return df.drop(columns=drop_cols)


def get_q2_21_22() -> pd.DataFrame:
    """reads the raw Quarter 2 2021-2022 ASQ data. Disregards 95% CI columns.
    source: https://www.gov.uk/government/statistics/child-development-outcomes-at-2-to-2-and-a-half-years-quarterly-data-for-2021-to-2022
    ** data was manually converted to xlsx from ods file prior to upload to S3

    Returns:
        pd.DataFrame: dataframe of raw ASQ Q2 2021-2022 data
    """
    df = download(
        BUCKET_NAME,
        "raw/asq/2021-to-2022-Q4-child-development-data.xlsx",
        kwargs={"sheet_name": "Quarter_2_2021_to_2022", "header": 10},
    )
    drop_cols = [col for col in df.columns if "95% confidence interval" in col]
    return df.drop(columns=drop_cols)


def get_q3_21_22() -> pd.DataFrame:
    """reads the raw Quarter 3 2021-2022 ASQ data. Disregards 95% CI columns.
    source: https://www.gov.uk/government/statistics/child-development-outcomes-at-2-to-2-and-a-half-years-quarterly-data-for-2021-to-2022
    ** data was manually converted to xlsx from ods file prior to upload to S3

    Returns:
        pd.DataFrame: dataframe of raw ASQ Q2 2021-2022 data
    """
    df = download(
        BUCKET_NAME,
        "raw/asq/2021-to-2022-Q4-child-development-data.xlsx",
        kwargs={"sheet_name": "Quarter_3_2021_to_2022", "header": 10},
    )
    drop_cols = [col for col in df.columns if "95% confidence interval" in col]
    return df.drop(columns=drop_cols)


def get_q4_21_22() -> pd.DataFrame:
    """reads the raw Quarter 4 2021-2022 ASQ data. Disregards 95% CI columns.
    source: https://www.gov.uk/government/statistics/child-development-outcomes-at-2-to-2-and-a-half-years-quarterly-data-for-2021-to-2022
    ** data was manually converted to xlsx from ods file prior to upload to S3

    Returns:
        pd.DataFrame: dataframe of raw ASQ Q2 2021-2022 data
    """
    df = download(
        BUCKET_NAME,
        "raw/asq/2021-to-2022-Q4-child-development-data.xlsx",
        kwargs={"sheet_name": "Quarter_4_2021_to_2022", "header": 10},
    )
    drop_cols = [col for col in df.columns if "95% confidence interval" in col]
    return df.drop(columns=drop_cols)
