import pandas as pd
from afs_mapping_target_families import PROJECT_DIR, BUCKET_NAME


def get_la_level() -> pd.DataFrame:
    """gets the local authority level eyfsp data

    Returns:
        pd.DataFrame: local level eyfsp data
    """
    return pd.read_csv(f"{PROJECT_DIR}/datasets/eyfsp_la_level.csv")


def get_region_level() -> pd.DataFrame:
    """gets the regional level eyfsp data

    Returns:
        pd.DataFrame: region level eyfsp data
    """
    return pd.read_csv(f"{PROJECT_DIR}/datasets/eyfsp_region_level.csv")


def get_national_level(local: str = False) -> pd.DataFrame:
    """gets the national level eyfsp data

    Returns:
        pd.DataFrame: national level eyfsp data
    """
    return pd.read_csv(f"{PROJECT_DIR}/datasets/eyfsp_national_level.csv")
