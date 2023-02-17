from nesta_ds_utils.loading_saving.S3 import download_obj
from afs_mapping_target_families import BUCKET_NAME
import pandas as pd


def get_combined_data() -> pd.DataFrame():
    """
    Retrieves aggregated quarterly data with census data created in pipeline/asq/aggregate_quarterly_data.py
    """
    return download_obj(
        BUCKET_NAME, "processed/2021_2022_compiled_v2.csv", download_as="dataframe"
    )
