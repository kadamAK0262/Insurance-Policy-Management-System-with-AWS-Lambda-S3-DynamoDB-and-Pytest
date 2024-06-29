import boto3
import pandas as pd
from io import StringIO
from datetime import datetime
import logging

from exceptionss import CustomException, DataNotFoundError, ValidationError
from validationss import validate_policy_id

logger = logging.getLogger()
bucket_name = 'new-usecase'


def read_policy(event, s3):
    policy_id = event.get('policy_id')
    date_str = event.get('date', datetime.now().strftime("%Y-%m-%d"))
    folder_prefix = f'{date_str}/'
    
    logger.info("Reading policy with ID: %s", policy_id)
    logger.info("Looking for S3 key: %s", folder_prefix)

    valid, message = validate_policy_id(event)
    if not valid:
        raise ValidationError(400, 'Validation Error', message)
    
    try:
        response = s3.list_objects_v2(Bucket=bucket_name, Prefix=folder_prefix)
        
        if 'Contents' not in response or not response['Contents']:
            logger.error("No files found in folder: %s", folder_prefix)
            raise DataNotFoundError(404, 'File Not Found', f'No files found in folder: {folder_prefix}')

        policy_data_json = []
        
        for obj in response['Contents']:
            key = obj['Key']
            if key.startswith(folder_prefix) and key.endswith('.csv'):
            # if key.startswith(folder_prefix + date_str):
                logger.info("Found file: %s", key)
                obj = s3.get_object(Bucket=bucket_name, Key=key)
                df_existing = pd.read_csv(obj['Body'])

                if policy_id:
                    policy_data = df_existing[df_existing['policy number'] == policy_id]
                    if policy_data.empty:
                        logger.warning("Policy with ID %s not found", policy_id)
                        raise DataNotFoundError(404, 'Policy Not Found', f'Policy with ID {policy_id} not found!')
                else:
                    policy_data = df_existing
                policy_data_json.extend(policy_data.to_dict(orient='records'))

        if not policy_data_json:
            logger.error("No matching files found in folder: %s", folder_prefix)
            raise DataNotFoundError(404, 'File Not Found', f'No matching files found in folder: {folder_prefix}')
        
        return {
            'statusCode': 200,
            'body': policy_data_json
        }
    
    except CustomException as e:
        logger.error("Custom exception occurred: %s", e)
        raise e

    except Exception as e:
        logger.error("Error reading policy: %s", e)
        raise CustomException(500, 'Internal Server Error', f'Error reading policy: {str(e)}')








# ***************Working code *******************


# def read_policy(event):
#     policy_id = event.get('policy_id')
#     date_str = event.get('date', datetime.now().strftime("%Y-%m-%d"))
#     folder_prefix = f'{date_str}/'
    
#     logger.info("Reading policy with ID: %s", policy_id)
#     logger.info("Looking for S3 key: %s", folder_prefix)

#     valid, message = validate_policy_id(event)
#     if not valid:
#         raise ValidationError(400, 'Validation Error', message)
    
#     try:
#         response = s3.list_objects_v2(Bucket=bucket_name, Prefix=folder_prefix)
        
#         if 'Contents' not in response:
#             logger.error("No files found in folder: %s", folder_prefix)
#             raise DataNotFoundError(404, 'File Not Found', f'No files found in folder: {folder_prefix}')
            
#         for obj in response['Contents']:
#             key = obj['Key']
#             if key.startswith(folder_prefix + date_str):
#                 logger.info("Found file: %s", key)
#                 obj = s3.get_object(Bucket=bucket_name, Key=key)
#                 df_existing = pd.read_csv(obj['Body'])

#                 if policy_id:
#                     policy_data = df_existing[df_existing['policy number'] == policy_id]
#                     if policy_data.empty:
#                         logger.warning("Policy with ID %s not found", policy_id)
#                         raise DataNotFoundError(404, 'Policy Not Found', f'Policy with ID {policy_id} not found!')
#                 else:
#                     policy_data = df_existing

#                 policy_data_json = policy_data.to_dict(orient='records')
                
#                 return {
#                     'statusCode': 200,
#                     'body': policy_data_json
#                 }

#         logger.error("No matching files found in folder: %s", folder_prefix)
#         raise DataNotFoundError(404, 'File Not Found', f'No matching files found in folder: {folder_prefix}')
    
#     except CustomException as e:
#         raise e
    
#     except Exception as e:
#         logger.error("Error reading policy: %s", e)
#         raise CustomException(500, 'Internal Server Error', f'Error reading policy: {str(e)}')

