import sys
import logging
from threading import local

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

formatter = logging.Formatter(
    fmt="%(asctime)s - %(levelname)s [%(request_id)s | %(module)s.%(funcName)s:%(lineno)d]: %(message)s"
)

stream_handler = logging.StreamHandler(sys.stdout)
file_handler = logging.FileHandler("logs.log")

stream_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

logger.handlers = [stream_handler, file_handler]

# Thread-local storage to store request context
log_context = local()


# Custom logging filter to add request_id
class RequestIdFilter(logging.Filter):
    def filter(self, record):
        record.request_id = getattr(log_context, "request_id", "N/A")
        return True


# Add the filter to logger
logger.addFilter(RequestIdFilter())
