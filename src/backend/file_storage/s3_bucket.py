"""
Module allowing interaction with S3 Buckets for file uploads, deletion, and reading
"""

import boto3

from ..environment import DOCUMENT_STORAGE_BUCKET_READ_ROLE, DOCUMENT_STORAGE_BUCKET_WRITE_ROLE


class S3Bucket:
    """
    Abstraction around an S3 Bucket providing a limited selection of operations on a given bucket.
    """

    def __init__(self, bucket_name: str, access: str):
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

        assumed_role_object: dict = boto3.client("sts").assume_role(
            RoleArn=role_to_assume, RoleSessionName="SyncMasterRoleSession"
        )
        self._creds: dict = assumed_role_object["Credentials"]

        self._client = boto3.client(
            "s3",
            aws_access_key_id=self._creds["AccessKeyId"],
            aws_secret_access_key=self._creds["SecretAccessKey"],
            aws_session_token=self._creds["SessionToken"],
        )

    def start_multipart_upload(self, key: str) -> str:
        """
        Initiates a multipart upload and creates an upload ID

        :param key: The S3 key to initiate the multipart upload for
        :return: The upload ID of the new multipart upload
        :raises ExternalServiceException: Unexpected error occurs in S3
        :raises PermissionException: Assumed role does not have permission to start a multipart
            upload, likely due to bucket being initialized with only read permissions
        """
        response: dict = self._client.create_multipart_upload(Bucket=self.name, Key=key)
        upload_id: str = response["UploadId"]
        return upload_id

    def create_upload_part_url(self, key: str, upload_id: str, part_number: int) -> str:
        """
        Creates a presigned URL for the UI to upload a part of the
        initialized multipart upload to the S3 Bucket

        :param key: The S3 key that this upload is going to
        :param upload_id: The id of the initialized multipart upload
        :param part_number: The part number of the part being uploaded, indexing from 1-10,000
        :return: The presigned url to upload the part to S3
        :raises UploadNotFound: The multipart upload with the given id could not be found
        :raises ExternalServiceException: Unexpected error occurs in S3
        :raises PermissionException: Assumed role does not have permission to make an upload url,
            likely due to bucket being initialized with only read permissions
        """
        url: str = self._client.generate_presigned_url(
            ClientMethod="upload_part",
            Params={
                "Bucket": self.name,
                "Key": key,
                "UploadId": upload_id,
                "PartNumber": part_number,
            },
        )
        return url

    def complete_multipart_upload(self, key: str, upload_id: str, parts: list[dict]) -> str:
        """
        Completes an existing multipart upload

        :param key: The S3 key that this upload is going to
        :param upload_id: The id of the initialized multipart upload
        :param parts: A list of dictionaries of containing metadata of the completed upload parts.
            The dictionaries should be formatted as:
            ```
            {
                "ETag": str
                "PartNumber": int
            }
            ```
        :return: The ETag of the new S3 Object
        :raises UploadNotFound: The multipart upload with the given id could not be found
        :raises ExternalServiceException: Unexpected error occurs in S3
        :raises PermissionException: Assumed role does not have permission
            to complete a multipart upload, likely due to bucket being
            initialized with only read permissions
        """
        response: dict = self._client.complete_multipart_upload(
            Bucket=self.name, Key=key, MultipartUpload={"Parts": parts}, UploadId=upload_id
        )
        e_tag: str = response["ETag"]
        return e_tag

    def abort_multipart_upload(self, key: str, upload_id: str) -> None:
        """
        Aborts an existing multipart upload

        :param key: The S3 key that this upload is going to
        :param upload_id: The id of the initialized multipart upload
        :raises UploadNotFound: The multipart upload with the given id could not be found
        :raises ExternalServiceException: Unexpected error occurs in S3
        :raises PermissionException: Assumed role does not have permission
            to abort a multipart upload, likely due to bucket being
            initialized with only read permissions
        """
        self._client.abort_multipart_upload(Bucket=self.name, Key=key, UploadId=upload_id)

    def create_get_url(self, key: str, e_tag: str) -> str:
        """
        Creates a presigned get url to get an object from S3

        :param key: The key of the object to get from S3
        :param e_tag: The e_tag to match when getting the object
        :return: The get object presigned url
        :raises ExternalServiceException: Unexpected error occurs in S3
        """
        url = self._client.generate_presigned_url(
            ClientMethod="get_object", Params={"Bucket": self.name, "Key": key, "IfMatch": e_tag}
        )
        return url

    def delete(self, key: str, e_tag: str) -> None:
        """
        Delete an object from S3

        :param key: The key of the S3 Object to delete
        :param e_tag: The ETag to match against the object to delete
        :raises FileNotFound: The S3 Object with the given key, and ETag could not be found
        :raises ExternalServiceException: Unexpected error occurs in S3
        :raises PermissionException: Assumed role does not have permission
            to delete a file, likely due to bucket being
            initialized with only read permissions
        """
        self._client.delete_object(Bucket=self.name, Key=key, IfMatch=e_tag)
