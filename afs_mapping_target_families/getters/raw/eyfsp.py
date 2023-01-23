from afs_mapping_target_families import BUCKET_NAME
from nesta_ds_utils.loading_saving.S3 import download_obj
import pandas as pd


def get_raw_eyfsp() -> pd.DataFrame:
    """gets the raw 2021/2022 EYFSP results.
        Raw data was downloaded from the table '1 Headline measures by characteristics' found here:
        https://explore-education-statistics.service.gov.uk/data-catalogue/early-years-foundation-stage-profile-results/2021-22"

    Returns:
        pd.DataFrame: raw 2021/2022 EYFSP results
    """

    return download_obj(
        BUCKET_NAME,
        "raw/eyfsp/1_eyfsp_headline_measures_2022.csv",
        download_as="dataframe",
    )


def get_la_gld() -> pd.DataFrame():
    """gets a summary of good level of development percentage by local authority from the 2021/2022 EYFSP

    Returns:
        pd.DataFrame: summary of gld by la for 2021/2022 EYFSP
    """
    raw_eyfsp = get_raw_eyfsp()

    return raw_eyfsp.loc[
        (raw_eyfsp["geographic_level"] == "Local authority")
        & (raw_eyfsp["characteristic"] == "Total")
        & (raw_eyfsp["characteristic_type"] == "Total")
        & (raw_eyfsp["gender"] == "Total")
    ][["la_name", "gld_percentage"]]
