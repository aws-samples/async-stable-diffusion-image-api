import boto3
import logging
import os
import json

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)
DYNAMO = boto3.client('dynamodb')
TABLE_NAME = os.environ.get('TABLE_NAME')
CDN_URL = os.environ.get('CDN_URL')

def lambda_handler(event, context):
  scan_params = {
    'TableName': TABLE_NAME,
  }
  # Scan the table
  response = DYNAMO.scan(**scan_params)
  # Retrieve the scanned items
  items = response['Items']
  images = []
  # Process the items as needed
  for item in items:
      # Extract attribute values
      LOGGER.info(item)
      image = {
          "objectUrl": CDN_URL + item['object_key']['S'],
          "prompt": item['prompt']['S'],
          "imageName": item['image_name']['S'],
      }
      images.append(image)

  LOGGER.info(images)
  return {
      'statusCode': 200,
      "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Credentials": True,
      },
      'body': json.dumps({
          'images': images,
      })
  }