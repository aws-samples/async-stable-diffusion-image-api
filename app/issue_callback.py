import boto3
import logging
import os
from boto3.dynamodb.conditions import Key

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)
API_ID = os.getenv("API_ID")
TABLE_NAME = os.environ.get("TABLE_NAME", "image-conneciton-table")
DYNAMO = boto3.resource("dynamodb")


def lambda_handler(event, context):
    """
    Function responsible for sending the generated imafe data to the an open Websocket API connection.
    This function will retrieve a connection id to callback to by querying the DynamoDB table for the provided State Machine execution arn.

    :param event: payload containing the encoded image data to be posted to an open websocket connection.
    :param context: lambda context
    :return: response with the execution arn
    """
    LOGGER.info(f"Recieved Event: {event}")
    body = event.get("payload").get("body")
    execution_arn = event.get("executionArn")
    table = DYNAMO.Table(TABLE_NAME)
    response = table.query(KeyConditionExpression=Key("executionArn").eq(execution_arn))
    connection = response.get("Items")[0]["connectionId"]

    LOGGER.info(response)
    LOGGER.info(API_ID)
    api_url = f"https://{API_ID}.execute-api.us-east-1.amazonaws.com/prod"
    apiManagement = boto3.client("apigatewaymanagementapi", endpoint_url=api_url)
    response = apiManagement.post_to_connection(Data=body, ConnectionId=connection)
    LOGGER.info(f"Success! {response}")
