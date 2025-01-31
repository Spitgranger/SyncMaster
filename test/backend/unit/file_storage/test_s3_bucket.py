from http import HTTPStatus

import pytest
import requests
from backend.service.environment import DOCUMENT_STORAGE_BUCKET_NAME
from backend.service.file_storage.s3_bucket import S3Bucket
from backend.service.util import AWSAccessLevel
from botocore.exceptions import ClientError

from ..constants import TEST_S3_FILE_CONTENT, TEST_S3_FILE_KEY


def test_upload_file(empty_s3_bucket):
    client = empty_s3_bucket

    # Initialize bucket wrapper
    bucket = S3Bucket(bucket_name=DOCUMENT_STORAGE_BUCKET_NAME, access=AWSAccessLevel.WRITE)

    # Create upload url
    url = bucket.create_upload_url(key=TEST_S3_FILE_KEY)

    # Upload to the url
    http_response = requests.put(url=url, data=TEST_S3_FILE_CONTENT)
    assert http_response.status_code == HTTPStatus.OK.value
    e_tag = http_response.headers["ETag"]

    obj = client.get_object(Bucket=bucket.name, Key=TEST_S3_FILE_KEY, IfMatch=e_tag)
    assert obj["Body"].read() == bytes(TEST_S3_FILE_CONTENT, encoding="utf-8")


def test_get_object_url(s3_bucket_with_item):
    client, metadata = s3_bucket_with_item
    e_tag = metadata["ETag"]

    # Initialize bucket wrapper
    bucket = S3Bucket(bucket_name=DOCUMENT_STORAGE_BUCKET_NAME, access=AWSAccessLevel.READ)

    # Create get url
    url = bucket.create_get_url(key=TEST_S3_FILE_KEY, e_tag=e_tag)

    # Get content from URL
    http_response = requests.get(url=url)
    assert http_response.status_code == HTTPStatus.OK.value
    assert http_response.content == bytes(TEST_S3_FILE_CONTENT, encoding="utf-8")


def test_delete_object(s3_bucket_with_item):
    client, metadata = s3_bucket_with_item
    e_tag = metadata["ETag"]

    # Initialize bucket wrapper
    bucket = S3Bucket(bucket_name=DOCUMENT_STORAGE_BUCKET_NAME, access=AWSAccessLevel.WRITE)

    # Delete object
    bucket.delete(key=TEST_S3_FILE_KEY, e_tag=e_tag)

    with pytest.raises(ClientError) as client_error:
        client.head_object(Bucket=bucket.name, Key=TEST_S3_FILE_KEY, IfMatch=e_tag)

    assert client_error.value.response["Error"]["Code"] == str(HTTPStatus.NOT_FOUND.value)
