import os
import json
import boto3
import time
from urllib import request, parse

s3_client = boto3.client('s3')


def test():
    response = {}
    start_time = time.time()

    bucket_id = os.environ['S3_BUCKET_ID']

    blob_object = s3_client.get_object(Bucket=bucket_id, Key='test_file')
    blob_content = blob_object['Body'].read().decode('utf-8')

    load_s3_time = time.time()
    response['load_s3_seconds'] = load_s3_time - start_time

    return response


def handler(event, context):
    body = json.loads(event.get("body", "{}"))
    response_body = {}
    if body.get('test') == True:
        response_body = test()
    else:
        # response_body = {"event": event}
        pass

    return {'statusCode': 200, 'body': json.dumps(response_body)}
