from io import BytesIO
import pytest
from unittest.mock import patch, MagicMock
from get import read_policy
from exceptionss import CustomException, DataNotFoundError, ValidationError
from validationss import validate_policy_id 

# bucket_name = 'new-usecase'

# Helper function to create a mock S3 client with specified behavior
def create_mock_s3_client(list_objects_v2_response, get_object_response):
    s3_mock = MagicMock()
    s3_mock.list_objects_v2.return_value = list_objects_v2_response
    s3_mock.get_object.return_value = get_object_response
    return s3_mock


def test_read_policy_success():
    event = {'policy_id': 'a12', 'date': '2024-06-17'}
    mock_list_objects_v2 = {'Contents': [{'Key': '2024-06-17/example.csv'}]}
    csv_content = (
        b'policy number,insurance type,policy start date,policy end date,renewal status,insured member,renewed by,policy status\n'
        b'a12,health,2024-01-01,2024-12-31,renewed,Akshay,JD123,active\n'
    )
    mock_get_object = {'Body': BytesIO(csv_content)}

    s3_mock = create_mock_s3_client(mock_list_objects_v2, mock_get_object)

    with patch('boto3.client', return_value=s3_mock):
        response = read_policy(event, s3_mock)
        assert response['statusCode'] == 200
        assert len(response['body']) == 1
        assert response['body'][0]['policy number'] == 'a12'


def test_read_policy_validation_error():
    # Define various invalid `policy_id` values
    invalid_events = [
        {'policy_id': None, 'date': '2024-06-17'},
        {'policy_id': '', 'date': '2024-06-17'},
        {'policy_id': '   ', 'date': '2024-06-17'},
        {'date': '2024-06-17'},  # missing policy_id
    ]
    
    s3_mock = create_mock_s3_client({}, {})

    with patch('boto3.client', return_value=s3_mock):
        for event in invalid_events:
            with pytest.raises(ValidationError):
                read_policy(event, s3_mock)

def test_read_policy_no_files():
    event = {'policy_id': 'a12', 'date': '2024-06-17'}
    s3_mock = create_mock_s3_client({'Contents': []}, {})

    with patch('boto3.client', return_value=s3_mock):
        with pytest.raises(DataNotFoundError):
            read_policy(event, s3_mock)



def test_read_policy_policy_not_found():
    event = {'policy_id': 'nonexistent', 'date': '2024-06-17'}
    mock_list_objects_v2 = {'Contents': [{'Key': '2024-06-17/example.csv'}]}
    csv_content = (
        b'policy number,insurance type,policy start date,policy end date,renewal status,insured member,renewed by,policy status\n'
        b'another_policy,health,2024-01-01,2024-12-31,renewed,Akshay,JD123,active\n'
    )
    mock_get_object = {'Body': BytesIO(csv_content)}

    s3_mock = create_mock_s3_client(mock_list_objects_v2, mock_get_object)

    with patch('boto3.client', return_value=s3_mock):
        with pytest.raises(DataNotFoundError):
            read_policy(event, s3_mock)



def test_read_policy_no_matching_files():
    event = {'policy_id': 'a12', 'date': '2024-06-17'}
    mock_list_objects_v2 = {'Contents': [{'Key': '2024-06-17/nomatch.txt'}]}
    s3_mock = create_mock_s3_client(mock_list_objects_v2, {})

    with patch('boto3.client', return_value=s3_mock):
        with pytest.raises(DataNotFoundError):
            read_policy(event, s3_mock)

