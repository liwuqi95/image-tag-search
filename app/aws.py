import boto3
from datetime import datetime, timedelta
import os
from app import app
import pytz

s3 = boto3.resource('s3',
                    aws_access_key_id='AKIAIBS34MHIN5U5W24A',
                    aws_secret_access_key='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',
                    region_name='us-east-1')

cl = boto3.client('s3',
                  aws_access_key_id='AKIAIBS34MHIN5U5W24A',
                  aws_secret_access_key='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',
                  region_name='us-east-1')

bucket = s3.Bucket('ece1779projecta3bucket')

db = boto3.resource('dynamodb',
                    aws_access_key_id='AKIAIBS34MHIN5U5W24A',
                    aws_secret_access_key='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',
                    region_name='us-east-1')

db_client = boto3.client('dynamodb',
                         aws_access_key_id='AKIAIBS34MHIN5U5W24A',
                         aws_secret_access_key='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',
                         region_name='us-east-1')


def move_to_s3(image, key):
    """store image to s3"""

    bucket.upload_fileobj(image, 'images/' + key)

    print("Moved to s3")


def get_db():
    return db


def get_db_client():
    return db_client


def list_objects():
    """list all the s3 objects"""
    res = cl.list_objects(Bucket='ece1779projecta3bucket')
    if 'Contents' not in res.keys(): return None
    return [{'Key': obj['Key']} for obj in res['Contents']]


def clear_s3():
    """clear s3 """
    objects = list_objects()
    if objects is not None:
        bucket.delete_objects(Delete={'Objects': objects})


if __name__ == "__main__":
    pass
