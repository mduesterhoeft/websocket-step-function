import json
import uuid
import boto3
import os
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
tasksTable = dynamodb.Table('tasks')
stepFunctionClient = boto3.client('stepfunctions')
stepFunctionArn = os.environ['STEP_FUNCTION_ARN']


def register_task(event, context):
    print("starting step function")
    task_id = uuid.uuid4().__str__()
    step_function_execution_response = stepFunctionClient.start_execution(
        stateMachineArn=stepFunctionArn,
        name=task_id,
        input="{}"
    )

    print("started stepfunction ", step_function_execution_response['executionArn'])

    tasksTable.put_item(
        Item={
            "taskId": task_id,
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "state": "started"
        }
    )

    print("stored task with id", task_id)

    body = {
        "taskId": task_id
    }
    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }

    return response


def ws_connect_handler(event, context):
    print(event)
    connection_id = event['requestContext']['connectionId']
    print("connect ", connection_id)
    response = {
        "statusCode": 200,
    }
    return response


def ws_default_handler(event, context):
    connection_id = event['requestContext']['connectionId']
    body = event["body"]
    print(body)
    task_id = body.replace('\n', '').strip()
    print("default handler for ", connection_id, task_id)
    tasksTable.update_item(
        Key={"taskId": task_id},
        UpdateExpression="SET connection_id = :connection_id",
        ExpressionAttributeValues={':connection_id': connection_id}
    )
    response = {
        "statusCode": 200,
    }
    return response


def step_function_successful(event, context):
    task_id = event["detail"]["name"]
    print("state machine finished for task ", task_id)
    task_item = tasksTable.get_item(
        Key={"taskId": task_id}
    )
    connection_id = task_item["Item"]["connection_id"]
    print("found connection ", connection_id)

    api_gateway_api_client = boto3.client('apigatewaymanagementapi',
                                          endpoint_url='https://so8c9y95jk.execute-api.eu-central-1.amazonaws.com/dev')

    api_gateway_api_client.post_to_connection(
        Data=b'finished',
        ConnectionId=connection_id
    )


