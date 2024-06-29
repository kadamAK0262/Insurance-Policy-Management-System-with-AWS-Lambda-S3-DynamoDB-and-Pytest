import os
import sys
import pytest
import boto3
from botocore.exceptions import ClientError
import unittest
from unittest.mock import Mock, patch, MagicMock
from io import StringIO
import pandas as pd
from datetime import datetime

# Import the functions from utils.py
from util import upload_csv_to_s3, store_temp_metadata_update, end_of_day_update
from exceptionss import S3UploadError, DynamoDBUpdateError
# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../Python')))

class TestUtilFunctions(unittest.TestCase):

    @patch('boto3.client')
    def test_upload_csv_to_s3_success(self, mock_boto_client):
        mock_s3 = Mock()
        mock_boto_client.return_value = mock_s3

        file_id = "test_file"
        csv_data = pd.DataFrame({"col1": [1, 2], "col2": [3, 4]})
        bucket_name = "test_bucket"

        upload_csv_to_s3(file_id, csv_data, bucket_name)
        
        # Check if put_object was called with the correct parameters
        self.assertTrue(mock_s3.put_object.called)
        args, kwargs = mock_s3.put_object.call_args
        self.assertEqual(kwargs['Bucket'], bucket_name)
        self.assertIn(file_id, kwargs['Key'])

    @patch('boto3.resource')
    def test_store_temp_metadata_update_success(self, mock_boto_resource):
        mock_dynamodb = Mock()
        mock_table = Mock()
        mock_boto_resource.return_value = mock_dynamodb
        mock_dynamodb.Table.return_value = mock_table

        file_id = "test_file"
        num_policies = 10
        temp_table_name = "temp_table"

        store_temp_metadata_update(file_id, num_policies, temp_table_name, mock_dynamodb)
        
        # Check if put_item was called with the correct parameters
        self.assertTrue(mock_table.put_item.called)
        args, kwargs = mock_table.put_item.call_args
        self.assertEqual(kwargs['Item']['policy_id'], file_id)
        self.assertEqual(kwargs['Item']['NumberOfPolicies'], num_policies)

    @patch('boto3.resource')
    def test_end_of_day_update_success(self, mock_boto_resource):
        mock_dynamodb = Mock()
        mock_temp_table = Mock()
        mock_main_table = Mock()
        mock_boto_resource.return_value = mock_dynamodb
        mock_dynamodb.Table.side_effect = [mock_temp_table, mock_main_table]

        temp_table_name = "temp_table"
        table_name = "main_table"

        mock_temp_table.scan.return_value = {
            'Items': [
                {'policy_id': 'test_file', 'NumberOfPolicies': 10, 'UpdateTimestamp': datetime.utcnow().isoformat()}
            ]
        }

        # Mock the batch_writer context manager
        mock_batch_writer = Mock()
        mock_batch_writer.__enter__ = Mock(return_value=mock_batch_writer)
        mock_batch_writer.__exit__ = Mock(return_value=None)
        mock_temp_table.batch_writer.return_value = mock_batch_writer

        end_of_day_update(temp_table_name, table_name, mock_dynamodb)
        
        # Check if update_item was called with the correct parameters
        self.assertTrue(mock_main_table.update_item.called)
        args, kwargs = mock_main_table.update_item.call_args
        self.assertEqual(kwargs['Key']['policy_id'], 'test_file')
        self.assertTrue(mock_batch_writer.delete_item.called)
        delete_args, delete_kwargs = mock_batch_writer.delete_item.call_args
        self.assertEqual(delete_kwargs['Key']['policy_id'], 'test_file')
        

if __name__ == '__main__':
    unittest.main()


