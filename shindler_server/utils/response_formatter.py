"""
Response formatting utilities for consistent API responses
"""

from typing import Dict, Any, Optional


class ResponseFormatter:
    """Utility class for formatting consistent API responses"""

    @staticmethod
    def format_response(
        message: str,
        status_code: int,
        body: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Format a generic API response with any status code

        Args:
            message: Response message
            status_code: HTTP status code (any valid code)
            body: Response body data (optional)

        Returns:
            Formatted response dictionary
        """
        return {
            "status_code": status_code,
            "message": message,
            "body": body or {}
        }

    @staticmethod
    def success_response(
        message: str,
        body: Optional[Dict[str, Any]] = None,
        status_code: int = 200
    ) -> Dict[str, Any]:
        """
        Format a successful API response

        Args:
            message: Success message
            body: Response body data (optional)
            status_code: HTTP status code (default: 200)

        Returns:
            Formatted response dictionary
        """
        return ResponseFormatter.format_response(
            message=message,
            status_code=status_code,
            body=body
        )

    @staticmethod
    def error_response(
        message: str,
        body: Optional[Dict[str, Any]] = None,
        status_code: int = 500
    ) -> Dict[str, Any]:
        """
        Format an error API response

        Args:
            message: Error message
            body: Additional error details (optional)
            status_code: HTTP status code (default: 500)

        Returns:
            Formatted error response dictionary
        """
        return ResponseFormatter.format_response(
            message=message,
            status_code=status_code,
            body=body
        )

    @staticmethod
    def client_error_response(
        message: str,
        status_code: int = 400,
        body: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Format a client error response (4xx)

        Args:
            message: Error message
            status_code: HTTP status code (default: 400)
            body: Additional error details (optional)

        Returns:
            Formatted error response dictionary
        """
        return ResponseFormatter.format_response(
            message=message,
            status_code=status_code,
            body=body
        )

    @staticmethod
    def server_error_response(
        message: str,
        status_code: int = 500,
        body: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Format a server error response (5xx)

        Args:
            message: Error message
            status_code: HTTP status code (default: 500)
            body: Additional error details (optional)

        Returns:
            Formatted error response dictionary
        """
        return ResponseFormatter.format_response(
            message=message,
            status_code=status_code,
            body=body
        )
    

