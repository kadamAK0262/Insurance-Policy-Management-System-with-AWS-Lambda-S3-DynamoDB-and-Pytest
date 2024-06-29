import json

class CustomException(Exception):
    """Base class for custom exceptions"""
    def __init__(self, status, errormsg, error_body):
        self.errormsg = errormsg
        self.status = status
        self.error_body = error_body

    def __str__(self):
        return json.dumps({
            "status": self.status,
            "error": self.errormsg,
            "message": self.error_body
        })

    def to_dict(self):
        """Convert error message to JSON format"""
        return {
            "status": self.status,
            "error": self.errormsg,
            "message": self.error_body
        }

class ValidationError(CustomException):
    """Exception for validation errors"""
    def __init__(self, status, error, message):
        self.status = status
        self.error = error
        self.message = message

    def to_dict(self):
        return {
            'status': self.status,
            'error': self.error,
            'message': self.message
        }

    def __str__(self):
        return str(self.to_dict())

class S3UploadError(CustomException):
    """Exception for S3 upload errors"""
    def __init__(self, status, error, message):
        self.status = status
        self.error = error
        self.message = message

    def to_dict(self):
        return {
            'status': self.status,
            'error': self.error,
            'message': self.message
        }

    def __str__(self):
        return str(self.to_dict())

class DynamoDBUpdateError(CustomException):
    """Exception for DynamoDB update errors"""
    def __init__(self, status, error, message):
        self.status = status
        self.error = error
        self.message = message

    def to_dict(self):
        return {
            'status': self.status,
            'error': self.error,
            'message': self.message
        }

    def __str__(self):
        return str(self.to_dict())

class DataNotFoundError(CustomException):
    """Exception for data not found errors"""
    def __init__(self, status, error, message):
        self.status = status
        self.error = error
        self.message = message

    def to_dict(self):
        return {
            'status': self.status,
            'error': self.error,
            'message': self.message
        }

    def __str__(self):
        return str(self.to_dict())

def build_exception_response(error):
    """Generic exception response"""
    return {
        "status": 500,
        "error": "Internal Server Error",
        "message": {"information": str(error)}
    }


