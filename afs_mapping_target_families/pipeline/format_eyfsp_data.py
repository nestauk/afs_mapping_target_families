from nesta_ds_utils.loading_saving.S3 import upload_obj
from afs_mapping_target_families import BUCKET_NAME, PROJECT_DIR
from afs_mapping_target_families.getters.raw.eyfsp import get_raw_eyfsp

if __name__ == "__main__":
    eyfsp_data = get_raw_eyfsp()
    la_level = eyfsp_data[eyfsp_data["geographic_level"] == "Local authority"]
    region_level = eyfsp_data[eyfsp_data["geographic_level"] == "Regional"]
    national_level = eyfsp_data[eyfsp_data["geographic_level"] == "National"]

    upload_obj(la_level, BUCKET_NAME, "processed/eyfsp_la_level.csv")
    upload_obj(region_level, BUCKET_NAME, "processed/eyfsp_regional_level.csv")
    upload_obj(national_level, BUCKET_NAME,
               "processed/eyfsp_national_level.csv")

    la_level.to_csv(f"{PROJECT_DIR}/datasets/eyfsp_la_level.csv")
    region_level.to_csv(f"{PROJECT_DIR}/datasets/eyfsp_region_level.csv")
    national_level.to_csv(f"{PROJECT_DIR}/datasets/eyfsp_national_level.csv")
