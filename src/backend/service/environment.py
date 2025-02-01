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

TARGET_LATITUDE = float(getenv("TARGET_LATITUDE", "43.2588581564085"))
TARGET_LONGITUDE = float(getenv("TARGET_LONGITUDE", "-79.92097591189501"))
# Coordinates for ITB

ACCEPTABLE_RADIUS_METERS = int(getenv("ACCEPTABLE_RADIUS_METERS", "100"))
# radius in which location accepted
