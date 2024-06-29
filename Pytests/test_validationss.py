# Pytests/test_validation.py
import pytest
import sys
import os
import unittest
from unittest.mock import patch, Mock

# import validation
# from Python_code import validation  # Adjust the import as necessary

# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../Python')))

# from Python_code import validation
from validationss import validate_event, validate_policy_data, validate_policy_id, validate_date_format

class TestValidationFunctions(unittest.TestCase):

    def test_validate_event_create_success(self):
        event = {
            "operation": "create",
            "policy_data": [
                {
                    "policy number": "ABC123",
                    "insurance type": "car insurance",
                    "policy start date": "2024-06-01",
                    "policy end date": "2025-06-01",
                    "renewal status": "renewed",
                    "insured member": "John Doe",
                    "renewed by": "jdoe123",
                    "policy status": "active"
                }
            ]
        }
        result, message = validate_event(event)
        self.assertTrue(result)
        self.assertEqual(message, 'Validation successful.')

    def test_validate_event_create_missing_policy_data(self):
        event = {
            "operation": "create"
        }
        result, message = validate_event(event)
        self.assertFalse(result)
        self.assertEqual(message, 'Missing policy_data field for create operation.')

    def test_validate_event_read_success(self):
        event = {
            "operation": "read",
            "policy_id": "ABC123"
        }
        result, message = validate_event(event)
        self.assertTrue(result)
        self.assertEqual(message, 'Validation successful.')

    def test_validate_event_read_missing_policy_id(self):
        event = {
            "operation": "read"
        }
        result, message = validate_event(event)
        self.assertFalse(result)
        self.assertEqual(message, 'Missing policy_id field for read operation.')

    def test_validate_policy_data_success(self):
        policy_data = [
            {
                "policy number": "ABC123",
                "insurance type": "car insurance",
                "policy start date": "2024-06-01",
                "policy end date": "2025-06-01",
                "renewal status": "renewed",
                "insured member": "John Doe",
                "renewed by": "jdoe123",
                "policy status": "active"
            }
        ]
        result, message = validate_policy_data(policy_data)
        self.assertTrue(result)
        self.assertEqual(message, 'Validation successful.')

    def test_validate_policy_data_missing_field(self):
        policy_data = [
            {
                "policy number": "ABC123",
                "insurance type": "car insurance",
                "policy start date": "2024-06-01",
                "policy end date": "2025-06-01",
                "renewal status": "renewed",
                "insured member": "John Doe",
                "policy status": "active"
            }
        ]
        result, message = validate_policy_data(policy_data)
        self.assertFalse(result)
        self.assertEqual(message, 'Missing field renewed by in policy.')

    def test_validate_date_format_success(self):
        self.assertTrue(validate_date_format("2024-06-01"))

    def test_validate_date_format_failure(self):
        self.assertFalse(validate_date_format("2024-13-01"))

    def test_validate_policy_id_success(self):
        event = {"policy_id": "ABC123"}
        result, message = validate_policy_id(event)
        self.assertTrue(result)
        self.assertEqual(message, 'Validation successful.')

    def test_validate_policy_id_missing_policy_id(self):
        event = {}
        result, message = validate_policy_id(event)
        self.assertFalse(result)
        self.assertEqual(message, 'Missing policy_id field in the input event.')

if __name__ == '__main__':
    unittest.main()















# # Pytests/test_validation.py
# import pytest
# import sys
# import os
# import unittest
# from unittest.mock import patch, Mock

# # import validation
# # from Python_code import validation  # Adjust the import as necessary

# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../python')))

# # from Python_code import validation
# from validationss import validate_event, validate_policy_data, validate_policy_id, validate_date_format

# class TestValidationFunctions(unittest.TestCase):

#     def test_validate_event_create_success(self):
#         event = {
#             "operation": "create",
#             "policy_data": [
#                 {
#                     "policy number": "ABC123",
#                     "insurance type": "car insurance",
#                     "policy start date": "2024-06-01",
#                     "policy end date": "2025-06-01",
#                     "renewal status": "renewed",
#                     "insured member": "John Doe",
#                     "renewed by": "jdoe123",
#                     "policy status": "active"
#                 }
#             ]
#         }
#         result, message = validate_event(event)
#         self.assertTrue(result)
#         self.assertEqual(message, 'Validation successful.')

#     def test_validate_event_create_missing_policy_data(self):
#         event = {
#             "operation": "create"
#         }
#         result, message = validate_event(event)
#         self.assertFalse(result)
#         self.assertEqual(message, 'Missing policy_data field for create operation.')

#     def test_validate_event_read_success(self):
#         event = {
#             "operation": "read",
#             "policy_id": "ABC123"
#         }
#         result, message = validate_event(event)
#         self.assertTrue(result)
#         self.assertEqual(message, 'Validation successful.')

#     def test_validate_event_read_missing_policy_id(self):
#         event = {
#             "operation": "read"
#         }
#         result, message = validate_event(event)
#         self.assertFalse(result)
#         self.assertEqual(message, 'Missing policy_id field for read operation.')

#     def test_validate_policy_data_success(self):
#         policy_data = [
#             {
#                 "policy number": "ABC123",
#                 "insurance type": "car insurance",
#                 "policy start date": "2024-06-01",
#                 "policy end date": "2025-06-01",
#                 "renewal status": "renewed",
#                 "insured member": "John Doe",
#                 "renewed by": "jdoe123",
#                 "policy status": "active"
#             }
#         ]
#         result, message = validate_policy_data(policy_data)
#         self.assertTrue(result)
#         self.assertEqual(message, 'Validation successful.')

#     def test_validate_policy_data_missing_field(self):
#         policy_data = [
#             {
#                 "policy number": "ABC123",
#                 "insurance type": "car insurance",
#                 "policy start date": "2024-06-01",
#                 "policy end date": "2025-06-01",
#                 "renewal status": "renewed",
#                 "insured member": "John Doe",
#                 "policy status": "active"
#             }
#         ]
#         result, message = validate_policy_data(policy_data)
#         self.assertFalse(result)
#         self.assertEqual(message, 'Missing field renewed by in policy.')

#     def test_validate_date_format_success(self):
#         self.assertTrue(validate_date_format("2024-06-01"))

#     def test_validate_date_format_failure(self):
#         self.assertFalse(validate_date_format("2024-13-01"))

#     def test_validate_policy_id_success(self):
#         event = {"policy_id": "ABC123"}
#         result, message = validate_policy_id(event)
#         self.assertTrue(result)
#         self.assertEqual(message, 'Validation successful.')

#     def test_validate_policy_id_missing_policy_id(self):
#         event = {}
#         result, message = validate_policy_id(event)
#         self.assertFalse(result)
#         self.assertEqual(message, 'Missing policy_id field in the input event.')

# if __name__ == '__main__':
#     unittest.main()
