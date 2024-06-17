from io import BytesIO
from behave import given, when, then
import requests
import websockets
import base64
import asyncio
import json
import logging
from PIL import Image

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


@given("A request is made to the /generate endpoint using text prompt")
def test_generate(context):
    context.prompt = context.text.replace("\n", " ")
    print(f"Prompt: {context.prompt}")
    data = {"prompt": context.prompt}
    response = requests.post(
        f"{context.rest_api_url}generate",
        json=data,
        headers={"x-api-key": context.api_key},
    ).json()
    print(response)
    context.resp = asyncio.get_event_loop().run_until_complete(
        connect_to_websocket(context, response["executionArn"])
    )


@then("I should recieve a response with encoded image data.")
def test_response(context):
    print(f"Returned Prompt: {context.resp['prompt']}")
    assert context.resp["generatedImages"] is not None
    assert len(context.resp["generatedImages"]) == 1
    assert context.resp["prompt"] == context.prompt

    for image in context.resp["generatedImages"]:

        image_decoded = BytesIO(base64.b64decode(image.encode()))
        image_rgb = Image.open(image_decoded).convert("RGB")
        image_rgb.show()


async def connect_to_websocket(context, execution_arn):
    async with websockets.connect(context.websocket_api_url) as websocket:
        # Sending a message
        payload = {"data": {"executionArn": execution_arn}}
        await websocket.send(json.dumps(payload))
        # Receiving messages
        while True:
            message = await websocket.recv()
            print(f"Received Response")
            return json.loads(message)
