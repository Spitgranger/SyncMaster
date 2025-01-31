"""
Environment variables passed in from AWS Lambda
"""

from os import getenv

DOCUMENT_STORAGE_BUCKET_NAME = getenv("DOCUMENT_STORAGE_BUCKET_NAME", "")
# Name of the bucket used for storing documents

DOCUMENT_STORAGE_BUCKET_READ_ROLE = getenv("DOCUMENT_STORAGE_BUCKET_READ_ROLE", "")
# Role used for reading from the document storage bucket

DOCUMENT_STORAGE_BUCKET_WRITE_ROLE = getenv("DOCUMENT_STORAGE_BUCKET_WRITE_ROLE", "")
# Role used for writing to the document storage bucket

TABLE_NAME = getenv("TABLE_NAME", "")
# Name of the DB table used to store job info

TABLE_READ_ROLE = getenv("TABLE_READ_ROLE", "")
# Role used for reading from the DB table

TABLE_WRITE_ROLE = getenv("TABLE_WRITE_ROLE", "")
# Role used for writing to the DB table
