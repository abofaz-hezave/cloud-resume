import json
import os
import boto3
from botocore.exceptions import ClientError

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TABLE_NAME'])

counterKey = 'visitor_count'

def lambda_handler(event, context):
    """Increment the visitor count in DynamoDB and return the new value"""
    try:
        response = table.update_item(
            Key={"id": counterKey},
            UpdateExpression="ADD visit_count :inc",
            ExpressionAttributeValues={":inc": 1},
            ReturnValues="UPDATED_NEW"
        )

        count = int(response["Attributes"]["visit_count"])

        return {
            "statusCode": 200,
            "body": json.dumps({"count": count}),
        }

    except ClientError as e:
        print(f"DynamoDB error: {e.response['Error']['Message']}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Could not update visitor count"}),
        }
