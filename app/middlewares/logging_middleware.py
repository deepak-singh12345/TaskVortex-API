import time
import uuid 

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from app.core import logging
from app.core.logging import trace_id_var
import logging

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        trace_id = request.headers.get("X-Trace-Id") or uuid.uuid4().hex
        
        token = trace_id_var.set(trace_id)
        
        logger = logging.getLogger(__name__)

        logger.info(
            "Middleware trace id set",
            extra={
                "context": {
                    "trace_id_from_context": trace_id_var.get()
                }
            }
        )
        
        try:
            response = await call_next(request)

            response.headers["X-Trace-Id"] = trace_id
            return response
        finally:
            trace_id_var.reset(token)
        