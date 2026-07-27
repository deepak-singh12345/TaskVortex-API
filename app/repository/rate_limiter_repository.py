from app.core.rate_limiter import TokenBucket
from app.core.redis import redis_client
from app.core.config import settings

class RateLimitingRepository:
    def _get_key(self, ip: str) -> str:
        return f"rate_limit:{ip}"
    
    async def get_bucket(self, ip: str, now: float) -> TokenBucket:
        key = self._get_key(ip)
        data = await redis_client.hgetall(key)
        
        if not data:
            return TokenBucket(
                capacity=settings.RATE_LIMIT_CAPACITY,
                refill_rate=settings.RATE_LIMIT_REFILL_RATE,
                timestamp=now
            )
            
        return TokenBucket.from_state(
            capacity=settings.RATE_LIMIT_CAPACITY,
            refill_rate=settings.RATE_LIMIT_REFILL_RATE,
            tokens=float(data["tokens"]),
            last_refill_time=float(data['last_refill_time'])
        )
    
    async def save_bucket(self, ip: str, bucket: TokenBucket) -> None:
        key = self._get_key(ip)
        await redis_client.hset(
            key, 
            mapping={
                "tokens": bucket.tokens,
                "last_refill_time": bucket.last_refill_time
            },
        )
        await redis_client.expire(
            key, settings.RATE_LIMIT_TTL
        )
        