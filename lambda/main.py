import os
import json

def handler(event, context):
    return_body = {
        'env': os.environ.__repr__(),
        'TELEGRAM_TOKEN': os.environ.get('TELEGRAM_TOKEN')
    }
    return {
        'statusCode': 200,
        'body': json.dumps(return_body)
    }
