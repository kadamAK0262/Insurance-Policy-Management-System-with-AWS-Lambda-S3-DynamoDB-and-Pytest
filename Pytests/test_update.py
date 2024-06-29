from io import BytesIO
import os
import sys
import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock
from update import update_policy
from util import store_temp_metadata_update, upload_csv_to_s3

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../python')))

# Helper function to create a mock S3 client
def create_mock_s3_client(s3_objects, s3_key=None, s3_file_content=None):
    s3_mock = MagicMock()
    s3_mock.list_objects_v2.return_value = s3_objects
    if s3_key and s3_file_content:
        s3_mock.get_object.return_value = {'Body': MagicMock(read=MagicMock(return_value=s3_file_content.encode('utf-8')))}
    return s3_mock


@patch('boto3.client')
@patch('boto3.resource')
@patch('update.store_temp_metadata_update')
@patch('update.upload_csv_to_s3')
@patch('validationss.validate_policy_data', return_value=(True, "Valid"))
def test_update_policy_success(mock_validate, mock_upload_csv, mock_store_temp, mock_boto3_resource, mock_s3):
    s3_mock_instance = MagicMock()
    s3_mock_instance.list_objects_v2.return_value = {'Contents': [{'Key': '2024-06-17/example.csv'}]}

    csv_content = (
        b'policy number,insurance type,policy start date,policy end date,renewal status,insured member,renewed by,policy status\n'
        b'12345,Health,2023-01-01,2024-01-01,Pending,John Doe,Agent X,Active\n'
    )
    s3_mock_instance.get_object.return_value = {'Body': BytesIO(csv_content)}

    mock_s3.return_value = s3_mock_instance
    dynamodb_mock_instance = MagicMock()
    mock_boto3_resource.return_value = dynamodb_mock_instance

    event = {
        'operation': 'update',
        'date': '2024-06-17',
        'policy_data': [{'policy number': '12345', 'insurance type': 'Health', 'policy start date': '2023-01-01',    
                         'policy end date': '2024-01-01', 'renewal status': 'Pending', 'insured member': 'John Doe', 
                         'renewed by': 'Agent X', 'policy status': 'Active'}]
    }

    response = update_policy(event, s3_mock_instance, dynamodb_mock_instance)

    assert response['statusCode'] == 200
    assert response['body'] == 'Policy updated successfully!'


@patch('validationss.validate_policy_data', return_value=(False, 'Validation Error'))
def test_update_policy_validation_error(mock_validate):
    event = {
        'operation': 'update',
        'date': '2024-06-17',
        'policy_data': [{'policy number': '', 'insurance type': 'Health', 'policy start date': '2023-01-01',
                         'policy end date': '2024-01-01', 'renewal status': 'Pending', 'insured member': 'John Doe',
                         'renewed by': 'Agent X', 'policy status': 'Active'}]
    }
    s3_mock = create_mock_s3_client({})
    dynamodb_mock = MagicMock()   
    response = update_policy(event, s3_mock, dynamodb_mock)
    
    assert response['statusCode'] == 400
    assert response['body']['error'] == 'Validation Error'

def test_update_policy_file_not_found():
    event = {
        'operation': 'update',
        'date': '2024-06-17',
        'policy_data': [{'policy number': '12345', 'insurance type': 'Health', 'policy start date': '2023-01-01',
                         'policy end date': '2024-01-01', 'renewal status': 'Pending', 'insured member': 'John Doe',
                         'renewed by': 'Agent X', 'policy status': 'Active'}]
    }  
    s3_mock = create_mock_s3_client({})
    dynamodb_mock = MagicMock()
    response = update_policy(event, s3_mock, dynamodb_mock)
    
    assert response['statusCode'] == 404
    assert response['body']['error'] == 'File Not Found'

def test_update_policy_unsupported_operation():
    event = {
        'operation': 'delete',
        'date': '2024-06-17',
        'policy_data': [{'policy number': '12345', 'insurance type': 'Health', 'policy start date': '2023-01-01',
                         'policy end date': '2024-01-01', 'renewal status': 'Pending', 'insured member': 'John Doe',
                         'renewed by': 'Agent X', 'policy status': 'Active'}]
    }
    s3_mock = create_mock_s3_client({})
    dynamodb_mock = MagicMock()
    response = update_policy(event, s3_mock, dynamodb_mock)
    
    assert response['statusCode'] == 400
    assert response['body']['error'] == 'Validation Error'

