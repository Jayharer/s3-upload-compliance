import json
import urllib.parse
import boto3
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP

s3 = boto3.client('s3')
dynamo_db = boto3.resource('dynamodb')
table = dynamo_db.Table('s3objects')


def lambda_handler(event, context):
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    try:
        resp = s3.get_object(Bucket=bucket, Key=key)
        print("resp", resp)
        file_type = resp['ContentType']
        file_size = round(int(resp['ContentLength'])/1024.0, 2)
        print(key, file_type, file_size)
        table.put_item(
            Item={
                'file_name': key,
                'file_type': file_type,
                'file_size':  Decimal(file_size).quantize(Decimal("0.01"),rounding=ROUND_HALF_UP),
                'curr_dt': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            })
        return key
    except Exception as e:
        print(e)
        print('Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.'.format(key, bucket))
        raise e
