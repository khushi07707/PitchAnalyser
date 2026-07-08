import time
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

# Set up logging for API routes
logger = logging.getLogger("app.api_audit")

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        """
        Intercepts incoming HTTP requests to log their method, route, 
        processing time, and response status codes.
        """
        start_time = time.time()
        
        path = request.url.path
        query = request.url.query
        method = request.method
        
        full_route = f"{path}?{query}" if query else path
        logger.info(f"HTTP Request Started - Method: {method} | Path: {full_route} | Client: {request.client.host if request.client else 'Unknown'}")
        
        try:
            response = await call_next(request)
            duration = time.time() - start_time
            
            # Log successful processing metrics
            logger.info(
                f"HTTP Request Finished - Method: {method} | "
                f"Path: {path} | Status: {response.status_code} | "
                f"Duration: {duration:.4f}s"
            )
            return response
        except Exception as e:
            duration = time.time() - start_time
            # Log failure metrics and stack trace
            logger.error(
                f"HTTP Request Exception - Method: {method} | "
                f"Path: {path} | Error: {str(e)} | "
                f"Duration: {duration:.4f}s", 
                exc_info=True
            )
            raise e
