import json
import requests
import boto3

def lambda_handler(event, context):
    api_url = "http://ecs-demo-alb-184978582.ap-northeast-1.elb.amazonaws.com/token"

    try:
        # Make the GET request to the target API
        response = requests.get(api_url)

        # Log the raw response text for debugging purposes
        print(f"Response Text: {response.text}")

        # Check if the request was successful
        if response.status_code == 200:
            response_data = response.text

            # Prepare the payload for the second Lambda function
            payload = {
                'statusCode': 200,
                'body': json.dumps({
                    'message': 'Request succeeded',
                    'response': response_data,
                    'accessToken': response_data  # Assuming the response contains the access token
                })
            }

            # Invoke the second Lambda function asynchronously
            lambda_client = boto3.client('lambda')
            lambda_client.invoke(
                FunctionName='GetHeapDump',
                InvocationType='Event',  # Asynchronous invocation
                Payload=json.dumps(payload)
            )

            return {
                'statusCode': 200,
                'body': json.dumps({
                    'message': 'API called and second Lambda invoked asynchronously',
                    'first_response': response_data
                })
            }
        else:
            return {
                'statusCode': response.status_code,
                'body': json.dumps({
                    'message': 'Failed to call API',
                    'status_code': response.status_code,
                    'response': response.text
                })
            }
    except requests.exceptions.RequestException as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': 'Request failed',
                'error': str(e)
            })
        }
