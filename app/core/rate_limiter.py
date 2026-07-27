


class TokenBucket:
    def __init__(
        self,
        capacity: int,
        refill_rate: float,
        timestamp: float,
    ):
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = capacity
        self.last_refill_time = timestamp
        
    @classmethod
    def from_state(cls, capacity: int, refill_rate: float, tokens: float, last_refill_time: float):
        bucket = cls(capacity, refill_rate, last_refill_time)
        bucket.tokens = tokens
        return bucket
        
    
    def consume(self, now: float) -> bool:
        self._refill(now)
        if self.tokens >= 1:
            self.tokens -= 1
            return True
        return False

    def _refill(self, now: float):
        elapsed_time = now - self.last_refill_time
        new_tokens = elapsed_time * self.refill_rate
        self.tokens = min(self.capacity, self.tokens + new_tokens)
        self.last_refill_time = now