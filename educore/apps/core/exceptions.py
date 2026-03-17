"""
apps/core/exceptions.py

Consistent JSON error shapes across all endpoints.
All errors return:
{
  "error": true,
  "code": "VALIDATION_ERROR",
  "message": "Human-readable summary",
  "details": { ... }   # field-level errors for validation
}
"""
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is None:
        # Unhandled exception — log and return 500
        logger.exception('Unhandled exception in view %s', context.get('view'))
        return Response(
            {'error': True, 'code': 'SERVER_ERROR',
             'message': 'An unexpected error occurred. Please try again.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    code    = 'API_ERROR'
    message = 'Request failed.'
    details = {}

    if response.status_code == 400:
        code    = 'VALIDATION_ERROR'
        message = 'Validation failed. Please check the fields below.'
        details = response.data if isinstance(response.data, dict) else {'non_field_errors': response.data}

    elif response.status_code == 401:
        code    = 'UNAUTHORIZED'
        message = 'Authentication required. Please log in.'

    elif response.status_code == 403:
        code    = 'FORBIDDEN'
        message = 'You do not have permission to perform this action.'

    elif response.status_code == 404:
        code    = 'NOT_FOUND'
        message = 'The requested resource was not found.'

    elif response.status_code == 405:
        code    = 'METHOD_NOT_ALLOWED'
        message = f'Method not allowed on this endpoint.'

    elif response.status_code == 429:
        code    = 'THROTTLED'
        message = 'Too many requests. Please slow down.'

    response.data = {
        'error':   True,
        'code':    code,
        'message': message,
        'details': details,
    }
    return response
