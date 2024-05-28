import boto3


def before_all(context):
    context.api_key = ""
    context.websocket_api_url = (
        ""
    )
    context.rest_api_url = (
        ""
    )


def after_all(context):
    pass
