import boto3
import pytest
from moto import mock_aws
from backend.environment import DOCUMENT_STORAGE_BUCKET_NAME
from io import BytesIO
from ..constants import TEST_S3_FILE_KEY, TEST_S3_FILE_CONTENT


@pytest.fixture()
def empty_s3_bucket():
    with mock_aws():
        # setup
        client = boto3.client("s3")
        client.create_bucket(Bucket=DOCUMENT_STORAGE_BUCKET_NAME)
        client.get_waiter("bucket_exists").wait(Bucket=DOCUMENT_STORAGE_BUCKET_NAME)
        yield client
        # implicit teardown from closing mock_aws

@pytest.fixture()
def s3_bucket_with_item():
    with mock_aws():
        # setup
        client = boto3.client("s3")
        client.create_bucket(Bucket=DOCUMENT_STORAGE_BUCKET_NAME)
        client.get_waiter("bucket_exists").wait(Bucket=DOCUMENT_STORAGE_BUCKET_NAME)
        metadata = client.put_object(Bucket=DOCUMENT_STORAGE_BUCKET_NAME, Key=TEST_S3_FILE_KEY, Body=BytesIO(bytes(TEST_S3_FILE_CONTENT, encoding="utf-8")))
        client.get_waiter("object_exists").wait(Bucket=DOCUMENT_STORAGE_BUCKET_NAME, Key=TEST_S3_FILE_KEY)
        yield client, metadata
        # implicit teardown from closing mock_aws
