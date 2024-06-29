import boto3
import pandas as pd
from io import StringIO
from datetime import datetime
import logging

from exceptionss import CustomException, DataNotFoundError, ValidationError
from update import store_temp_metadata_update, upload_csv_to_s3
from validationss import validate_policy_id

logger = logging.getLogger()
logger.setLevel(logging.INFO)

bucket_name = 'new-usecase'

def delete_policy(event):
    policy_id = event['policy_id']
    date_str = event.get('date', datetime.now().strftime("%Y-%m-%d"))
    folder_prefix = f'{date_str}/'

    logger.info("Deleting policy with ID: %s from folder: %s", policy_id, folder_prefix)
    
    try:
        # List all objects in the specified date folder
        logger.info("Validating policy ID")
        valid, message = validate_policy_id(event)
        if not valid:
            logger.error("Validation failed: %s", message)
            raise ValidationError(400, 'Validation Error', message)
        
        # Initialize the S3 client
        logger.info("Initializing S3 client")
        s3 = boto3.client('s3')
        
        logger.info("Listing objects in folder: %s", folder_prefix)
        response = s3.list_objects_v2(Bucket=bucket_name, Prefix=folder_prefix)
        if 'Contents' not in response or len(response['Contents']) == 0:
        # if 'Contents' not in response:
            logger.error("No files found in folder: %s", folder_prefix)
            raise DataNotFoundError(404, 'File Not Found', f'No files found in folder: {folder_prefix}')

        # Find the file that matches the date
        logger.info("Processing found objects")
        for obj in response['Contents']:
            key = obj['Key']
            if key.startswith(folder_prefix):
                logger.info("Found file: %s", key)
                obj = s3.get_object(Bucket=bucket_name, Key=key)
                df_existing = pd.read_csv(obj['Body'])

                # Delete policy data from existing DataFrame
                logger.info("Deleting policy data from DataFrame")
                df_updated = df_existing[df_existing['policy number'] != policy_id]

                # Upload updated CSV file to S3
                logger.info("Uploading updated CSV to S3")
                upload_csv_to_s3(date_str, df_updated, bucket_name)

                # Update metadata in DynamoDB
                # logger.info("Updating metadata in DynamoDB")
                # store_temp_metadata_update(date_str, len(df_updated))

                # Update metadata in DynamoDB
                logger.info("Updating metadata in DynamoDB")
                dynamodb = boto3.resource('dynamodb')
                temp_table_name = 'your_temp_table_name'  # replace with your actual temp table name
                store_temp_metadata_update(date_str, len(df_updated), temp_table_name, dynamodb)
                
                return {
                    'statusCode': 200,
                    'body': 'Policy deleted successfully!'
                }
            
        logger.error("No matching files found in folder: %s", folder_prefix)
        raise DataNotFoundError(404, 'File Not Found', f'No matching files found in folder: {folder_prefix}')
    
    except ValidationError as e:
        raise e
    
    except DataNotFoundError as e:
        raise e
    
    except CustomException as e:
        raise e
    
    except Exception as e:
        logger.error("Error deleting policy: %s", e)
        raise CustomException(500, 'Internal Server Error', f'Error deleting policy: {str(e)}')


    # except CustomException as e:
    #     raise e
    
    # except Exception as e:
    #     logger.error("Error deleting policy: %s", e)
    #     raise CustomException(500, 'Internal Server Error', f'Error deleting policy: {str(e)}')
