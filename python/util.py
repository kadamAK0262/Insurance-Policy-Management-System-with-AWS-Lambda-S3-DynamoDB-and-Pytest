import boto3
import pandas as pd
from io import StringIO
from datetime import datetime
import logging

from python.exceptionss import DynamoDBUpdateError, S3UploadError

logger = logging.getLogger()

def upload_csv_to_s3(file_id, csv_data, bucket_name):
    logger.info("Uploading CSV to S3 with file ID: %s", file_id)
    csv_buffer = StringIO()
    csv_data.to_csv(csv_buffer, index=False)
    date_str = datetime.now().strftime("%Y-%m-%d")
    s3_key = f'{date_str}/{file_id}.csv'
    
    try:
        s3 = boto3.client('s3')
        s3.put_object(Bucket=bucket_name, Key=s3_key, Body=csv_buffer.getvalue())
        logger.info("CSV uploaded successfully to S3 at %s", s3_key)
    
    except Exception as e:
        logger.error("Error uploading CSV to S3: %s", e)
        raise S3UploadError(500, 'S3 Upload Error', f'Failed to upload CSV to S3: {str(e)}')


def store_temp_metadata_update(file_id, num_policies, temp_table_name, dynamodb):
    logger.info("Storing temporary metadata update for file ID: %s", file_id)
    temp_table = dynamodb.Table(temp_table_name)

    try:
        response = temp_table.put_item(
            Item={
                'policy_id': file_id,
                'NumberOfPolicies': num_policies,
                'UpdateTimestamp': datetime.utcnow().isoformat()
            }
        )
        logger.info("Temporary metadata stored successfully for file ID: %s", file_id)
    
    except Exception as e:
        logger.error("Error storing temporary metadata update: %s", e)
        raise DynamoDBUpdateError(500, 'DynamoDB Update Error', f'Failed to store temporary metadata update: {str(e)}')


def end_of_day_update(temp_table_name, table_name, dynamodb):
    logger.info("Starting end-of-day metadata update")
    temp_table = dynamodb.Table(temp_table_name)
    main_table = dynamodb.Table(table_name)


    try:
        response = temp_table.scan()
        items = response.get('Items', [])
        
        for item in items:
            file_id = item['policy_id']
            num_policies = item['NumberOfPolicies']
            update_timestamp = item['UpdateTimestamp']
            
            main_table.update_item(
                Key={
                    'policy_id': file_id
                },
                UpdateExpression='SET NumberOfPolicies = :np, UpdateTimestamp = :ut',
                ExpressionAttributeValues={
                    ':np': num_policies,
                    ':ut': update_timestamp
                }
            )
        
        with temp_table.batch_writer() as batch:
            for item in items:
                batch.delete_item(
                    Key={
                        'policy_id': item['policy_id']
                    }
                )

        logger.info("End-of-day metadata update completed successfully")
    
    except Exception as e:
        logger.error("Error in end-of-day metadata update: %s", e)
        raise DynamoDBUpdateError(500, 'DynamoDB Update Error', f'Failed end-of-day metadata update: {str(e)}')
    
