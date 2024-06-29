# Insurance-Policy-Management-System-with-AWS-Lambda-S3-DynamoDB-and-Pytest

The Insurance Policy Management System is an application built using AWS Lambda (Python), Amazon S3, and DynamoDB to automate and manage insurance policies efficiently. The primary purpose of this project is to learn and practice writing Pytests using mocking and patching techniques.

# Overview :

The Insurance Policy Management System is an application built using AWS Lambda (Python), Amazon S3, and DynamoDB to automate and manage insurance policies efficiently. The primary purpose of this project is to learn and practice writing Pytests using mocking and patching techniques. The system handles daily insurance policy records for various types of insurance (car, life, health), performs CRUD operations, and ensures data consistency across the S3 bucket and DynamoDB.

# Key Features :

1. Automated Daily Records: Every day, a new file is created in the S3 bucket that includes all the insurance policies initiated on that day.
2. CRUD Operations: Customers can create, read, update, and delete their policy information. These operations are reflected both in the CSV files stored in S3 and the corresponding metadata in DynamoDB.
3. Data Consistency: Any updates or deletions are processed at the end of the day, ensuring that the data in S3 and DynamoDB are synchronized.
4. Timestamp Management: The system tracks the creation and update timestamps, the user who updated the information, the file ID, and the number of policies.
5. End-of-Day Data Processing: Data is added to DynamoDB at the end of each day using a CloudWatch Event Rule to trigger the Lambda function.

# Technical Details :

1. AWS Lambda: Serves as the core processing unit for handling policy data. The Lambda function receives input from events and performs necessary operations.
2. Amazon S3: Stores the daily CSV files containing policy data. Each file is updated with new policies or modifications at the end of the day.
3. DynamoDB: Maintains metadata including timestamps, update information, and policy counts, ensuring quick access and management of policy data. Data is updated in DynamoDB at the end of the day.
4. CloudWatch Event Rule: Used as a scheduler to trigger the Lambda function at the end of the day, ensuring timely updates to DynamoDB.
5. Pytest with Mocking and Patching: The project uses the unittest framework to write Pytests, with AWS services being mocked using mocking techniques. This allows for comprehensive test coverage and reliable testing of the Lambda function and its interactions with AWS services.

# Testing :

Pytest: Comprehensive test coverage is ensured by writing Pytest test cases using the unittest framework, targeting to all code coverage. AWS services are mocked using mocking and patching techniques, ensuring reliability and robustness of the system.

# Contributions :

Contributions are welcome! Please fork the repository and create a pull request with detailed information on the changes.
