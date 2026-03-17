"""
apps/core/middleware.py

Production middleware stack:
  1. RequestLogMiddleware  — logs every API request with latency
  2. AuditMiddleware       — records write operations (POST/PUT/PATCH/DELETE) to AuditLog
"""
import time
import logging
import json

logger = logging.getLogger('educore.requests')
audit_logger = logging.getLogger('educore.audit')


class RequestLogMiddleware:
    """
    Logs: method, path, status_code, user, latency_ms for every request.
    Skips static file requests.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/static/') or request.path.startswith('/media/'):
            return self.get_response(request)

        start = time.monotonic()
        response = self.get_response(request)
        latency  = round((time.monotonic() - start) * 1000, 1)

        user = getattr(request, 'user', None)
        username = user.username if user and user.is_authenticated else 'anonymous'

        level = logging.WARNING if response.status_code >= 400 else logging.INFO
        logger.log(level, '%s %s %s %sms user=%s',
                   request.method, request.path, response.status_code, latency, username)
        return response


class AuditMiddleware:
    """
    Records all write operations to an in-memory audit log (extend to DB model for persistence).
    Only logs API paths to avoid noise from admin/static.
    """
    WRITE_METHODS = {'POST', 'PUT', 'PATCH', 'DELETE'}

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if (request.method in self.WRITE_METHODS
                and request.path.startswith('/api/')
                and response.status_code < 400):

            user = getattr(request, 'user', None)
            username = user.username if user and user.is_authenticated else 'anonymous'

            audit_logger.info(
                'AUDIT | user=%s method=%s path=%s status=%s',
                username, request.method, request.path, response.status_code
            )

        return response
