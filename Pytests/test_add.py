import os
import sys
import pytest
from unittest.mock import MagicMock, patch
from python.add import create_policy
from python.exceptionss import DynamoDBUpdateError, ValidationError
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../python')))

@pytest.fixture
def event():
    return {
        'policy_data': [
            {'policy_number': '123', 'policy_details': 'details'}
        ]
    }

@pytest.fixture
def empty_event():
    return {
        'policy_data': None
    }

@pytest.fixture
def invalid_event():
    return {
        'policy_data': [
            {'policy_number': '', 'policy_details': 'details'}
        ]
    }

@pytest.fixture
def valid_event():
    return {'policy_data': [{'policy_details': 'details', 'policy_number': '123'}]}

@patch('python.add.validate_policy_data')
@patch('python.add.upload_csv_to_s3')
@patch('python.add.store_temp_metadata_update')
def test_create_policy_success(mock_store_temp_metadata_update, mock_upload_csv_to_s3, mock_validate_policy_data, event):
    mock_validate_policy_data.return_value = (True, '')
    mock_upload_csv_to_s3.return_value = None
    mock_store_temp_metadata_update.return_value = None

    response = create_policy(event)
    
    print(response)
    assert response['statusCode'] == 200
    assert response['body'] == 'Policy created successfully!'
    mock_validate_policy_data.assert_called_once_with(event['policy_data'])
    mock_upload_csv_to_s3.assert_called_once()
    mock_store_temp_metadata_update.assert_called_once()

@patch('python.add.validate_policy_data')
@patch('python.add.upload_csv_to_s3')
@patch('python.add.store_temp_metadata_update')
def test_create_policy_no_policy_data(mock_store_temp_metadata_update, mock_upload_csv_to_s3, mock_validate_policy_data, empty_event):
    response = create_policy(empty_event)
    
    print(response)
    assert response['statusCode'] == 400
    assert response['body'] == 'No policy data provided'
    mock_validate_policy_data.assert_not_called()
    mock_upload_csv_to_s3.assert_not_called()
    mock_store_temp_metadata_update.assert_not_called()

@patch('python.add.validate_policy_data')
@patch('python.add.upload_csv_to_s3')
@patch('python.add.store_temp_metadata_update')
def test_create_policy_validation_error(mock_store_temp_metadata_update, mock_upload_csv_to_s3, mock_validate_policy_data, invalid_event):
    mock_validate_policy_data.return_value = (False, 'Invalid policy data')
    
    response = create_policy(invalid_event)
    
    print(response)
    assert response['statusCode'] == 400
    assert response['body'] == 'Invalid policy data'
    mock_validate_policy_data.assert_called_once_with(invalid_event['policy_data'])
    mock_upload_csv_to_s3.assert_not_called()
    mock_store_temp_metadata_update.assert_not_called()

@patch('python.add.validate_policy_data')
@patch('python.add.upload_csv_to_s3')
@patch('python.add.store_temp_metadata_update')
def test_create_policy_upload_error(mock_store_temp_metadata_update, mock_upload_csv_to_s3, mock_validate_policy_data, event):
    mock_validate_policy_data.return_value = (True, '')
    mock_upload_csv_to_s3.side_effect = Exception("S3 upload failed")
    
    response = create_policy(event)
    
    print(response)
    assert response['statusCode'] == 500
    assert response['body'] == 'An unexpected error occurred'
    mock_validate_policy_data.assert_called_once_with(event['policy_data'])
    mock_upload_csv_to_s3.assert_called_once()
    mock_store_temp_metadata_update.assert_not_called()

@patch('python.add.validate_policy_data')
@patch('python.add.upload_csv_to_s3')
@patch('python.add.store_temp_metadata_update')
def test_create_policy_dynamodb_update_error(mock_store_temp_metadata_update, mock_upload_csv_to_s3, mock_validate_policy_data, event):
    mock_validate_policy_data.return_value = (True, '')
    mock_store_temp_metadata_update.side_effect = DynamoDBUpdateError(500, 'DynamoDB Update Error', 'Failed to store metadata update')
    
    response = create_policy(event)
    
    print(response)
    assert response['statusCode'] == 500
    assert response['body'] == 'Failed to store metadata update'
    mock_validate_policy_data.assert_called_once_with(event['policy_data'])
    mock_upload_csv_to_s3.assert_called_once()
    mock_store_temp_metadata_update.assert_called_once()

