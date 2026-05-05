"""JSON-structured logging. Production-ready out of the box."""
import logging
import sys
import json
from datetime import datetime


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            log["exception"] = self.formatException(record.exc_info)
        # Include any extra fields passed via logger.info("...", extra={"station_id": "X"})
        for key, value in record.__dict__.items():
            if key not in ("args", "msg", "levelname", "name", "exc_info", "exc_text",
                          "pathname", "filename", "module", "lineno", "funcName",
                          "created", "msecs", "relativeCreated", "thread", "threadName",
                          "processName", "process", "stack_info", "levelno", "message",
                          "taskName"):
                log[key] = value
        return json.dumps(log)


def setup_logging(level: str = "INFO") -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(level)