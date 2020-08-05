import os
import json
from urllib import request, parse

def handler(event, context):
    body = json.loads(event["body"])
    print("Body")
    print(body)

    chat_id = body["message"]["chat"]["id"]
    text = body["message"]["text"]

    token = os.environ.get('TELEGRAM_TOKEN')
    send_url = f"https://api.telegram.org/bot{token}/sendMessage"

    data = {"chat_id": chat_id, "text": f"You said {text}"}
    data_encoded = parse.urlencode(data).encode()
    req =  request.Request(send_url, data=data_encoded)
    resp = request.urlopen(req)

    return {
        'statusCode': 200,
        'body': json.dumps({}),
    }
