import time
import uuid
from typing import Callable

from django.http import HttpRequest, HttpResponse
from django.utils.deprecation import MiddlewareMixin


class SimpleLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        print(f"Request path: {request.path}")
        response = self.get_response(request)
        return response


# SR[20260322]: custom middleware to monitor requests performance
class RequestTelemetryMiddleware:
    """
    Middleware to inject a unique Request-ID and measure execution performance.

    This follows the modern functional middleware pattern introduced in Django 1.10+.
    """

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request: HttpRequest) -> HttpResponse:
        """
        Main logic executed for each request.

        Args:
            request: The incoming Django HttpRequest object.

        Returns:
            The resulting HttpResponse object with telemetry headers.
        """
        request.request_id = str(uuid.uuid4())
        start_time = time.perf_counter()

        response = self.get_response(request)
        duration = time.perf_counter() - start_time

        # Add telemetry to the response headers for the client
        response["X-Request-ID"] = request.request_id
        response["X-Execution-Time-Seconds"] = f"{duration:.4f}"

        # Print to console
        print(
            f">>: [{request.request_id}] {request.method} {request.path} - {duration:.4f}s"
        )

        return response
