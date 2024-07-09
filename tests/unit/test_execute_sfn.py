import json
from unittest import TestCase
from unittest.mock import patch
from app.execute_sfn import lambda_handler, start_execution


class TestExecuteSFN(TestCase):
    @patch("boto3.client")
    def setUp(self, client) -> None:
        self.client = client

    def test_start_execution(self):
        self.client.start_execution.return_value = {"executionArn": "exec_arn"}
        response = start_execution("fake-arn", "fake-input", self.client)
        self.assertEqual({"executionArn": "exec_arn"}, response)

    @patch("app.execute_sfn.start_execution")
    def test_lambda_handler(self, start_exec_mock):
        start_exec_mock.return_value = {"executionArn": "exec_arn"}
        response = lambda_handler({"body": json.dumps({"prompt": "test"})}, {})
        expected_response = {
            "statusCode": 200,
            "body": json.dumps({"executionArn": "exec_arn"}),
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Credentials": True,
            },
        }
        self.assertEqual(expected_response, response)

    def test_lambda_handler_no_body(self):
        response = lambda_handler({"blah": None}, {})
        expected_response = {
            "statusCode": 400,
            "body": json.dumps(
                {"error": "Missing required field 'body' in the request body"}
            ),
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Credentials": True,
            },
        }
        self.assertEqual(expected_response, response)

    def test_lambda_handler_no_prompt(self):
        response = lambda_handler({"body": json.dumps({"blah": "not a prompt"})}, {})
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
        self.assertEqual(expected_response, response)
