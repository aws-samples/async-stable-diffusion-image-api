from unittest import TestCase
from unittest.mock import patch
from app.store_conn import lambda_handler, put_item
import json

UID = "12345678"
EXEC_ARN = "exec-arn"
CONN_ID = "conn-id"
FMT_DT_TM = "01-01-1999"
EXPIRE_AT = "10021999"


class TestStoreConnection(TestCase):
    @patch("boto3.client")
    def setUp(self, client) -> None:
        self.client = client

    def test_put_item(self):
        self.client.put_item.return_value = "test success"
        respoone = put_item(UID, EXEC_ARN, CONN_ID, FMT_DT_TM, EXPIRE_AT, self.client)
        self.assertEqual("test success", respoone)
        self.client.put_item.assert_called_once_with(
            TableName="image-conneciton-table",
            Item={
                "id": {"S": str(UID)},
                "executionArn": {"S": EXEC_ARN},
                "connectionId": {"S": CONN_ID},
                "date_time": {"S": FMT_DT_TM},
                "expire_at": {"N": str(EXPIRE_AT)},
            },
        )

    @patch("uuid.uuid4", return_value=UID)
    @patch("app.store_conn.time")
    @patch("app.store_conn.put_item", return_value="success!")
    def test_lambda_handler(self, put_item, tm, uid):
        tm.strftime.return_value = FMT_DT_TM
        tm.time.return_value = EXPIRE_AT
        test_context = {
            "body": json.dumps({"data": {"executionArn": EXEC_ARN}}),
            "requestContext": {"connectionId": CONN_ID},
        }
        expected_response = {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Credentials": True,
            },
            "body": json.dumps({"message": "success"}),
        }
        response = lambda_handler(test_context, {})
        self.assertEqual(expected_response, response)
        put_item.assert_called_once_with(
            UID, EXEC_ARN, CONN_ID, FMT_DT_TM, int(EXPIRE_AT) + 300
        )
