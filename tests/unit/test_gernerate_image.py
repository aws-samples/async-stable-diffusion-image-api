import json
import io
from unittest import TestCase
from unittest.mock import Mock, patch
from app.generate_image import lambda_handler, invoke
from botocore.response import StreamingBody

TEST_PAYLOAD = ("im a payload",)
TEST_ENDPOINT = "im an endpoint"


class TestGenerateImage(TestCase):
    @patch("boto3.client")
    def setUp(self, client) -> None:
        self.client = client

    def test_invoke(self):
        self.client.invoke_endpoint.return_value = {"test": "test"}
        result = invoke(TEST_PAYLOAD, self.client, TEST_ENDPOINT)
        self.assertEqual(result, {"test": "test"})
        self.client.invoke_endpoint.assert_called_with(
            EndpointName=TEST_ENDPOINT,
            ContentType="application/json",
            Accept="application/json;jpeg",
            Body=TEST_PAYLOAD,
        )

    def test_lambda_handler_no_prompt(self):
        expected_response = {
            "statusCode": 400,
            "body": json.dumps(
                {"error": "Missing required field 'prompt' in the request body"}
            ),
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Credentials": True,
            },
        }

    @patch("app.generate_image.invoke")
    def test_lambda_handler_body_content_error(self, mock_invoke):
        expected_response = {
            "statusCode": 500,
            "body": json.dumps(
                {
                    "error": "Body is missing from repsonse, something has gone wrong with the model response!"
                }
            ),
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Credentials": True,
            },
        }
        mock_invoke.return_value = {"Body": "Something is wrong"}
        response = lambda_handler({"prompt": "test"}, {})
        self.assertEqual(expected_response, response)

    @patch("app.generate_image.invoke")
    def test_lambda_handler(self, mock_invoke: Mock):
        mock_body = {"generated_images": "testing 1234", "prompt": "a test prompt"}
        encoded_response = json.dumps(mock_body).encode("utf-8")
        body = StreamingBody(io.BytesIO(encoded_response), len(encoded_response))
        mock_response = {"Body": body}
        mock_invoke.return_value = mock_response
        expected_response = {
            "statusCode": 200,
            "body": json.dumps(
                {
                    "generatedImages": "testing 1234",
                    "prompt": "a test prompt",
                }
            ),
        }

        response = lambda_handler({"prompt": "a test prompt"}, {})
        mock_invoke.assert_called()
        self.assertEqual(expected_response, response)
