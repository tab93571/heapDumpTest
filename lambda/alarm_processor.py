import json
import boto3

# 目前還沒使用

client = boto3.client('cloudwatch')

alarm_name = 'ecs_task_cpu_and_memory_usage_to_high'


def get_dimension_value(response, dimension_name):
  print('TODO - Call the AWS SDK to retrieve the task ID.')
  return None

def stop_task(task_id):
  print('TODO - Call the AWS SDK to stop the task.')
  return None

def lambda_handler(event, context):
  print('--- START ---')
  print(event)
  print(event['alarmArn'])
  task_id = event['alarmArn'].split(':')[-1].split('-')[-2]

  print(f"task id: {task_id}")
  z = event['alarmData']['configuration']['metrics']
  print(z)
  # task_id = get_dimension_value(response, 'TaskId')

  if task_id:
    print(f'TaskId: {task_id}')
    stop_task(task_id)
  else:
    print('TaskId not found')

  print('--- END ---')
  return {
    'statusCode': 200,
    'body': json.dumps('Hello from Lambda!')
  }

