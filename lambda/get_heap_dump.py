import json
import requests

def lambda_handler(event, context):
    # Extract the body from the event
    body = json.loads(event['body'])
    access_token = body.get('accessToken')


    # Hardcoded values (replace with dynamic values if necessary)
    api_url = "http://172.31.19.91:8080/heapDump"

    try:
        # Prepare headers for the GET request
        headers = {
            'accessToken': access_token
        }
        print(f"Request Headers: {headers}")

        # Make the GET request to the target API with the access token in the header
        response = requests.get(api_url, headers=headers)
        print(f"Response Text: {response.text}")

        # Check if the request was successful
        if response.status_code == 200:
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'message': 'Request succeeded',
                    'response': response.text
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
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': 'An error occurred',
                'error': str(e)
            })
        }
