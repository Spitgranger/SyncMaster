from http import HTTPStatus

import requests
from backend.file_storage.s3_bucket import S3Bucket


def test_upload_file(empty_s3_bucket):
    bucket = S3Bucket(bucket_name="test_document_bucket", access="write")
    upload_id = bucket.start_multipart_upload(key="hello.txt")
    url = bucket.create_upload_part_url(key="hello.txt", upload_id=upload_id, part_number=1)
    http_response = requests.put(url=url, data="Hello World")
    assert http_response.status_code == HTTPStatus.OK.value
    e_tag = http_response.headers["ETag"]
    bucket.complete_multipart_upload(
        key="hello.txt", upload_id=upload_id, parts=[{"ETag": e_tag, "PartNumber": 1}]
    )
