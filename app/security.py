import logging
import os


# Store the security log in the project root
BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

LOG_FILE = os.path.join(
    BASE_DIR,
    "secureauth_security.log"
)


security_logger = logging.getLogger("secureauth.security")

security_logger.setLevel(logging.INFO)


# Prevent duplicate handlers
if not security_logger.handlers:

    handler = logging.FileHandler(LOG_FILE)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s"
    )

    handler.setFormatter(formatter)

    security_logger.addHandler(handler)


def log_security_event(event, username=None, details=None):

    message = f"EVENT={event}"

    if username:
        message += f" | USER={username}"

    if details:
        message += f" | DETAILS={details}"

    security_logger.info(message)

    # Make sure the event is immediately written to disk
    for handler in security_logger.handlers:
        handler.flush()