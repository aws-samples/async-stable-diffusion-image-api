import boto3
import logging
import os
import time
import json
import uuid

TABLE_NAME = os.environ.get("TABLE_NAME", "image-conneciton-table")
LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)


def lambda_handler(event, context):
    """
    This function stores the websocket connection id in DynamoDB for 5 minutes.
    :param event: payload from the API Gateway with the state machine execution arn and websocket connection ID.
    :param context: lambda context
    :return: response with the execution arn
    """
    LOGGER.info(event)
    event_body = json.loads(event.get("body"))
    LOGGER.info(event_body)
    exec_arn = event_body.get("data").get("executionArn")
    connection_id = event.get("requestContext").get("connectionId")
    fmt_date_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    expire_at = int(time.time()) + 300  # 5 minute TTL
    uid = uuid.uuid4()

    # DYNAMO ACTIONS
    LOGGER.info(f"Writing image data to dynamodb for: {exec_arn}: {connection_id}")
    response = put_item(uid, exec_arn, connection_id, fmt_date_time, expire_at)
    return {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Credentials": True,
        },
        "body": json.dumps({"message": "success"}),
    }


def put_item(uid, exec_arn, connection_id, fmt_date_time, expire_at, client=None):
    client = client if client else boto3.client("dynamodb")
    # DYNAMO ACTIONS
    LOGGER.info(f"Writing image data to dynamodb for: {exec_arn}: {connection_id}")
    response = client.put_item(
        TableName=TABLE_NAME,
        Item={
            "id": {"S": str(uid)},
            "executionArn": {"S": exec_arn},
            "connectionId": {"S": connection_id},
            "date_time": {"S": fmt_date_time},
            "expire_at": {"N": str(expire_at)},
        },
    )
    LOGGER.info("Write Success!")
    return response
