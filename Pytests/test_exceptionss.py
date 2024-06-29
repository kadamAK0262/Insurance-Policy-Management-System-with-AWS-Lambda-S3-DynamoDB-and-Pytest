# Pytests/test_exception.py

import unittest
from unittest.mock import patch, Mock
import json
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../python')))

from exceptionss import CustomException, ValidationError, S3UploadError, DynamoDBUpdateError, DataNotFoundError, build_exception_response

class TestCustomExceptions(unittest.TestCase):

    def test_custom_exception_str(self):
        exc = CustomException(400, "Error occurred", "Some error details")
        expected_output = json.dumps({
            "status": 400,
            "error": "Error occurred",
            "message": "Some error details"
        })
        self.assertEqual(str(exc), expected_output)

    def test_custom_exception_to_dict(self):
        exc = CustomException(400, "Error occurred", "Some error details")
        expected_output = {
            "status": 400,
            "error": "Error occurred",
            "message": "Some error details"
        }
        self.assertEqual(exc.to_dict(), expected_output)

    def test_validation_error(self):
        with self.assertRaises(ValidationError) as cm:
            raise ValidationError(400, "Validation failed", "Invalid data provided")
        exc = cm.exception
        self.assertEqual(exc.status, 400)
        self.assertEqual(exc.error, "Validation failed")
        self.assertEqual(exc.message, "Invalid data provided")

    def test_s3_upload_error(self):
        with self.assertRaises(S3UploadError) as cm:
            raise S3UploadError(500, "S3 Upload failed", "Unable to upload to S3")
        exc = cm.exception
        self.assertEqual(exc.status, 500)
        self.assertEqual(exc.error, "S3 Upload failed")
        self.assertEqual(exc.message, "Unable to upload to S3")

    def test_dynamodb_update_error(self):
        with self.assertRaises(DynamoDBUpdateError) as cm:
            raise DynamoDBUpdateError(500, "DynamoDB Update failed", "Unable to update DynamoDB")
        exc = cm.exception
        self.assertEqual(exc.status, 500)
        self.assertEqual(exc.error, "DynamoDB Update failed")
        self.assertEqual(exc.message, "Unable to update DynamoDB")

    def test_data_not_found_error(self):
        with self.assertRaises(DataNotFoundError) as cm:
            raise DataNotFoundError(404, "Data not found", "Requested data does not exist")
        exc = cm.exception
        self.assertEqual(exc.status, 404)
        self.assertEqual(exc.error, "Data not found")
        self.assertEqual(exc.message, "Requested data does not exist")

    @patch('exceptionss.build_exception_response')
    def test_build_exception_response(self, mock_build_exception_response):
        exc = CustomException(500, "Internal Error", "An unexpected error occurred")
        mock_build_exception_response.return_value = {
            "status": 500,
            "error": "Internal Server Error",
            "message": {"information": str(exc)}
        }
        response = build_exception_response(exc)
        self.assertEqual(response, mock_build_exception_response.return_value)

if __name__ == '__main__':
    unittest.main()

