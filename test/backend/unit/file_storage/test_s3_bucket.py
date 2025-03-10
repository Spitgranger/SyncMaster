import io
from http import HTTPStatus

import pytest
import requests
from backend.service.environment import DOCUMENT_STORAGE_BUCKET_NAME
from backend.service.exceptions import (
    ExternalServiceException,
    PermissionException,
    ResourceNotFound,
)
from backend.service.file_storage.s3_bucket import S3Bucket
from backend.service.util import AWSAccessLevel
from botocore.exceptions import ClientError
from botocore.stub import Stubber

from ..constants import TEST_S3_FILE_CONTENT, TEST_S3_FILE_KEY


def test_upload_file(empty_s3_bucket):
    client = empty_s3_bucket

    # Initialize bucket wrapper
    bucket = S3Bucket(bucket_name=DOCUMENT_STORAGE_BUCKET_NAME, access=AWSAccessLevel.WRITE)

    # Create upload url
    url = bucket.create_upload_url(key=TEST_S3_FILE_KEY)

    # Upload to the url
    f = io.StringIO(TEST_S3_FILE_CONTENT)
    files = {"file": (TEST_S3_FILE_CONTENT, f)}
    http_response = requests.post(url["url"], data=url["fields"], files=files)
    assert http_response.status_code == HTTPStatus.NO_CONTENT.value

    obj = client.get_object(Bucket=bucket.name, Key=TEST_S3_FILE_KEY)
    assert obj["Body"].read() == bytes(TEST_S3_FILE_CONTENT, encoding="utf-8")


def test_upload_file_permission_error(empty_s3_bucket):
    client = empty_s3_bucket

    # Initialize bucket wrapper
    bucket = S3Bucket(bucket_name=DOCUMENT_STORAGE_BUCKET_NAME, access=AWSAccessLevel.READ)

    with pytest.raises(PermissionException):
        # Create upload url failure
        bucket.create_upload_url(key=TEST_S3_FILE_KEY)


def test_get_object_url(s3_bucket_with_item):
    client, metadata = s3_bucket_with_item
    e_tag = metadata["ETag"]

    # Initialize bucket wrapper
    bucket = S3Bucket(bucket_name=DOCUMENT_STORAGE_BUCKET_NAME, access=AWSAccessLevel.READ)

    # Create get url
    url = bucket.create_get_url(key=TEST_S3_FILE_KEY)

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


@pytest.mark.parametrize(
    "aws_error_code, expected_error_class",
    [
        pytest.param("PreconditionFailed", ResourceNotFound, id="Etag Mismatch"),
        pytest.param("InternalError", ExternalServiceException, id="AWS Error"),
        pytest.param("AccessDenied", PermissionException, id="Incorrect Permissions"),
    ],
)
def test_delete_object_with_errors(s3_bucket_with_item, aws_error_code, expected_error_class):
    client, metadata = s3_bucket_with_item
    e_tag: str = metadata["ETag"]

    # Initialize bucket wrapper
    bucket = S3Bucket(bucket_name=DOCUMENT_STORAGE_BUCKET_NAME, access=AWSAccessLevel.WRITE)

    stubber = Stubber(bucket._client)
    stubber.add_client_error(method="delete_object", service_error_code=aws_error_code)
    with stubber:
        # Delete object failure
        with pytest.raises(expected_error_class):
            print(bucket.delete(key=TEST_S3_FILE_KEY, e_tag=e_tag))
