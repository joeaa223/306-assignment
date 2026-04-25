import time
import logging

logger = logging.getLogger(__name__)

class PerformanceMonitoringMiddleware:
    """
    Middleware to measure and log the response time of each request.
    Used for Topic 9: Performance Improvement comparison.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Start timer
        start_time = time.time()

        response = self.get_response(request)

        # Calculate duration
        duration = time.time() - start_time
        
        # Log to terminal
        duration_ms = duration * 1000
        print(f"DEBUG: [Performance] {request.method} {request.path} took {duration_ms:.2f}ms")
        
        # Add a custom header for verification in browser tools
        response['X-Response-Time-Ms'] = f"{duration_ms:.2f}"

        return response
