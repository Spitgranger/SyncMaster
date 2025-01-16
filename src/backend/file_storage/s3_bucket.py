from __future__ import annotations

import boto3

from ..environment import DOCUMENT_STORAGE_BUCKET_READ_ROLE, DOCUMENT_STORAGE_BUCKET_WRITE_ROLE


class S3Bucket:
    def __init__(self, bucket_name: str, access: str) -> S3Bucket:
        """
        Initialize a connection to an S3 Bucket

        :param bucket_name: The name of the underlying S3 Bucket in AWS
        :param access: The level of permission desired for this connection
        :return: The S3 Bucket object
        :raises ExternalServiceException: Unable to connect to the S3 Service
        :raises IAMPermissionError: Unable to assume IAM role for required access level
        """
        self.name = bucket_name
        self.access = access

        role_to_assume = None
        if access == "read":
            role_to_assume = DOCUMENT_STORAGE_BUCKET_READ_ROLE
        elif access == "write":
            role_to_assume = DOCUMENT_STORAGE_BUCKET_WRITE_ROLE

        assumed_role_object = boto3.client("sts").assume_role(
            RoleArn=role_to_assume, RoleSessionName="SyncMasterRoleSession"
        )
        self._creds: dict = assumed_role_object["Credentials"]

        self._client = boto3.client(
            "s3",
            aws_access_key_id=self._creds["AccessKeyId"],
            aws_secret_access_key=self._creds["SecretAccessKey"],
            aws_session_token=self._creds["SessionToken"],
        )

    def create_upload_url(self, key: str) -> tuple[str, dict]:
        response = self._client.generate_presigned_post(Bucket=self.name, Key=key)
        return response["url"], response["fields"]

    def create_get_url(self, key: str) -> str:
        url = self._client.generate_presigned_url(
            ClientMethod="get_object", Params={"Bucket": self.name, "Key": key}
        )
        return url

    def delete(self, key: str) -> str:
        self._client.delete_object(Bucket=self.name, Key=key)
