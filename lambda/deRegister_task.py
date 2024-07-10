import json
import logging
import boto3
from botocore.exceptions import ClientError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ecs_client = boto3.client('ecs')
elbv2_client = boto3.client('elbv2')

def lambda_handler(event, context):
    # Extract task ID, service name, and cluster name
    task_id = get_task_id(event)
    service_name = get_service_name(event)
    cluster_name = get_cluster_name(event)

    # Print the extracted values
    print(f"Task ID: {task_id}")
    print(f"Service Name: {service_name}")
    print(f"Cluster Name: {cluster_name}")

    if task_id and service_name and cluster_name:
        # Get the private IP of the task
        private_ip = get_task_private_ip(cluster_name, task_id)
        if private_ip:
            # Print the private IP
            print(f"Private IP: {private_ip}")

            # Get the target group ARN using private IP, service name, and cluster name
            target_group_arn = find_target_group_arn(cluster_name, service_name, private_ip)
            if target_group_arn:
                print(f"Target Group ARN: {target_group_arn}")
                # Deregister the task from the target group
                deregister_target(target_group_arn, private_ip)

    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }

def get_task_id(event):
    """Extract task ID from CloudWatch alarm ARN."""
    alarm_arn = event.get('alarmArn', '')
    if not alarm_arn:
        logger.error("alarmArn not found in event")
        return None

    try:
        task_id = alarm_arn.split(':')[-1].split('-')[-2]
        print(f"Extracted task id: {task_id}")
        return task_id
    except IndexError as e:
        logger.error(f"Error extracting task ID: {e}")
        return None

def get_service_name(event):
    """Extract service name from CloudWatch alarm ARN."""
    alarm_arn = event.get('alarmArn', '')
    try:
        ecs_demo_service = '-'.join(alarm_arn.split(':')[-1].split('-')[3:6])
        print(f"Extracted service name: {ecs_demo_service}")
        return ecs_demo_service
    except IndexError as e:
        logger.error(f"Error extracting service name: {e}")
        return None

def get_cluster_name(event):
    """Extract ECS cluster name from CloudWatch alarm data."""
    metrics = event.get('alarmData', {}).get('configuration', {}).get('metrics', [])
    for metric in metrics:
        namespace = metric.get('metricStat', {}).get('metric', {}).get('namespace', None)
        if namespace:
            print(f"Extracted cluster name: {namespace}")
            return namespace
    logger.error("Cluster name not found in event")
    return None

def get_task_private_ip(cluster_name, task_id):
    """Get the private IP of the ECS task."""
    try:
        response = ecs_client.describe_tasks(
            cluster=cluster_name,
            tasks=[task_id]
        )
        attachments = response['tasks'][0]['attachments']
        for attachment in attachments:
            if attachment['type'] == 'ElasticNetworkInterface':
                for detail in attachment['details']:
                    if detail['name'] == 'privateIPv4Address':
                        private_ip = detail['value']
                        print(f"Extracted private IP: {private_ip}")
                        return private_ip
    except ClientError as e:
        logger.error(f"Error describing task {task_id}: {e}")
    except IndexError as e:
        logger.error(f"Error extracting private IP: {e}")
    return None

def find_target_group_arn(cluster_name, service_name, private_ip):
    """Find the target group ARN for the ECS service that has the specified private IP as a registered target."""
    try:
        # Describe the ECS service to get the target group ARNs
        response = ecs_client.describe_services(
            cluster=cluster_name,
            services=[service_name]
        )
        if 'loadBalancers' in response['services'][0]:
            for lb in response['services'][0]['loadBalancers']:
                if 'targetGroupArn' in lb:
                    target_group_arn = lb['targetGroupArn']

                    # Describe the target group to see if it has the specified private IP
                    target_response = elbv2_client.describe_target_health(
                        TargetGroupArn=target_group_arn
                    )
                    for target in target_response['TargetHealthDescriptions']:
                        if target['Target']['Id'] == private_ip:
                            print(f"Found target group ARN: {target_group_arn}")
                            return target_group_arn
        logger.error(f"Target group ARN not found for service: {service_name} with private IP: {private_ip}")
    except ClientError as e:
        logger.error(f"Error finding target group ARN for service {service_name} in cluster {cluster_name}: {e}")
    return None

def deregister_target(target_group_arn, ip):
    """Deregister the target (task) from the target group."""
    try:
        response = elbv2_client.deregister_targets(
            TargetGroupArn=target_group_arn,
            Targets=[
                {
                    'Id': ip,
                    'Port': 8080  # Update the port as necessary
                }
            ]
        )
        print(f"Deregister response: {response}")
    except ClientError as e:
        logger.error(f"Error deregistering target {ip}: {e}")
