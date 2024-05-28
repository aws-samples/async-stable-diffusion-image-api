import requests
import websockets
import base64
import asyncio
import json
from io import BytesIO
from PIL import Image


API_KEY=""

async def connect_to_websocket(exec_id):
    uri = ""

    async with websockets.connect(uri) as websocket:
        # Sending a message
        payload = {
            "data": {
                "executionArn": exec_id
            }
        }
        await websocket.send(json.dumps(payload))

        # Receiving messages
        while True:
            message = await websocket.recv()
            print(f"Received: {message}")
            if "generatedImages" in message:
                return json.loads(message)

if __name__ == "__main__":
    url = "https://.execute-api.us-east-1.amazonaws.com/prod/generate"
    data = {"prompt": "cat lying on beach with a large brimmed sun hat, playing with a ball of yarn"}
    response = requests.post(url, json=data, headers={"x-api-key": API_KEY}).json()
    resp = asyncio.get_event_loop().run_until_complete(connect_to_websocket(response['executionArn']))
    for image in resp["generatedImages"]:

        image_decoded = BytesIO(base64.b64decode(image.encode()))
        image_rgb = Image.open(image_decoded).convert("RGB")
        image_rgb.show()