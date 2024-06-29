import boto3
from datetime import datetime
import logging
from exceptionss import CustomException, ValidationError, build_exception_response
from validationss import validate_event
from util import end_of_day_update
from add import create_policy
from get import read_policy
from update import update_policy
from delete import delete_policy

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
table_name = 'new_usecase'
bucket_name = 'new-usecase'
temp_table_name = 'temporary_metadata_updates'

def lambda_handler(event, context):
    logger.info("Received event: %s", event)
    operation = event['operation']
    
    try:
        valid, message = validate_event(event)
        if not valid:
            raise ValidationError(400, 'Validation Error', message)
        
        if operation == 'create':
            return create_policy(event)
        elif operation == 'read':
            return read_policy(event, s3)
        elif operation == 'update':
            return update_policy(event, s3, dynamodb)
        elif operation == 'delete':
            return delete_policy(event)
        elif operation == 'end_of_day_update':
            return end_of_day_update(temp_table_name, table_name, dynamodb)
        else:
            raise CustomException(400, 'Invalid Operation', 'Invalid operation specified')

    except ValidationError as e:
        logger.error("ValidationError: %s", e)
        return build_exception_response(e)
    
    except CustomException as e:
        logger.error("CustomException: %s", e)
        return build_exception_response(e)
    
    except Exception as e:
        logger.error("Unexpected error: %s", e)
        response = build_exception_response(e)
        return {
            'statusCode': response['status'],
            'body': str(response)
        }




# import boto3
# import pandas as pd
# from io import StringIO
# from datetime import datetime
# import logging

# # Set up logging
# logger = logging.getLogger()
# logger.setLevel(logging.INFO)

# s3 = boto3.client('s3')
# dynamodb = boto3.resource('dynamodb')
# table_name = 'new_usecase'
# bucket_name = 'new-usecase'
# temp_table_name = 'temporary_metadata_updates'

# def lambda_handler(event, context):
    
#     logger.info("Received event: %s", event)
#     operation = event['operation']
    
#     if operation == 'create':
#         return create_policy(event)
#     elif operation == 'read':
#         return read_policy(event)
#     elif operation == 'update':
#         return update_policy(event)
#     elif operation == 'delete':
#         return delete_policy(event)
#     elif operation == 'end_of_day_update':
#         return end_of_day_update()
#     else:
#         logger.error("Invalid operation: %s", operation)
#         return {
#             'statusCode': 400,
#             'body': 'Invalid operation!'
#         }

# def create_policy(event):
#     policy_data = event.get('policy_data')
#     logger.info("Creating policy with data: %s", policy_data)
    
#     if not policy_data:
#         logger.error("No policy data provided")
#         return {
#             'statusCode': 400,
#             'body': 'No policy data provided'
#         }
    
#     df = pd.DataFrame(policy_data)
#     file_id = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    
#     upload_csv_to_s3(file_id, df)
#     store_temp_metadata_update(file_id, len(policy_data))

    
#     return {
#         'statusCode': 200,
#         'body': 'Policy created successfully!'
#     }

# def read_policy(event):
#     policy_id = event.get('policy_id')
#     date_str = event.get('date', datetime.now().strftime("%Y-%m-%d"))
#     # file_key = f'{date_str}/{date_str}.csv'
#     # s3_key = f'{date_str}/{date_str}.csv'
#     folder_prefix = f'{date_str}/'
#     logger.info("Reading policy with ID: %s", policy_id)
#     logger.info("Looking for S3 key: %s", folder_prefix)
    
#     try:
#         # Fetch existing CSV file from S3
#         # obj = s3.get_object(Bucket=bucket_name, Key=f'{file_id}/{file_id}.csv')
#         # obj = s3.get_object(Bucket=bucket_name, Key=s3_key)
#         response = s3.list_objects_v2(Bucket=bucket_name, Prefix=folder_prefix)
        
#         if 'Contents' not in response:
#             logger.error("No files found in folder: %s", folder_prefix)
#             return {
#                 'statusCode': 404,
#                 'body': 'Policy file not found!'
#             }
            
#         # Find the file that matches the date
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
#                         return {
#                             'statusCode': 404,
#                             'body': f'Policy with ID {policy_id} not found!'
#                         }
#                 else:
#                     policy_data = df_existing

#                 policy_data_json = policy_data.to_dict(orient='records')
                
#                 return {
#                     'statusCode': 200,
#                     'body': policy_data_json
#                 }

#         logger.error("No matching files found in folder: %s", folder_prefix)
#         return {
#             'statusCode': 404,
#             'body': 'Policy file not found!'
#         }
#     except Exception as e:
#         logger.error("Error reading policy: %s", e)
#         return {
#             'statusCode': 500,
#             'body': f'Error reading policy: {str(e)}'
#         }

# def update_policy(event):
#     updated_policy_data = event['updated_policy_data']
#     date_str = event.get('date', datetime.now().strftime("%Y-%m-%d"))
#     folder_prefix = f'{date_str}/'
#     logger.info("Updating policy data in folder: %s", folder_prefix)
    
#     try:
#         # List all objects in the specified date folder
#         response = s3.list_objects_v2(Bucket=bucket_name, Prefix=folder_prefix)
#         if 'Contents' not in response:
#             logger.error("No files found in folder: %s", folder_prefix)
#             return {
#                 'statusCode': 404,
#                 'body': 'Policy file not found!'
#             }

#         # Find the file that matches the date
#         for obj in response['Contents']:
#             key = obj['Key']
#             if key.startswith(folder_prefix + date_str):
#                 logger.info("Found file: %s", key)
#                 obj = s3.get_object(Bucket=bucket_name, Key=key)
#                 df_existing = pd.read_csv(obj['Body'])

#                 # Convert updated policy data to DataFrame
#                 df_new = pd.DataFrame(updated_policy_data)

#                 # Update policy data in existing DataFrame
#                 df_updated = pd.concat([df_existing, df_new]).drop_duplicates(subset=['policy number'], keep='last')

#                 # Upload updated CSV file to S3
#                 upload_csv_to_s3(date_str, df_updated)

#                 # Update metadata in DynamoDB
#                 store_temp_metadata_update(date_str, len(df_updated))
                
#                 return {
#                     'statusCode': 200,
#                     'body': 'Policy updated successfully!'
#                 }

#         logger.error("No matching files found in folder: %s", folder_prefix)
#         return {
#             'statusCode': 404,
#             'body': 'Policy file not found!'
#         }
#     except Exception as e:
#         logger.error("Error updating policy: %s", e)
#         return {
#             'statusCode': 500,
#             'body': f'Error updating policy: {str(e)}'
#         }

# def delete_policy(event):
#     policy_id = event['policy number']
#     date_str = event.get('date', datetime.now().strftime("%Y-%m-%d"))
#     folder_prefix = f'{date_str}/'

#     logger.info("Deleting policy with ID: %s from folder: %s", policy_id, folder_prefix)
    
#     try:
#         # List all objects in the specified date folder
#         response = s3.list_objects_v2(Bucket=bucket_name, Prefix=folder_prefix)
#         if 'Contents' not in response:
#             logger.error("No files found in folder: %s", folder_prefix)
#             return {
#                 'statusCode': 404,
#                 'body': 'Policy file not found!'
#             }

#         # Find the file that matches the date
#         for obj in response['Contents']:
#             key = obj['Key']
#             if key.startswith(folder_prefix + date_str):
#                 logger.info("Found file: %s", key)
#                 obj = s3.get_object(Bucket=bucket_name, Key=key)
#                 df_existing = pd.read_csv(obj['Body'])

#                 # Delete policy data from existing DataFrame
#                 df_updated = df_existing[df_existing['policy number'] != policy_id]

#                 # Upload updated CSV file to S3
#                 upload_csv_to_s3(date_str, df_updated)

#                 # Update metadata in DynamoDB
#                 store_temp_metadata_update(date_str, len(df_updated))
                
#                 return {
#                     'statusCode': 200,
#                     'body': 'Policy deleted successfully!'
#                 }

#         logger.error("No matching files found in folder: %s", folder_prefix)
#         return {
#             'statusCode': 404,
#             'body': 'Policy file not found!'
#         }
#     except Exception as e:
#         logger.error("Error deleting policy: %s", e)
#         return {
#             'statusCode': 500,
#             'body': f'Error deleting policy: {str(e)}'
#         }


# def upload_csv_to_s3(file_id, csv_data):
#     logger.info("Uploading CSV to S3 with file ID: %s", file_id)
#     csv_buffer = StringIO()
#     csv_data.to_csv(csv_buffer, index=False)
#     # Create a folder structure based on the date
#     date_str = datetime.now().strftime("%Y-%m-%d")
#     s3_key = f'{date_str}/{file_id}.csv'
    
#     s3.put_object(Bucket=bucket_name, Key=s3_key, Body=csv_buffer.getvalue())
#     logger.info("CSV uploaded successfully to S3 at %s", s3_key)



# def store_temp_metadata_update(file_id, num_policies):
#     logger.info("Storing temporary metadata update for file ID: %s", file_id)
#     temp_table = dynamodb.Table(temp_table_name)
#     response = temp_table.put_item(
#         Item={
#             'policy_id': file_id,
#             'NumberOfPolicies': num_policies,
#             'UpdateTimestamp': datetime.utcnow().isoformat()
#         }
#     )


# def end_of_day_update():
#     logger.info("Starting end-of-day metadata update")
#     temp_table = dynamodb.Table(temp_table_name)
#     main_table = dynamodb.Table(table_name)
    
#     # Scan all items in the temporary metadata table
#     response = temp_table.scan()
#     items = response.get('Items', [])
    
#     # Update main metadata table
#     for item in items:
#         file_id = item['policy_id']
#         num_policies = item['NumberOfPolicies']
#         update_timestamp = item['UpdateTimestamp']
        
#         main_table.update_item(
#             Key={
#                 'policy_id': file_id
#             },
#             UpdateExpression='SET NumberOfPolicies = :np, UpdateTimestamp = :ut',
#             ExpressionAttributeValues={
#                 ':np': num_policies,
#                 ':ut': update_timestamp
#             }
#         )
    
#     # Clear the temporary metadata table
#     with temp_table.batch_writer() as batch:
#         for item in items:
#             batch.delete_item(
#                 Key={
#                     'policy_id': item['policy_id']
#                 }
#             )

#     logger.info("End-of-day metadata update completed successfully")
#     return {
#         'statusCode': 200,
#         'body': 'End-of-day metadata updated successfully!'
#     }
