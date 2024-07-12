import boto3
import logging
import json
import os

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)
SFN_ARN = os.environ.get("SFN_ARN")


def lambda_handler(event, context):
    """
    Function responsible for starting the step function execution.
    :param event: payload from the API Gateway with the prompt to be sent to the model.
    :param context: lambda context
    :return: response with the execution arn
    """
    LOGGER.info(f"Recieved Payload: {event}")
    if not event.get("body"):
        return build_error_response(
            400, "Missing required field 'body' in the request body"
        )
    body = json.loads(event.get("body"))

    if not body.get("prompt"):
        return build_error_response(
            400, "Missing required field 'prompt' in the request body"
        )

    payload = {"prompt": body.get("prompt")}
    response = start_execution(SFN_ARN, payload)
    return {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Credentials": True,
        },
        "body": json.dumps({"executionArn": response["executionArn"]}),
    }


def start_execution(sfn_arn, payload, client=None):
    client = client if client else boto3.client("stepfunctions")
    response = client.start_execution(
        stateMachineArn=sfn_arn,
        input=json.dumps(payload),
    )
    return response


def build_error_response(status_code, error_message):
    return {
        "statusCode": status_code,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Credentials": True,
        },
        "body": json.dumps({"error": error_message}),
    }
