import os
from b2sdk.v2 import B2Api, InMemoryAccountInfo, UploadSourceBytes
from cdn.models import Cloud


def upload_file(file_path, end_file_path, cloud_id):
    if not file_path:
        raise ValueError("Not file_path")
    if not end_file_path:
        raise ValueError("Not end_file_path")
    cloud = Cloud.objects.get(pk=cloud_id)
    info = InMemoryAccountInfo()
    b2_api = B2Api(info)
    b2_api.authorize_account("production", cloud.application_key_id, cloud.application_key)
    bucket = b2_api.get_bucket_by_name(cloud.bucket_name)
    with open(file_path, "rb") as f:
        file_data = f.read()
    upload_source = UploadSourceBytes(file_data)
    uploaded_file = bucket.upload(upload_source, end_file_path)
    return uploaded_file