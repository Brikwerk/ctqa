"""
CTQA Logging Utility

Utility for creating/instantiating a logger.
"""

# Constants
MAIN_LOG_FILE_NAME = 'ctqa.log'
MAIN_LOG_NAME = 'ctqa'
LOG_FORMAT = '%(asctime)-15s | %(levelname)-8s: %(message)s' # Format for log
LOG_SIZE = 1000000 #In Bytes -> 1,000,000 Bytes = 1 MB
LOG_BACKUPS = 5

# Imports
import logging
from logging.handlers import RotatingFileHandler

def initLog(fileName, logName, debug):
  """Initializes the logger and returns the logger object."""

  # Configuring logger
  # If debug is flagged, allow for debug commands to print, else only show warnings and up
  if debug:
    logging.basicConfig(
      format=LOG_FORMAT,  
      handlers=[RotatingFileHandler(fileName, maxBytes=LOG_SIZE, backupCount=LOG_BACKUPS)],
      level=logging.DEBUG
    )
  else:
    logging.basicConfig(
      format=LOG_FORMAT,
      handlers=[RotatingFileHandler(fileName, maxBytes=LOG_SIZE, backupCount=LOG_BACKUPS)],
      level=logging.WARNING
    )

  logger = logging.getLogger(logName)
  
  logger.warning('\n')
  logger.warning('----------------------Log Started----------------------')
  logger.debug('-----DEBUG MODE ENABLED')
  
  return logger