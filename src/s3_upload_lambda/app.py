import json
import urllib.parse
import boto3
from PIL import Image
from io import BytesIO
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP

s3 = boto3.client('s3')
dynamo_db = boto3.resource('dynamodb')
table = dynamo_db.Table('s3objects')


def create_thumbnail(bucket_name, object_key, thumbnail_bucket, thumbnail_key, 
        size=(128, 128)):
    """
    Create a thumbnail from an image stored in S3 and upload it to another S3 location.

    :param response: s3 object response.
    :param thumbnail_bucket: Destination S3 bucket name for the thumbnail.
    :param thumbnail_key: Key for the thumbnail in the destination bucket.
    :param size: Tuple specifying the thumbnail size (width, height).
    """

    # Download the image from S3
    response = s3.get_object(Bucket=bucket_name, Key=object_key)
    image_data = response['Body'].read()

    # Open the image using Pillow
    with Image.open(BytesIO(image_data)) as img:
        # Create a thumbnail
        img.thumbnail(size)
        
        # Save the thumbnail to an in-memory buffer
        buffer = BytesIO()
        img.save(buffer, format=img.format)
        buffer.seek(0)

        # Upload the thumbnail to the destination bucket
        s3.put_object(
            Bucket=thumbnail_bucket,
            Key=thumbnail_key,
            Body=buffer,
            ContentType=response['ContentType']  # Preserve original content type
        )

    print(f"Thumbnail created and uploaded to s3://{thumbnail_bucket}/{thumbnail_key}")


def lambda_handler(event, context):
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], 
    encoding='utf-8')
    try:
        resp = s3.get_object(Bucket=bucket, Key=key)
        # put object details into dynamodb
        file_type = resp['ContentType']
        file_size = round(int(resp['ContentLength'])/1024.0, 2)
        table.put_item(
            Item={
                'file_name': key,
                'file_type': file_type,
                'file_size':  Decimal(file_size).quantize(Decimal("0.01"),rounding=ROUND_HALF_UP),
                'curr_dt': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            })
        # craete thumbnai
        create_thumbnail(
            bucket_name=bucket,
            object_key=key.replace(" ","_"),
            thumbnail_bucket="aws-devops-project02-dest-bucket",
            thumbnail_key=key,
            size=(128, 128)
        )
        return key
    except Exception as e:
        print(e)
        print('Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.'.format(key, bucket))
        raise e
