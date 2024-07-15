import boto3
import logging
import os
from boto3.dynamodb.conditions import Key

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)
API_ID = os.getenv("API_ID")
TABLE_NAME = os.environ.get("TABLE_NAME", "image-conneciton-table")


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
    query_condition = Key("executionArn").eq(execution_arn)
    response = query_table(query_condition)
    print(response)
    connection = response.get("Items")[0]["connectionId"]

    LOGGER.info(response)
    LOGGER.info(API_ID)
    api_url = f"https://{API_ID}.execute-api.us-east-1.amazonaws.com/prod"
    response = post_to_connection(body, connection, api_url)
    LOGGER.info(f"Success! {response}")
    return response


def query_table(query_condition, resource=None):
    resource = resource if resource else boto3.resource("dynamodb")
    table = resource.Table(TABLE_NAME)
    return table.query(KeyConditionExpression=query_condition)


def post_to_connection(body, connection, api_url, client=None):
    client = (
        client
        if client
        else boto3.client("apigatewaymanagementapi", endpoint_url=api_url)
    )
    return client.post_to_connection(Data=body, ConnectionId=connection)
