import boto3
import pandas as pd
from io import StringIO
from datetime import datetime
# from conftest import mock_s3
from exceptionss import CustomException, DataNotFoundError, ValidationError, S3UploadError
from util import store_temp_metadata_update, upload_csv_to_s3
from validationss import validate_policy_data

import logging

# Assuming this is in your update.py file
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

bucket_name = 'new-usecase'

def update_policy(event, s3_client, dynamodb):
    try:
        logger.debug("Received event: %s", event)

        # Example validation logic
        if 'policy_data' not in event or not isinstance(event['policy_data'], list):
            raise ValidationError('policy_data should be a list.')

        # Extract event data
        operation = event.get('operation')
        date_str = event.get('date')
        updated_policy_data = event.get('policy_data') 
        
        logger.debug("Operation: %s, Date: %s", operation, date_str)

        if operation != 'update':
            logger.error("Unsupported operation: %s", operation)
            raise ValidationError(400, 'Validation Error', 'Unsupported operation')
        
        # Validate policy data
        is_valid, validation_message = validate_policy_data(updated_policy_data)
        if not is_valid:
            raise ValidationError(400, 'Validation Error', validation_message)
        
        # Fetch existing policy data from S3
        s3_key = f"{date_str}/example.csv"
        logger.debug("Fetching data from S3 with key: %s", s3_key)
        
        try:
            s3_response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=date_str)
            logger.debug("S3 list_objects_v2 response: %s", s3_response)
            
            if 'Contents' not in s3_response or not s3_response['Contents']:
                logger.error("No files found in folder: %s", date_str)
                raise DataNotFoundError(404, 'File Not Found', f'No files found in folder: {date_str}')

            s3_file = s3_response['Contents'][0]['Key']
            logger.debug("Fetching S3 file: %s", s3_file)
            s3_object = s3_client.get_object(Bucket=bucket_name, Key=s3_file)
            file_content = s3_object['Body'].read().decode('utf-8')
            logger.debug("Fetched file content: %s", file_content)
        
        except DataNotFoundError as e:
            logger.error("Data not found error: %s", e)
            return {
                'statusCode': e.status,
                'body': {'error': e.error, 'message': e.message}
            }
        
        except Exception as e:
            logger.error("Error fetching data from S3: %s", e)
            raise CustomException(500, 'Internal Server Error', str(e))
        
        # Convert updated policy data to DataFrame
        df = pd.DataFrame([updated_policy_data])

        # Update logic here...
        try:
            logger.debug("Uploading updated CSV to S3")
            upload_csv_to_s3(date_str, df, bucket_name)
        except S3UploadError as e:
            logger.error("S3 upload error: %s", e)
            raise CustomException(500, 'Internal Server Error', 'Upload to S3 failed')

        logger.debug("Storing temporary metadata update")
        store_temp_metadata_update(date_str, len(updated_policy_data), 'temp_table_name' , dynamodb)
        
        return {
            'statusCode': 200,
            'body': 'Policy updated successfully!'
        }
    
    
    except DataNotFoundError as e:
        logger.error("Data not found error: %s", e)
        return {
            'statusCode': e.status,
            'body': {'error': e.error, 'message': e.message}
        }
    
    
    except ValidationError as e:
        logger.error("Validation error: %s", e)
        return {
            'statusCode': e.status,
            'body': {'error': e.error, 'message': e.message}
        }
    
    except CustomException as e:
        logger.error("Custom exception occurred: %s", e)
        return {
            'statusCode': e.status,
            'body': {'error': e.errormsg, 'message': e.error_body}
        }
    
    except Exception as e:
        logger.error("Unexpected error: %s", e)
        return {
            'statusCode': 500,
            'body': {'error': 'Internal Server Error', 'message': str(e)}
        }




# except FileNotFoundError:
    #     logger.error("File not found error")
    #     return {
    #         'statusCode': 404,
    #         'body': {'error': 'File Not Found'}
    #     }

    
    # except ValidationError as ve:
    #     logger.error("Validation error: %s", ve)
    #     raise ve

    # except DataNotFoundError as dnfe:
    #     raise dnfe

    # except Exception as e:
    #     raise CustomException(f"Error updating policy: {str(e)}")
    
# except S3UploadError as e:
    #     logger.error("S3 upload error: %s", e)
    #     return {
    #         'statusCode': e.status,
    #         'body': {'error': e.error, 'message': e.message}
    #     }