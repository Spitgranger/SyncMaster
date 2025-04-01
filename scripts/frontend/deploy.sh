#!/bin/bash

STACK_NAME="SyncMaster-Frontend"
TEMPLATE_FILE="infrastructure/frontend.yaml"
PARAMS="ParameterKey=Repository,ParameterValue=https://github.com/Spitgranger/SyncMaster ParameterKey=BranchNameAdmin,ParameterValue=frontend-deploy-staging ParameterKey=BranchNameContractor,ParameterValue=frontend-deploy-contractor ParameterKey=BaseAPIUrl,ParameterValue=${BASE_API_URL} ParameterKey=OauthToken,ParameterValue=${PAT}"

STACK_STATUS=$(aws cloudformation describe-stacks --stack-name $STACK_NAME $PROFILE --query "Stacks[0].StackStatus" --output text 2>/dev/null)

if [ "$STACK_STATUS" == "ROLLBACK_COMPLETE" ] || [ "$STACK_STATUS" == "UPDATE_ROLLBACK_COMPLETE" ]; then
    echo "Stack is in rollback state ($STACK_STATUS). Deleting and recreating..."
    aws cloudformation delete-stack --stack-name $STACK_NAME $PROFILE
    echo "Stack deletion initiated. Waiting for completion..."
    
    while aws cloudformation describe-stacks --stack-name $STACK_NAME $PROFILE 2>/dev/null; do
        echo "Waiting for stack deletion..."
        sleep 10
    done
    
    echo "Stack deleted successfully. Recreating..."
    aws cloudformation create-stack \
      --stack-name $STACK_NAME \
      --template-body file://$TEMPLATE_FILE \
      --parameters $PARAMS \
      --capabilities CAPABILITY_NAMED_IAM \
      $PROFILE

elif [ -z "$STACK_STATUS" ]; then
    echo "Stack does not exist. Creating..."
    aws cloudformation create-stack \
      --stack-name $STACK_NAME \
      --template-body file://$TEMPLATE_FILE \
      --parameters $PARAMS \
      --capabilities CAPABILITY_NAMED_IAM \
      $PROFILE
else
    echo "Stack exists. Updating..."
    aws cloudformation update-stack \
      --stack-name $STACK_NAME \
      --template-body file://$TEMPLATE_FILE \
      --parameters $PARAMS \
      --capabilities CAPABILITY_NAMED_IAM \
      $PROFILE || {
        echo "No updates to perform."
        exit 0
    }
fi

echo "Monitoring stack deployment..."
while true; do
    STATUS=$(aws cloudformation describe-stacks --stack-name $STACK_NAME $PROFILE --query "Stacks[0].StackStatus" --output text)

    echo "Current Status: $STATUS"

    if [[ "$STATUS" == "CREATE_COMPLETE" || "$STATUS" == "UPDATE_COMPLETE" ]]; then
        echo "Deployment successful!"
        OUTPUTS=$(aws cloudformation describe-stacks --stack-name $STACK_NAME $PROFILE --query "Stacks[0].Outputs" --output json)

        # Extract values
        CONTRACTOR_APP_URL=$(echo $OUTPUTS | jq -r '.[] | select(.OutputKey=="ContractorAppURL") | .OutputValue')
        ADMIN_APP_URL=$(echo $OUTPUTS | jq -r '.[] | select(.OutputKey=="AdminAppURL") | .OutputValue')

        # Display results
        echo "Contractor App URL: $CONTRACTOR_APP_URL"
        echo "Admin App URL: $ADMIN_APP_URL"
        break
    elif [[ "$STATUS" == "ROLLBACK_COMPLETE" || "$STATUS" == "UPDATE_ROLLBACK_COMPLETE" ]]; then
        echo "Deployment failed. Check CloudFormation logs."
        exit 1
    fi

    sleep 10
done
