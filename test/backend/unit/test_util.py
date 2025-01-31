from unittest.mock import patch

import boto3
import pytest
from backend.service.environment import (
    DOCUMENT_STORAGE_BUCKET_READ_ROLE,
    DOCUMENT_STORAGE_BUCKET_WRITE_ROLE,
)
from backend.service.exceptions import ExternalServiceException, PermissionException
from backend.service.util import create_client_with_role
from botocore.stub import Stubber
from moto import mock_aws


def test_create_client_with_role():
    with mock_aws():
        client = create_client_with_role("sts", DOCUMENT_STORAGE_BUCKET_READ_ROLE)
        arn: str = client.get_caller_identity()["Arn"]
        assert arn.rsplit(sep="/", maxsplit=1)[1] == "SyncMasterRoleSession"


@pytest.mark.parametrize(
    "aws_error_code, expected_error_class",
    [
        pytest.param("InternalError", ExternalServiceException, id="AWS Error"),
        pytest.param("AccessDenied", PermissionException, id="Incorrect Permissions"),
    ],
)
def test_create_client_with_role_errors(aws_error_code, expected_error_class):
    with mock_aws():
        client = boto3.client("sts")
        stubber = Stubber(client)
        stubber.add_client_error("assume_role", service_error_code=aws_error_code)
        patcher = patch("boto3.client", return_value=client)
        with patcher, stubber, pytest.raises(expected_error_class):
            create_client_with_role("sts", DOCUMENT_STORAGE_BUCKET_WRITE_ROLE)
