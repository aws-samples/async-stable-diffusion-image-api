import boto3
import logging
import os
import datetime
import json
import uuid

TABLE_NAME = os.environ.get("TABLE_NAME", "image-conneciton-table")
LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)

dynamodb = boto3.client("dynamodb")
def lambda_handler(event, context):
    LOGGER.info(event)
    event_body = json.loads(event.get("body"))
    LOGGER.info(event_body)
    exec_arn = event_body.get("data").get("executionArn")
    connection_id = event.get("requestContext").get("connectionId")
    date_time = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    uid = uuid.uuid4()

    # DYNAMO ACTIONS
    LOGGER.info(f"Writing image data to dynamodb for: {exec_arn}: {connection_id}")
    dynamodb.put_item(
        TableName=TABLE_NAME,
        Item={
            'id': {'S': str(uid)},
            "executionArn": {'S': exec_arn},
            'connectionId': {'S': connection_id},
            'date_time': {'S': date_time}
        }
    )
    LOGGER.info("Write Success!")

    return {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Credentials": True,
         },
        "body": json.dumps({'message': 'success'})
    }