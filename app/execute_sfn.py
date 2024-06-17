import boto3
import logging
import json
import os

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)
CLIENT = boto3.client("stepfunctions")
SFN_ARN = os.environ.get("SFN_ARN")


def lambda_handler(event, context):
    LOGGER.info(f"Recieved Payload: {event}")
    body = json.loads(event.get("body"))
    payload = {"prompt": body.get("prompt")}
    response = CLIENT.start_execution(
        stateMachineArn=SFN_ARN,
        input=json.dumps(payload),
    )
    print(response)
    return {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Credentials": True,
        },
        "body": json.dumps({"executionArn": response["executionArn"]}),
    }
