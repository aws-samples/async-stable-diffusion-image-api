import json
import os
import boto3
from botocore.response import StreamingBody

RUNTIME= boto3.client('runtime.sagemaker')
ENDPOINT = os.getenv("ENDPOINT_NAME", "jumpstart-dft-stable-diffusion-v2-1-base")

def lambda_handler(event, context):
    print(event)

    payload = {
    "prompt": event.get("prompt"),
    "width": 512,
    "height": 512,
    "num_images_per_prompt": event.get("num_images", 1),
    "num_inference_steps": event.get("num_inference_steps", 50),
    }
    encoded_payload = json.dumps(payload).encode("utf-8")
    response = RUNTIME.invoke_endpoint(EndpointName=ENDPOINT,
                                       ContentType='application/json',
                                       Accept='application/json;jpeg',
                                       Body=encoded_payload)
    # Decode the content if it's in bytes
    body_content =  None
    if isinstance(response["Body"], StreamingBody):
        body_content = response["Body"].read()
        body_content = json.loads(body_content.decode('utf-8'))

    return {
        "statusCode": 200,
        "body": json.dumps({
            "generatedImages": body_content["generated_images"],
            "prompt": body_content["prompt"]
        }),
    }

        