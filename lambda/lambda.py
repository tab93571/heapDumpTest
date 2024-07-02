import json
import boto3

# 目前還沒使用

client = boto3.client('cloudwatch')

alarm_name = 'ecs_task_cpu_and_memory_usage_to_high'

# 调用 describe_alarms API 获取 Alarm 信息
response = client.describe_alarms(
  AlarmNames=[alarm_name]
)


def get_dimension_value(response, dimension_name):
  # for alarm in response['MetricAlarms']:
  #   if 'Metrics' in alarm:
  #     for metric in alarm['Metrics']:
  #       if 'MetricStat' in metric:
  #         for dimension in metric['MetricStat']['Metric']['Dimensions']:
  #           if dimension['Name'] == dimension_name:
  #             return dimension['Value']
  #   elif 'MetricStat' in alarm:
  #     for dimension in alarm['MetricStat']['Metric']['Dimensions']:
  #       if dimension['Name'] == dimension_name:
  #         return dimension['Value']
  print('TODO - Call the AWS SDK to retrieve the task ID.')
  return None

def stop_task(task_id):
  print('TODO - Call the AWS SDK to stop the task.')
  return None

def lambda_handler(event, context):
  print('--- START ---')
  print(event)

  task_id = get_dimension_value(response, 'TaskId')

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

