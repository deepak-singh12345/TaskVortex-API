import json
import logging
import queue
from contextvars import ContextVar
from datetime import datetime, UTC
from logging.handlers import QueueHandler, QueueListener
from typing import Any


trace_id_var: ContextVar[str] = ContextVar("trace_id", default="-")

class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_record = {
            "timestamp" : datetime.now(UTC).isoformat(timespec="milliseconds"),
            "level": record.levelname,
            "message": record.getMessage(),
            "trace_id": getattr(record, "trace_id", "-"),
            "logger_name": record.name,
            "file_name": record.filename,
            "line_number": record.lineno,
            "function": record.funcName,
            "module": record.module,
            "process": record.process,
            "thread": record.threadName,
            "context": getattr(record, "context", {})
        }
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
            
        return json.dumps(log_record, default=str)
    
class TraceIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.trace_id = trace_id_var.get()
        return True
    
log_queue: queue.Queue[logging.LogRecord] = queue.Queue()

queue_handler = QueueHandler(log_queue)
queue_handler.addFilter(TraceIdFilter())

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(JsonFormatter())

listener = QueueListener(log_queue, stream_handler)

def setup_logging() -> None:
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    root_logger.handlers.clear()
    
    root_logger.addHandler(queue_handler)
    
    listener.start()