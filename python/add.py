import pandas as pd
from io import StringIO
from datetime import datetime
import logging
from python.exceptionss import CustomException, DynamoDBUpdateError, ValidationError
from python.util import store_temp_metadata_update, upload_csv_to_s3
from python.validationss import validate_policy_data

logger = logging.getLogger()

def create_policy(event):

    try:
        policy_data = event.get('policy_data')
        if not policy_data:
            raise ValidationError(400, 'Validation Error', 'No policy data provided')
        
        logger.info("Creating policy with data: %s", policy_data)
        
        valid, message = validate_policy_data(policy_data)
        if not valid:
            raise ValidationError(400, 'Validation Error', message)
        
        # df = pd.DataFrame(policy_data)
        # file_id = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        
        # try:
        #     upload_csv_to_s3(file_id, df)
        # except Exception as e:
        #     logger.error("Error uploading CSV to S3: %s", e)
        #     raise ValidationError(500, 'Upload Error', 'Failed to upload CSV to S3')
        
        # try:
        #     store_temp_metadata_update(file_id, len(policy_data))
        # except Exception as e:
        #     logger.error("Error storing metadata update: %s", e)
        #     raise DynamoDBUpdateError(500, 'DynamoDB Update Error', 'Failed to store metadata update')
        
        upload_csv_to_s3(event)  # Assuming event contains necessary info
        store_temp_metadata_update(policy_data)  # Assuming this stores data in DynamoDB


        return {
            'statusCode': 200,
            'body': 'Policy created successfully!'
        }
    
    except ValidationError as ve:
        logger.error("Validation error: %s", ve)
        return {
            'statusCode': ve.status,
            'body': ve.message
        }
    
    except DynamoDBUpdateError as de:
        logger.error("DynamoDB update error: %s", de)
        return {
            'statusCode': de.status,
            'body': de.message
        }
    
    except CustomException as e:
        logger.error(f"CustomException: {str(e)}")
        return {
            'statusCode': e.status_code,
            'body': e.message
        }
    
    except Exception as e:
        logger.error("Unexpected error: %s", e)
        return {
            'statusCode': 500,
            'body': 'An unexpected error occurred'
        }


    # policy_data = event.get('policy_data')
    # logger.info("Creating policy with data: %s", policy_data)
    
    # valid, message = validate_policy_data(policy_data)
    # if not valid:
    #     raise ValidationError(400, 'Validation Error', message)
    
    # df = pd.DataFrame(policy_data)
    # file_id = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    
    # upload_csv_to_s3(file_id, df)
    # store_temp_metadata_update(file_id, len(policy_data))

    # return {
    #     'statusCode': 200,
    #     'body': 'Policy created successfully!'
    # }
