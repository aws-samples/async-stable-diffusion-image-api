import boto3
import os
import logging
import botocore

LOGGER = logging.getLogger()

def before_all(context):
    try:
        boto3.client('sagemaker').describe_endpoint(
    		EndpointName='test'
		)
        context.endpoint_exists = True
    except botocore.exceptions.ClientError:
        context.endpoint_exists = False
        raise
        
        
    client = boto3.client('apigateway')
    context.api_key = client.get_api_key(apiKey=os.environ.get('API_KEY_ID'), includeValue=True)['value']
    context.websocket_api_url = (
       f"wss://{os.environ.get('WSS_API_ID')}.execute-api.us-east-1.amazonaws.com/prod/"
    )
    context.rest_api_url = (
        f"https://{os.environ.get('REST_API_ID')}.execute-api.us-east-1.amazonaws.com/prod/"
    )


def after_all(context):
    if context.endpoint_exists:
        dynamo_client = boto3.client("dynamodb")
