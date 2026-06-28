import json
import os
from unittest.mock import patch, MagicMock
import pytest

os.environ["TABLE_NAME"] = "test-table"

with patch("boto3.resource") as mock_resource:
    mock_table = MagicMock()
    mock_resource.return_value.Table.return_value = mock_table
    from backend.lambda_function.app import lambda_handler

class TestLambdaHandler:
    """Tests for the visitor counter Lambda function."""

    def test_returns_200_on_success(self):
        """Should return status 200 with a count."""
        mock_table.update_item.return_value = {
            "Attributes": {"visit_count": 42}
        }

        result = lambda_handler({}, {})

        assert result["statusCode"] == 200
        body = json.loads(result["body"])
        assert body["count"] == 42

    def test_increments_counter(self):
        """Should call update_item with ADD expression."""
        mock_table.update_item.return_value = {
            "Attributes": {"visit_count": 1}
        }

        lambda_handler({}, {})

        mock_table.update_item.assert_called_once_with(
            Key={"id": "visitor_count"},
            UpdateExpression="ADD visit_count :inc",
            ExpressionAttributeValues={":inc": 1},
            ReturnValues="UPDATED_NEW",
        )

    def test_returns_500_on_dynamodb_error(self):
        """Should return 500 if DynamoDB throws an error."""
        from botocore.exceptions import ClientError

        mock_table.update_item.side_effect = ClientError(
            {"Error": {"Message": "Table not found", "Code": "ResourceNotFoundException"}},
            "UpdateItem",
        )

        result = lambda_handler({}, {})

        assert result["statusCode"] == 500
        body = json.loads(result["body"])
        assert "error" in body

    def test_response_body_is_valid_json(self):
        """The response body should always be parseable JSON."""
        mock_table.update_item.return_value = {
            "Attributes": {"visit_count": 7}
        }

        result = lambda_handler({}, {})

        # Should not raise
        parsed = json.loads(result["body"])
        assert isinstance(parsed, dict)

    def setup_method(self):
        """Reset mock state before each test."""
        mock_table.reset_mock()