import pandas as pd
from nesta_ds_utils.loading_saving.S3 import download_obj
from afs_mapping_target_families import PROJECT_DIR, BUCKET_NAME


def get_la_level(local: str = False) -> pd.DataFrame:
    """gets the local authority level eyfsp data

    Args:
        local (str, optional): True or False to download locally. Defaults to False.

    Returns:
        pd.DataFrame: local level eyfsp data
    """
    if local:
        return pd.read_csv(f"{PROJECT_DIR}/datasets/eyfsp_la_level.csv")
    else:
        return download_obj(
            BUCKET_NAME,
            "processed/eyfsp_la_level.csv",
            download_as="dataframe",
        )


def get_region_level(local: str = False) -> pd.DataFrame:
    """gets the regional level eyfsp data

    Args:
        local (str, optional): True or False to download locally. Defaults to False.

    Returns:
        pd.DataFrame: region level eyfsp data
    """
    if local:
        return pd.read_csv(f"{PROJECT_DIR}/datasets/eyfsp_region_level.csv")
    else:
        return download_obj(
            BUCKET_NAME,
            "processed/eyfsp_region_level.csv",
            download_as="dataframe",
        )


def get_national_level(local: str = False) -> pd.DataFrame:
    """gets the national level eyfsp data

    Args:
        local (str, optional): True or False to download locally. Defaults to False.

    Returns:
        pd.DataFrame: national level eyfsp data
    """
    if local:
        return pd.read_csv(f"{PROJECT_DIR}/datasets/eyfsp_national_level.csv")
    else:
        return download_obj(
            BUCKET_NAME,
            "processed/eyfsp_national_level.csv",
            download_as="dataframe",
        )
