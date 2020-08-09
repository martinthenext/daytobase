import os
import json
import boto3
import time
from urllib import request, parse

s3_client = boto3.client('s3')


def handler(event, context):

    response_body = {}
    start_time = time.time()

    # body = json.loads(event["body"])
    # print("Body")
    # print(body)

    # chat_id = body["message"]["chat"]["id"]
    # text = body["message"]["text"]

    # token = os.environ.get('TELEGRAM_TOKEN')
    # send_url = f"https://api.telegram.org/bot{token}/sendMessage"

    # data = {"chat_id": chat_id, "text": f"You said {text}"}
    # data_encoded = parse.urlencode(data).encode()
    # req =  request.Request(send_url, data=data_encoded)
    # resp = request.urlopen(req)


    # s3_client.download_file('buckit-604f47116c162f31', 'iris.csv', '/tmp/iris.csv')
    blob_object = s3_client.get_object(Bucket='buckit-604f47116c162f31', Key='daytobase.test.s3.csv')
    # blob_content = json.loads(blob_object['Body'].read().decode('utf-8'))
    blob_content = blob_object['Body'].read().decode('utf-8')
    # response_body['blob_content'] = blob_content

    load_s3_time = time.time()
    response_body['load_s3_seconds'] = load_s3_time - start_time

    # bla = ''
    # with open('/tmp/iris.csv', 'r') as f:
    #     bla = f.read()

    # file_read_and_parse_time = time.time()
    # response_body['file_read_and_parse_seconds'] = file_read_and_parse_time - load_s3_time

    return {
        'statusCode': 200,
        # 'body': json.dumps({'yo': bla}),
        'body': json.dumps(
            response_body
        ),
    }
