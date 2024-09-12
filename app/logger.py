import logging
import os
from typing import Any


# Create a custom logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create handlers
c_handler = logging.StreamHandler()
# f_handler = logging.FileHandler("data.log")
c_handler.setLevel(logging.DEBUG)
# f_handler.setLevel(logging.DEBUG)

# Create formatters and add it to handlers
c_format = logging.Formatter("%(name)s - %(levelname)s - %(message)s")
# f_format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
c_handler.setFormatter(c_format)
# f_handler.setFormatter(f_format)

# Add handlers to the logger
logger.addHandler(c_handler)
# logger.addHandler(f_handler)

# Get the logger for SQLAlchemy
sqlalchemy_logger = logging.getLogger("sqlalchemy.engine")

# Set the logging level to a high value to suppress logs
sqlalchemy_logger.setLevel(logging.WARNING)  # Adjust this level as needed

# Optionally, you can remove any existing handlers to completely stop SQLAlchemy logs
for handler in sqlalchemy_logger.handlers[:]:
    sqlalchemy_logger.removeHandler(handler)
