"""
Module allowing interaction with S3 Buckets for file uploads, deletion, and reading
"""

from ..environment import DOCUMENT_STORAGE_BUCKET_READ_ROLE, DOCUMENT_STORAGE_BUCKET_WRITE_ROLE
from ..util import AWSAccessLevel, create_client_with_role


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

    def create_upload_url(self, key: str) -> str:
        """
        Creates a presigned upload url for the specified S3 key

        :param key: The S3 key to create the upload url for
        :return: The presigned upload url
        :raises ExternalServiceException: Unexpected error occurs in S3
        :raises PermissionException: Assumed role does not have permission to create an
            upload url, likely due to bucket being initialized with only read permissions
        """
        url = self._client.generate_presigned_url(
            ClientMethod="put_object",
            Params={
                "Bucket": self.name,
                "Key": key,
            },
        )
        return url

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
