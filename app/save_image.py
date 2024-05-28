import base64
import datetime
from io import BytesIO
import json
import boto3
import os
import logging
import uuid

BUCKET_NAME = os.environ.get("BUCKET_NAME", "training-data-bucket-devops-offsite")
TABLE_NAME = os.environ.get("TABLE_NAME", "training-data-table-devops-offsite")
LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)

s3 = boto3.client("s3")
dynamodb = boto3.client("dynamodb")
def lambda_handler(event, context):
    
    LOGGER.info(f"Received event: {event}")
    body = json.loads(event.get("body"))
    generated_image = body.get("generatedImage")
    prompt = body.get("prompt")
    image_name = body.get("imageName")

    LOGGER.info(f"Saving image {image_name} for prompt {prompt}")
    date_time = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    uid = uuid.uuid4()
    object_key = f"images/{date_time}/{uid}/{image_name}.jpg"
    LOGGER.info(f"Saving image to {object_key}")

    s3.put_object(
        Bucket=BUCKET_NAME, 
        Key=object_key, 
        Body=BytesIO(base64.b64decode(generated_image.encode())), 
        ContentType="image/jpeg")
    
    
    # DYNAMO ACTIONS
    LOGGER.info(f"Writing image data to dynamodb for: {image_name}")
    response = dynamodb.put_item(
        TableName=TABLE_NAME,
        Item={
            'id': {'S': str(uid)},
            'prompt': {'S': prompt},
            'image_name': {'S': image_name},
            'object_key': {'S': object_key},
            'date_time': {'S': date_time}
        }
    )
    LOGGER.info(f"DynamoDB response: {response}")
    return {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Credentials": True,
         },
        "body": json.dumps({'id': str(uid)})
    }
    
