from io import BytesIO
import pytest
from unittest.mock import MagicMock, patch
from delete import delete_policy
from exceptionss import ValidationError, DataNotFoundError, CustomException


# @pytest.mark.timeout(10)
@patch('boto3.client')
@patch('boto3.resource')
@patch('update.store_temp_metadata_update')
@patch('update.upload_csv_to_s3')
@patch('validationss.validate_policy_id', return_value=(True, "Valid"))
def test_delete_policy_successful(mock_validate, mock_upload_csv, mock_store_temp, mock_boto3_resource, mock_s3):
    s3_mock_instance = MagicMock()
    s3_mock_instance.list_objects_v2.return_value = {'Contents': [{'Key': '2024-06-17/example.csv'}]}

    # Mock the get_object return value to simulate a file-like object for the CSV data
    csv_content = (
        b'policy number,insurance type,policy start date,policy end date,renewal status,insured member,renewed by,policy status\n'
        b'a12,health,2024-01-01,2024-12-31,renewed,Akshay,JD123,active\n'
    )
    s3_mock_instance.get_object.return_value = {'Body': BytesIO(csv_content)}

    mock_s3.return_value = s3_mock_instance
    dynamodb_mock_instance = MagicMock()
    mock_boto3_resource.return_value = dynamodb_mock_instance

    event = {'date': '2024-06-17', 'policy_id': 'a12'}
    # bucket_name = 'new-usecase'

    response = delete_policy(event)

    assert response['statusCode'] == 200
    assert response['body'] == 'Policy deleted successfully!'

    # mock_validate.assert_called_once_with(event)
    # mock_upload_csv.assert_called_once_with()
    # mock_store_temp.assert_called_once()


@patch('validationss.validate_policy_id', return_value=(False, "Invalid Policy ID"))
def test_delete_policy_validation_error(mock_validate):
    invalid_event = {'date': '2024-06-17', 'policy_id': ''}
    with pytest.raises(ValidationError) as excinfo:
        delete_policy(invalid_event)

    assert excinfo.value.to_dict() == {'status': 400, 'error': 'Validation Error', 'message': 'Missing policy_id field in the input event.'}
    # mock_validate.assert_called_once_with(invalid_event)


@patch('boto3.client')
@patch('update.store_temp_metadata_update')
@patch('update.upload_csv_to_s3')
@patch('validationss.validate_policy_id', return_value=(True, "Valid"))
def test_delete_policy_data_not_found(mock_validate, mock_upload_csv, mock_store_temp, mock_s3):
    event_not_found = {'date': '2024-06-17', 'policy_id': 'a12'}
    s3_mock_instance = MagicMock()
    s3_mock_instance.list_objects_v2.return_value = {'Contents': []}  # No objects found
    mock_s3.return_value = s3_mock_instance

    with pytest.raises(DataNotFoundError) as excinfo:
        delete_policy(event_not_found)

    assert excinfo.value.to_dict() == {'status': 404, 'error': 'File Not Found', 'message': 'No files found in folder: 2024-06-17/'}
    # mock_validate.assert_called_once_with(event_not_found)

@patch('boto3.client')
@patch('update.store_temp_metadata_update')
@patch('update.upload_csv_to_s3')
@patch('validationss.validate_policy_id', return_value=(True, "Valid"))
def test_delete_policy_internal_server_error(mock_validate, mock_upload_csv, mock_store_temp, mock_s3):
    event_server_error = {'date': '2024-06-17', 'policy_id': 'a12'}
    s3_mock_instance = MagicMock()
    s3_mock_instance.list_objects_v2.side_effect = Exception("Internal Server Error")
    mock_s3.return_value = s3_mock_instance

    with pytest.raises(CustomException) as excinfo:
        delete_policy(event_server_error)

    assert excinfo.value.to_dict() == {
        'status': 500,
        'error': 'Internal Server Error',
        'message': 'Error deleting policy: Internal Server Error'
    }

