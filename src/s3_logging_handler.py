import logging, os
import boto3
from botocore.exceptions import NoCredentialsError
from logging import Handler
from typing import Union

class S3LogHandler(Handler):
    def __init__(self, bucket_name, key_name):
        super().__init__()
        self.bucket_name = bucket_name
        self.key_name = key_name
        self.s3_client = boto3.client('s3')

    def emit(self, record):
        log_entry = self.format(record)
        try:
            response = self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=self.key_name,
                Body=log_entry + '\n'
            )
        except NoCredentialsError:
            print("No AWS credentials found.")

