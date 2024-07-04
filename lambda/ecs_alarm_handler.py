import boto3
import logging
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)
cloudwatch = boto3.resource("cloudwatch")
client = boto3.client('cloudwatch')
lambda_client = boto3.client('lambda')

class CLoudWatchWrapper:
  def __init__(self, cloudwatch_resource):
    self.cloudwatch_resource = cloudwatch_resource

  def create_metric_alarm(self,
      alarm_name,
      alarm_description,
      alarm_actions,
      eval_periods,
      threshold,
      comparison_op,
      metrics
  ):
    try:
      alarm = client.put_metric_alarm(
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

  def delete_metric_alarms(self, alarm_names):
    try:
      client.delete_alarms(
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


def lambda_handler(event, context):
  logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
  print("-" * 88)
  print("Welcome to the Amazon CloudWatch metrics and alarms demo!")
  print("-" * 88)

  task_id = event['resources'][0].split('/')[-1]
  print(f"task id: {task_id}")
  status = event['detail']['lastStatus']
  print(f"current status: {status}")
  cluster_name = event['resources'][0].split('/')[-2]
  print(f"cluster name: {cluster_name}")
  service_name = event['detail']['group'].split(':')[-1]
  print(f"service name: {service_name}")
  alarm_name = cluster_name + "-" + service_name + "-" + task_id + "-" + "alarm"
  print(f"alarm name: {alarm_name}")
  function_name = 'alarm_processor'

  cw_wrapper = CLoudWatchWrapper(cloudwatch)

  if status == 'PROVISIONING':
    print('crate task alarm...')
    alarm_actions = ['arn:aws:lambda:us-west-2:975049910219:function:' + function_name]
    alarm_description = 'use python create alarm'
    eval_periods = 1
    threshold = 1
    comparison_operator = "GreaterThanOrEqualToThreshold"
    metrics = [{
      'Id': 'reboot_alarm',
      'Label': 'reboot_alarm',
      'ReturnData': True,
      'Expression': '(cpu_usage > 20) && (memory_usage > 20)'
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
          'MetricName': 'cpu-utilized-metric',
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
          'MetricName': 'cpu-reserved-metric',
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
          'MetricName': 'memory-utilized-metric',
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
          'MetricName': 'memory-reserved-metric',
          'Dimensions': [{
            'Name': 'TaskId',
            'Value': task_id
          }]
        },
        'Stat': 'Average',
        'Period': 60
      },
    }, ]

    print(f"Creating alarm {alarm_name}")
    alarm = cw_wrapper.create_metric_alarm(alarm_name,
                                           alarm_description,
                                           alarm_actions,
                                           eval_periods,
                                           threshold,
                                           comparison_operator,
                                           metrics
                                           )
    print(f"alarm {alarm}")
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
    cw_wrapper.delete_metric_alarms([alarm_name])
    ## will throw exception if not exist
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
  else:
    print(f"show throw exception !!! {status}")
