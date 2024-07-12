import json
import os
import boto3
from botocore.response import StreamingBody

ENDPOINT = os.getenv("ENDPOINT_NAME", "jumpstart-dft-stable-diffusion-v2-1-base")


def lambda_handler(event, context):
    """
    Function to generate images using Stable Diffusion model.
    :param event: Dictionary containing the prompt and other parameters.
    :param context: Lambda context object.
    :return: Dictionary containing the generated images and the prompt.
    """
    if not event.get("prompt"):
        return build_error_response(
            400, "Missing required field 'prompt' in the request body"
        )
    payload = {
        "prompt": event.get("prompt"),
        "width": 512,
        "height": 512,
        "num_images_per_prompt": event.get("num_images", 1),
        "num_inference_steps": event.get("num_inference_steps", 50),
    }
    encoded_payload = json.dumps(payload).encode("utf-8")
    response = invoke(encoded_payload, None, ENDPOINT)
    # Decode the content if it's in bytes
    body_content = None
    if isinstance(response["Body"], StreamingBody):
        body_content = response["Body"].read()
        body_content = json.loads(body_content.decode("utf-8"))
    if not body_content:
        return build_error_response(
            500,
            "Body is missing from repsonse, something has gone wrong with the model response!",
        )
    return {
        "statusCode": 200,
        "body": json.dumps(
            {
                "generatedImages": body_content["generated_images"],
                "prompt": body_content["prompt"],
            }
        ),
    }


def invoke(payload, client=None, endpoint=ENDPOINT):
    client = client if client else boto3.client("runtime.sagemaker")
    return client.invoke_endpoint(
        EndpointName=endpoint,
        ContentType="application/json",
        Accept="application/json;jpeg",
        Body=payload,
    )


def build_error_response(status_code, error_message):
    return {
        "statusCode": status_code,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Credentials": True,
        },
        "body": json.dumps({"error": error_message}),
    }
