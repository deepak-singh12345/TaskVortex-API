from time import time

from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
from fastapi.responses import JSONResponse

from app.repository.rate_limiter_repository import RateLimitingRepository

class RateLimiterMiddleware(BaseHTTPMiddleware):
    
    def __init__(self, app):
        super().__init__(app)
        self.repo = RateLimitingRepository()
        
    async def dispatch(self, request, call_next):
        if request.url.path == "/health":
            return await call_next(request)
        
        ip = request.client.host
        
        now = time()
        
        bucket = await self.repo.get_bucket(ip, now)
        
        allowed = bucket.consume(now)
        
        await self.repo.save_bucket(ip, bucket)
        
        if not allowed:
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Rate limit exceeded"
                },
            )
            
        return await call_next(request)