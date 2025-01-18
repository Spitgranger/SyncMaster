from http import HTTPStatus

import pytest
import requests
from backend.environment import DOCUMENT_STORAGE_BUCKET_NAME
from backend.file_storage.s3_bucket import S3Bucket
from botocore.exceptions import ClientError

from ..constants import TEST_S3_FILE_CONTENT, TEST_S3_FILE_KEY


@pytest.mark.parametrize("", [pytest.param(id="complete"), pytest.param(id="abort")])
def test_upload_file_completed(empty_s3_bucket, request):
    client = empty_s3_bucket

    # Initialize bucket wrapper
    bucket = S3Bucket(bucket_name=DOCUMENT_STORAGE_BUCKET_NAME, access="write")

    # Start a multipart upload
    upload_id = bucket.start_multipart_upload(key=TEST_S3_FILE_KEY)

    # Create an upload url, for an upload part operation
    url = bucket.create_upload_part_url(key=TEST_S3_FILE_KEY, upload_id=upload_id, part_number=1)

    # Upload to the url
    http_response = requests.put(url=url, data=TEST_S3_FILE_CONTENT)
    assert http_response.status_code == HTTPStatus.OK.value

    if request.node.callspec.id == "complete":
        # Complete the multipart upload
        e_tag = http_response.headers["ETag"]
        final_e_tag = bucket.complete_multipart_upload(
            key=TEST_S3_FILE_KEY, upload_id=upload_id, parts=[{"ETag": e_tag, "PartNumber": 1}]
        )

        obj = client.get_object(Bucket=bucket.name, Key=TEST_S3_FILE_KEY, IfMatch=final_e_tag)
        assert obj["Body"].read() == bytes(TEST_S3_FILE_CONTENT, encoding="utf-8")
    elif request.node.callspec.id == "abort":
        # Abort the multipart upload
        bucket.abort_multipart_upload(key=TEST_S3_FILE_KEY, upload_id=upload_id)

        # Check for existing multipart uploads
        response: dict = client.list_multipart_uploads(Bucket=bucket.name)
        if uploads := response.get("Uploads"):
            for upload in uploads:
                if upload["Key"] == TEST_S3_FILE_KEY and upload["UploadId"] == upload_id:
                    pytest.fail("Found upload still active")


def test_upload_file_aborted(empty_s3_bucket):
    client = empty_s3_bucket

    # Initialize bucket wrapper
    bucket = S3Bucket(bucket_name=DOCUMENT_STORAGE_BUCKET_NAME, access="write")

    # Start a multipart upload
    upload_id = bucket.start_multipart_upload(key=TEST_S3_FILE_KEY)

    # Create an upload url, for an upload part operation
    url = bucket.create_upload_part_url(key=TEST_S3_FILE_KEY, upload_id=upload_id, part_number=1)

    # Upload to the url
    http_response = requests.put(url=url, data=TEST_S3_FILE_CONTENT)
    assert http_response.status_code == HTTPStatus.OK.value

    # Complete the multipart upload
    e_tag = http_response.headers["ETag"]
    final_e_tag = bucket.complete_multipart_upload(
        key=TEST_S3_FILE_KEY, upload_id=upload_id, parts=[{"ETag": e_tag, "PartNumber": 1}]
    )

    obj = client.get_object(Bucket=bucket.name, Key=TEST_S3_FILE_KEY, IfMatch=final_e_tag)
    assert obj["Body"].read() == bytes(TEST_S3_FILE_CONTENT, encoding="utf-8")


def test_get_object_url(s3_bucket_with_item):
    client, metadata = s3_bucket_with_item
    e_tag = metadata["ETag"]

    # Initialize bucket wrapper
    bucket = S3Bucket(bucket_name=DOCUMENT_STORAGE_BUCKET_NAME, access="read")

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
    bucket = S3Bucket(bucket_name=DOCUMENT_STORAGE_BUCKET_NAME, access="write")

    # Delete object
    bucket.delete(key=TEST_S3_FILE_KEY, e_tag=e_tag)

    with pytest.raises(ClientError) as client_error:
        client.head_object(Bucket=bucket.name, Key=TEST_S3_FILE_KEY, IfMatch=e_tag)

    assert client_error.value.response["Error"]["Code"] == str(HTTPStatus.NOT_FOUND.value)
