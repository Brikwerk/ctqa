"""
Title:.........Runner
Description: Runner file for starting program execution.
"""

# Imports
import sys
import os
import json
import logging
from ctqa import app, logutil, confutil, firstrun, profileutil
import ctqa.gui as client

#Constants
LOCATION = os.path.abspath(os.path.dirname(sys.argv[0]))
CONFIG = None # Stores config JSON file

# Flags
__AUDIT = False # Switches to audit run
__SERVICE = False # Switches to service run
__DEBUG = False # Allows debug logging
__SAVEROIS = False # Used for saving ROIs of a single dicom image

# Setting flags
if "--audit" in sys.argv:
  __AUDIT = True
  
if '--debug' in sys.argv:
  __DEBUG = True

# Determining which type of run we want
#--------------------------------------
# 0 - Default client run
# 1 - Audit run
#--------------------------------------
__RUNTYPE = 0
if __AUDIT:
  __RUNTYPE = 1

def main():
  # Setup
  logPath = LOCATION + "/" + logutil.MAIN_LOG_FILE_NAME
  logutil.initLog(logPath, logutil.MAIN_LOG_NAME, __DEBUG)

  confPath = LOCATION + "/" + confutil.DEFAULT_CONFIG_LOCATION
  config = confutil.loadConfig(confPath)

  logger = logging.getLogger(logutil.MAIN_LOG_NAME)
  logger.debug("Config Location: %s", confPath)
  logger.debug("Log Location: %s", logPath)

  profileutil.init(LOCATION + '/profiles.json')
  profiles = profileutil.openProfiles(LOCATION + '/profiles.json')

  # Ensuring data folder exists. If not, they are created.
  if not os.path.isdir(LOCATION + "/data"):
    os.makedirs(LOCATION + '/data')
  
  # Choose and run
  # Check for first run if not a service call
  frconf = confutil.openConfig(confPath) # Checking config file without validation
  if type(frconf) == dict and (frconf.get("FirstRun") == True and not __SERVICE):
    firstrun.run()
  elif __RUNTYPE == 1: # Audit run
    try:
      app.run(config, profiles, __DEBUG)
    except Exception as e:
      logger.error(e)
  else: # Client Run
    client.app.run()


if __name__ == "__main__":
  main()