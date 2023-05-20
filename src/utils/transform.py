import json

import pandas as pd
from google.cloud import storage


def blobs_to_dataframe(
    gcs_client: storage.Client, blobs: list[storage.blob.Blob], keys: list[str]
) -> pd.DataFrame:
    data = []

    for blob in blobs:
        bytes = blob.download_as_bytes(gcs_client)
        object_dict = json.loads(bytes)

        data_object = {}

        for k in keys:
            object_attribute = object_dict.get(k, None)
            data_object[k] = object_attribute

        data.append(data_object)

    data_df = pd.DataFrame(data)

    return data_df
