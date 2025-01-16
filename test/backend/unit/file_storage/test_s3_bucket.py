from backend.file_storage.s3_bucket import S3Bucket
import requests
from http import HTTPStatus

def test_create_upload_url(empty_s3_bucket):
    bucket = S3Bucket(bucket_name="test_document_bucket", access="write")
    url, fields = bucket.create_upload_url("hello.txt")
    http_response = requests.post(url=url, data=fields, files={"file": ("hello.txt", "Hello, World")})
    assert http_response.status_code == HTTPStatus.NO_CONTENT.value
    print(http_response.headers)

