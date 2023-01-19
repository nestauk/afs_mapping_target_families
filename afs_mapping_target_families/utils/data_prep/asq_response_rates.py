import pandas as pd
from typing import Union


def get_response_rate(asq_data: pd.Series, pop_data: pd.Series) -> Union[int, str]:
    """gets the yearly response rate of quarterly asq data based on census population estimates.
    Response rate is calculated based on fully completed responses (all categories of ASQ)

    Args:
        asq_data (pd.Series): quarterly ASQ data for a local authority
        pop_data (pd.Series): population estimate for children at a certain age as of March 2021

    Returns:
        Union[int, str]: estimated response rate of ASQ
    """
    try:
        return (asq_data["total_overall"].sum()) / pop_data["Population"].iloc[0]
    except:
        return "Could Not Calculate Response Rate"
