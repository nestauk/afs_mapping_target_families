from nesta_ds_utils.loading_saving.S3 import upload_obj
from afs_mapping_target_families import BUCKET_NAME

if __name__ == "__main__":
    eyfsp_data = get_la_eyfsp()
    eyfsp_data = eyfsp_data[eyfsp_data["geographic_level"] == "Local authority"]

    upload_obj(eyfsp_data, BUCKET_NAME, "processed/eyfsp_la_level.csv")
