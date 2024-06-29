import datetime
import boto3
import pandas as pd
import re

dynamodb = boto3.resource('dynamodb')
s3 = boto3.client('s3')
table_name = 'PolicyMetadata'
bucket_name = 'insurance-policies'


# for events in lambda_function.py 
def validate_event(event):
# Ensure 'operation' is present and valid
    allowed_operations = ['create', 'read', 'update', 'delete']
    operation = event.get('operation')
    
    if not operation:
        return False, 'Missing operation field in the input event.'
    
    if operation not in allowed_operations:
        return False, f'Invalid operation. Allowed operations are: {", ".join(allowed_operations)}'
    
    # Validate required fields based on the operation
    if operation == 'create' or operation == 'update':
        if 'policy_data' not in event:
            return False, f'Missing policy_data field for {operation} operation.'
        
        if not isinstance(event['policy_data'], list):
            return False, f'The policy_data field should be a list for {operation} operation.'
        
        # Further validation for each policy in the policy_data list can be done here
        for policy in event['policy_data']:
            if not isinstance(policy, dict):
                return False, f'Each policy should be a dictionary in the policy_data list for {operation} operation.'
            # Add more specific policy field validations here

    elif operation == 'read' or operation == 'delete':
        if 'policy_id' not in event:
            return False, f'Missing policy_id field for {operation} operation.'
        
        if not isinstance(event['policy_id'], str):
            return False, f'The policy_id field should be a string for {operation} operation.'
    
    return True, 'Validation successful.'

#*************************************************************
# for add and update
def validate_policy_data(policy_data):
    required_fields = [
        'policy number', 'insurance type', 'policy start date',
        'policy end date', 'renewal status', 'insured member',
        'renewed by', 'policy status'
    ]
    
    if not isinstance(policy_data, list):
        return False, 'policy_data should be a list.'
    
    for policy in policy_data:
        if not isinstance(policy, dict):
            return False, 'Each policy should be a dictionary.'
        
        for field in required_fields:
            if field not in policy:
                return False, f'Missing field {field} in policy.'
            
        # Check if the field value is None or empty string
            if policy[field] is None or (isinstance(policy[field], str) and policy[field].strip() == ''):
                return False, f'{field} cannot be None or empty.'
        
        # Check data types and business rules
        if not isinstance(policy['policy number'], str):
            return False, 'policy number should be a string.'
        if not isinstance(policy['insurance type'], str):
            return False, 'insurance type should be a string.'
        if not isinstance(policy['policy start date'], str) or not validate_date_format(policy['policy start date']):
            return False, 'policy start date should be a valid date string in YYYY-MM-DD format.'
        if not isinstance(policy['policy end date'], str) or not validate_date_format(policy['policy end date']):
            return False, 'policy end date should be a valid date string in YYYY-MM-DD format.'
        if not isinstance(policy['renewal status'], str):
            return False, 'renewal status should be a string.'
        if not isinstance(policy['insured member'], str):
            return False, 'insured member should be a string.'
        if not isinstance(policy['renewed by'], str):
            return False, 'renewed by should be a string.'
        if not isinstance(policy['policy status'], str):
            return False, 'policy status should be a string.'
        
        # Business logic: policy end date should be after policy start date
        if datetime.datetime.strptime(policy['policy end date'], '%Y-%m-%d') <= datetime.datetime.strptime(policy['policy start date'], '%Y-%m-%d'):
            return False, 'policy end date should be after policy start date.'
    
    return True, 'Validation successful.'

def validate_date_format(date_string):
    try:
        datetime.datetime.strptime(date_string, '%Y-%m-%d')
        return True
    except ValueError:
        return False

#*********************************************************************
    
#for policy id for get and delete :
def validate_policy_id(event):
    policy_id = event.get('policy_id')
    
    if not policy_id:
        return False, 'Missing policy_id field in the input event.'
    
    if not isinstance(policy_id, str) or not policy_id.strip():
        return False, 'The policy_id should be a non-empty string.'
    
    return True, 'Validation successful.'