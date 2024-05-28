from behave import given, when, then
import requests
import websockets
import base64
import asyncio
import json
import logging
import time

LOGGER = logging.getLogger(__name__)


@given("A request is made to the /generate endpoint using text prompt")
def test_generate(context):
    context.prompt = context.text
    data = {"prompt": context.prompt}
    response = requests.post(
        f"{context.rest_api_url}generate",
        json=data,
        headers={"x-api-key": context.api_key},
    ).json()
    LOGGER.info(response)
    context.resp = asyncio.get_event_loop().run_until_complete(
        connect_to_websocket(context, response["executionArn"])
    )


@then("I should recieve a response with encoded image data.")
def test_response(context):
    LOGGER.info(context.resp["prompt"])
    LOGGER.info(context.prompt)
    assert context.resp["generatedImages"] is not None
    assert len(context.resp["generatedImages"]) == 1
    assert context.resp["prompt"] == context.prompt


@then("I will save that image using /save with the name")
def test_save(context):
    context.image_name = f"{context.text}-{time.asctime()}"
    data = {
        "generatedImage": context.resp["generatedImages"][0],
        "imageName": f"{context.image_name}",
        "prompt": context.resp["prompt"],
    }
    response = requests.post(
        f"{context.rest_api_url}save",
        json=data,
        headers={"x-api-key": context.api_key},
    ).json()
    LOGGER.info(response)

    # assert response["statusCode"] == 200
    assert response["id"] is not None
    context.image_id = response["id"]


@then("I should be able to retrieve the images data using /images endpoint")
def test_retrieve(context):
    response = requests.get(
        f"{context.rest_api_url}images",
        headers={"x-api-key": context.api_key},
    ).json()
    LOGGER.info(response)
    for image in response['images']:
        if image['id'] == context.image_id:
            context.image = image
            break
        
    context.image_url = context.image['objectUrl']
    assert context.image is not None
    assert context.image['prompt'] == context.prompt
    assert context.image['imageName'] == context.image_name
    

@then("I should be able to view the image in my browser.")
def test_view(context):
    response = requests.get(
        f"{context.rest_api_url}view?name={context.text}",
        headers={"x-api-key": context.api_key},
    )
    LOGGER.info(response)

    assert response.status_code == 200
    assert response.headers["Content-Type"] == "image/png"
    assert response.content is not None


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
