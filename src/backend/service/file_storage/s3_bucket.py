"""
Module allowing interaction with S3 Buckets for file uploads, deletion, and reading
"""

from aws_lambda_powertools.logging import Logger
from botocore.exceptions import ClientError

from ..environment import DOCUMENT_STORAGE_BUCKET_READ_ROLE, DOCUMENT_STORAGE_BUCKET_WRITE_ROLE
from ..exceptions import ExternalServiceException, PermissionException, ResourceNotFound
from ..util import AWSAccessLevel, create_client_with_role

logger = Logger()


class S3Bucket:
    """
    Abstraction around an S3 Bucket providing a limited selection of operations on a given bucket.
    """

    def __init__(self, bucket_name: str, access: AWSAccessLevel):
        """
        Initialize a connection to an S3 Bucket

        :param bucket_name: The name of the underlying S3 Bucket in AWS
        :param access: The level of permission desired for this connection
        :return: The S3 Bucket object
        :raises ExternalServiceException: Unable to connect to the S3 Service
        :raises PermissionException: Unable to assume IAM role for required access level
        """
        self.name = bucket_name
        self.access = access

        role_to_assume = DOCUMENT_STORAGE_BUCKET_READ_ROLE
        if access == AWSAccessLevel.WRITE:
            role_to_assume = DOCUMENT_STORAGE_BUCKET_WRITE_ROLE

        self._client = create_client_with_role(service_name="s3", role=role_to_assume)

    def create_upload_url(self, key: str) -> dict:
        """
        Creates a presigned upload url for the specified S3 key

        :param key: The S3 key to create the upload url for
        :return: The presigned upload url
        :raises PermissionException: Assumed role does not have permission to create an
            upload url, due to bucket being initialized with only read permissions
        """
        if self.access != AWSAccessLevel.WRITE:
            # creating presigned URL's is a local operation, so will not get permission
            # errors from S3, instead we try our best to do the permission check here
            raise PermissionException("Creating an upload URL requires write access")
        return self._client.generate_presigned_post(Bucket=self.name, Key=key, Fields={})

    def create_get_url(self, key: str) -> str:
        """
        Creates a presigned get url to get an object from S3

        :param key: The key of the object to get from S3
        :return: The get object presigned url
        """
        return self._client.generate_presigned_url(
            ClientMethod="get_object", Params={"Bucket": self.name, "Key": key}
        )

    def delete(self, key: str, e_tag: str) -> None:
        """
        Delete an object from S3

        :param key: The key of the S3 Object to delete
        :param e_tag: The ETag to match against the object to delete
        :raises ResourceNotFound: The S3 Object exists, but the given ETag does not,
            This means that you are attempting to delete the wrong object
        :raises ExternalServiceException: Unexpected error occurs in S3
        :raises PermissionException: Assumed role does not have permission
            to delete a file, due to bucket being
            initialized with only read permissions
        """
        try:
            self._client.delete_object(Bucket=self.name, Key=key)
        except ClientError as err:
            logger.exception(err)
            if err.response["Error"]["Code"] == "AccessDenied":
                raise PermissionException(
                    "Insufficient permissions to perform delete on the S3 Bucket"
                ) from err
            if err.response["Error"]["Code"] == "PreconditionFailed":
                raise ResourceNotFound(
                    resource_type="file", resource_id=str({"Key": key, "ETag": e_tag})
                ) from err
            raise ExternalServiceException("Unknown Error from AWS") from err
