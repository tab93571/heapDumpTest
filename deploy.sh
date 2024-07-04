#!/bin/bash
# 還沒完成！！
if [ $# -eq 0 ]; then
  echo "缺少stack-name參數"
  exit
fi

if [ $# -eq 1 ]; then
  echo "缺少region參數"
  exit
fi

stackName=$1
region=$2
echo
echo stack-name: "$stackName"
echo region: "$region"
echo "開始部署pipeline..."
# create stack
aws cloudformation create-stack \
--parameters ParameterKey=ecsDemoVpcId,ParameterValue=vpc-09cb5cd5ef925ee97 \
ParameterKey=subnetIdList,ParameterValue="subnet-074ae923c244cddda\,subnet-0e1f6fcd2dcfa5adc\,subnet-03022198daa7101b8\,subnet-081292846f185bf89" \
--stack-name ecs-demo-stack --template-body file://ecs.yml --capabilities CAPABILITY_NAMED_IAM CAPABILITY_AUTO_EXPAND --region us-west-2

# delete stack
aws cloudformation delete-stack --stack-name ecs-demo-stack


