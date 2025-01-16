import pytest
import boto3
from moto import mock_aws

@pytest.fixture()
def empty_s3_bucket():
    with mock_aws():
        #setup
        client = boto3.client("s3")
        client.create_bucket(Bucket="test_document_bucket")
        client.get_waiter('bucket_exists').wait(Bucket="test_document_bucket")
        yield client
        #teardown
        paginator = client.get_paginator('list_objects_v2')
        for response in paginator.paginate(Bucket="test_document_bucket"):
            keys = [object["Key"] for object in response["Contents"]]
            for key in keys:
                try:
                    client.delete_object(Bucket="test_document_bucket", Key=key)
                except Exception as e:
                    continue
        client.delete_bucket(Bucket="test_document_bucket")
        client.get_waiter('bucket_not_exists').wait(Bucket="test_document_bucket")

