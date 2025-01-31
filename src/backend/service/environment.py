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

JOB_TABLE_NAME = getenv("JOB_TABLE_NAME", "")
# Name of the table used to store job info

JOB_TABLE_READ_ROLE = getenv("JOB_TABLE_READ_ROLE", "")
# Role used for reading from the job table

JOB_TABLE_WRITE_ROLE = getenv("JOB_TABLE_WRITE_ROLE", "")
# Role used for writing to the job table
