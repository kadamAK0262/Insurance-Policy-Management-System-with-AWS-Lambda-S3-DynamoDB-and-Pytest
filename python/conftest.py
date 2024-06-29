import boto3
import os 
import pytest
from unittest.mock import patch, MagicMock
from botocore.stub import Stubber


# (scope='function')
@pytest.fixture(scope='session', autouse=True)
def aws_credentials():
    """ MOcked aws credentials"""

    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"


@pytest.fixture
def mock_dynamodb():
    with patch('boto3.resource') as mock:
        yield mock

@pytest.fixture
def mock_s3():
    with patch('boto3.client') as mock:
        yield mock

# @pytest.fixture
# def mock_dynamodb(aws_credentials):
#     with patch('boto3.client') as mock:
#         dynamodb = boto3.client('dynamodb', region_name='us-east-1')
#         stubber = Stubber(dynamodb)
#         mock.return_value = dynamodb
#         yield stubber
#         stubber.deactivate()

# @pytest.fixture
# def mock_s3(aws_credentials):
#     with patch('boto3.client') as mock:
#         s3 = boto3.client('s3', region_name='us-east-1')
#         stubber = Stubber(s3)
#         mock.return_value = s3
#         yield stubber
#         stubber.deactivate()








# @pytest.fixture
# def mock_dynamodb(aws_credentials):
#     with mock_dynamodb():
#         conn = boto3.client("dynamodb", region_name ="us-east-1" )
#         yield conn


# @pytest.fixture
# def mock_s3(aws_credentials):
#     with mock_s3():
#         conn =boto3.client('s3', region_name='us-east-1')
#         yield conn 