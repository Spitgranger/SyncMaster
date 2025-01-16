"""
Environment variables passed in from AWS Lambda
"""

from os import getenv

DOCUMENT_STORAGE_BUCKET_NAME = getenv("DOCUMENT_STORAGE_BUCKET_NAME", "test_document_bucket")
# Name of the bucket used for storing documents

DOCUMENT_STORAGE_BUCKET_READ_ROLE = getenv(
    "DOCUMENT_STORAGE_BUCKET_READ_ROLE", "arn:aws:iam::123456789012:role/document_s3_write_role"
)
# Role used for reading from the document storage bucket

DOCUMENT_STORAGE_BUCKET_WRITE_ROLE = getenv(
    "DOCUMENT_STORAGE_BUCKET_WRITE_ROLE", "arn:aws:iam::123456789012:role/document_s3_write_role"
)
# Role used for writing to the document storage bucket
