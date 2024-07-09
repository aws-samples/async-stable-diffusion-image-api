from unittest import TestCase
from unittest.mock import MagicMock, patch
from app.issue_callback import lambda_handler, query_table, post_to_connection
from boto3.dynamodb.conditions import Key


class TestIssueCallback(TestCase):
    @patch("boto3.client")
    @patch("boto3.resource")
    def setUp(self, resource, client) -> None:
        self.client = client
        self.resource = resource

    def test_query_table(self):
        table = MagicMock()
        self.resource.Table.return_value = table
        table.query.return_value = "we did it!"
        test_expression = Key("executionArn").eq("test")
        result = query_table(test_expression, self.resource)
        table.query.assert_called_once_with(KeyConditionExpression=test_expression)
        self.assertEqual("we did it!", result)

    def test_post_to_connection(self):
        test_body = "test"
        test_connection = "test connection"
        self.client.post_to_connection.return_value = "we did it!"
        response = post_to_connection(test_body, test_connection, None, self.client)
        self.client.post_to_connection.called_once_with(
            Data=test_body, ConnectionId=test_connection
        )
        self.assertEqual("we did it!", response)

    @patch("app.issue_callback.query_table")
    @patch("app.issue_callback.post_to_connection")
    def test_lambda_handler(self, post_to_connection, query):
        query.return_value = {"Items": [{"connectionId": "connection-id"}]}
        post_to_connection.return_value = "we did it!"
        response = lambda_handler(
            {"payload": {"body": "test"}, "executionArn": "test"}, {}
        )
        self.assertEqual("we did it!", response)
