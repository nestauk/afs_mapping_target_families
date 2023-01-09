import boto3
import io
import pandas as pd


def download(bucket: str, path_from: str, kwargs) -> pd.DataFrame:
    """downloads an excel file from S3

    Args:
        bucket (str): bucket name
        path_from (str): path to file to load

    Returns:
        pd.DataFrame: pandas dataframe downloaded from S3
    """
    s3 = boto3.client("s3")
    fileobj = io.BytesIO()
    s3.download_fileobj(bucket, path_from, fileobj)
    fileobj.seek(0)
    return pd.read_excel(fileobj, **kwargs)
