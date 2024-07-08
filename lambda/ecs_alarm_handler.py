import logging

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)
cloudwatch_client = boto3.client('cloudwatch')
lambda_client = boto3.client('lambda')


def create_metric_alarm(alarm_name,
    alarm_description, alarm_actions,
    eval_periods, threshold,
    comparison_op, metrics):
  try:
    alarm = cloudwatch_client.put_metric_alarm(
      AlarmName=alarm_name,
      AlarmDescription=alarm_description,
      AlarmActions=alarm_actions,
      Threshold=threshold,
      DatapointsToAlarm=1,
      EvaluationPeriods=eval_periods,
      ComparisonOperator=comparison_op,
      Metrics=metrics
    )
    print(
      "Added alarm %s to track metric ",
      alarm_name,
    )
  except ClientError:
    logger.exception(
      "Couldn't add alarm %s to metric ",
      alarm_name,
    )
    raise
  else:
    return alarm


def delete_metric_alarms(alarm_names):
  try:
    cloudwatch_client.delete_alarms(
      AlarmNames=alarm_names
    )
    print(
      "Deleted alarms %s.", alarm_names
    )
  except ClientError:
    logger.exception(
      "Couldn't delete alarms for metric %s.%s.",
    )
    raise

def get_task_id(event):
  task_id = event['resources'][0].split('/')[-1]
  print(f"task id: {task_id}")
  return task_id

def get_task_status(event):
  status = event['detail']['lastStatus']
  print(f"current status: {status}")
  return status

def get_ecs_cluster_name(event):
  cluster_name = event['resources'][0].split('/')[-2]
  print(f"cluster name: {cluster_name}")
  return cluster_name

def get_ecs_service_name(event):
  service_name = event['detail']['group'].split(':')[-1]
  print(f"service name: {service_name}")
  return service_name

def lambda_handler(event, context):
  logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
  task_id = get_task_id(event)
  status = get_task_status(event)
  cluster_name = get_ecs_cluster_name(event)
  service_name = get_ecs_service_name(event)

  alarm_name = cluster_name + "-" + service_name + "-" + task_id + "-" + "alarm"
  print(f"alarm name: {alarm_name}")
  ## 變數
  function_name = 'close_unhealthy_task'

  if status == 'PROVISIONING':
    print('crate task alarm...')
    ## 變數
    alarm_actions = [
      'arn:aws:lambda:us-west-2:975049910219:function:' + function_name]
    ## rename
    alarm_description = 'use python create alarm' \
      ## 變數
    eval_periods = 1
    ## 變數
    threshold = 1
    ## 變數
    comparison_operator = "GreaterThanOrEqualToThreshold"
    ## 變數
    metrics = [{
      'Id': 'reboot_alarm',
      'Label': 'reboot_alarm',
      'ReturnData': True,
      'Expression': '(cpu_usage > 50) && (memory_usage > 20)'
    }, {
      'Id': 'cpu_usage',
      'Label': 'cpu_usage',
      'ReturnData': False,
      'Expression': '(cpu_utilized* 100) / cpu_reserved'
    }, {
      'Id': 'memory_usage',
      'Label': 'memory_usage',
      'ReturnData': False,
      'Expression': '(memory_utilized* 100) / memory_reserved',
    }, {
      'Id': 'cpu_utilized',
      'Label': 'cpu_utilized',
      'ReturnData': False,
      'MetricStat': {
        'Metric': {
          'Namespace': 'ecs-demo-cluster',
          'MetricName': 'CpuUtilized',
          'Dimensions': [{
            'Name': 'TaskId',
            'Value': task_id
          }]
        },
        'Stat': 'Average',
        'Period': 60

      },
    }, {
      'Id': 'cpu_reserved',
      'Label': 'cpu_reserved',
      'ReturnData': False,
      'MetricStat': {
        'Metric': {
          'Namespace': 'ecs-demo-cluster',
          'MetricName': 'CpuReserved',
          'Dimensions': [{
            'Name': 'TaskId',
            'Value': task_id
          }]
        },
        'Stat': 'Average',
        'Period': 60
      },
    }, {
      'Id': 'memory_utilized',
      'Label': 'memory_utilized',
      'ReturnData': False,
      'MetricStat': {
        'Metric': {
          'Namespace': 'ecs-demo-cluster',
          'MetricName': 'MemoryUtilized',
          'Dimensions': [{
            'Name': 'TaskId',
            'Value': task_id
          }]
        },
        'Stat': 'Average',
        'Period': 60
      },
    }, {
      'Id': 'memory_reserved',
      'Label': 'memory_reserved',
      'ReturnData': False,
      'MetricStat': {
        'Metric': {
          'Namespace': 'ecs-demo-cluster',
          'MetricName': 'MemoryReserved',
          'Dimensions': [{
            'Name': 'TaskId',
            'Value': task_id
          }]
        },
        'Stat': 'Average',
        'Period': 60
      },
    }]

    print(f"Creating alarm {alarm_name}")
    alarm = create_metric_alarm(alarm_name,
                                alarm_description,
                                alarm_actions,
                                eval_periods,
                                threshold,
                                comparison_operator,
                                metrics
                                )
    print(f"alarm {alarm}")
    ## 變數
    alarm_arn = 'arn:aws:cloudwatch:us-west-2:975049910219:alarm:' + alarm_name
    print(f"alarm_arn: {alarm_arn}")

    res = lambda_client.add_permission(
      FunctionName=function_name,
      Action='lambda:InvokeFunction',
      StatementId='alarm_lambda_' + task_id,
      Principal='lambda.alarms.cloudwatch.amazonaws.com',
      SourceArn=alarm_arn
    )
    print('------')
    print(f"add lambda permission: {res}")

  elif status == 'DEPROVISIONING':
    delete_metric_alarms([alarm_name])
    try:
      res = lambda_client.remove_permission(
        FunctionName=function_name,
        StatementId='alarm_lambda_' + task_id
      )
      print(f"remove lambda permission: {res}")
    except ClientError:
      logger.exception(
        "Couldn't add alarm %s to metric ",
        alarm_name,
      )
      print('encounter error')
