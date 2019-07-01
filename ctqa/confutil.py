"""
CTQA Config Utility

Utility for creating/saving/loading/updating a JSON configuration file.
"""
# Imports
import json
import re
import os
import logging
from ctqa import logutil

# Constants
DEFAULT_CONFIG = {
  "Source" : "",
  "OrthancRESTAddress" : "",
  "LastImageNumber" : 0,
  "FirstRun" : True,
  "LastRun" : "",
  "DaysToForecast": 60,
  "DailyReportDaysToGraph": 365,
  "WeeklyReportDaysToGraph": 90,
  "LastPACSDateChecked": False,
  "ReportLocation": "./reports",
  "ServicesInstalled": False
}
DEFAULT_CONFIG_LENGTH = 3
DEFAULT_CONFIG_LOCATION = 'config.json'
SOURCE_LIST = ['ORTHANC', 'TEST']

#Logger init
logger = logging.getLogger(logutil.MAIN_LOG_NAME)


def loadConfig(path):
  '''
  Attempts to load json config named/specced from path

  Returns the JSON config or -1 (Bad validation)
  '''

  CONFIG = openConfig(path)
  if CONFIG == -1:
    return CONFIG
  elif CONFIG == 0:
    createConfig(path)
    return CONFIG
    
  # Ensuring that config has valid values before returning
  validation = validateConfig(CONFIG)
  if validation == -1:
    return -1
  
  logger.debug(CONFIG)
  
  return CONFIG


def openConfig(path):
  '''
  Attempts to open the file at the passed path. Returns a dict object if found
  and parsed successfully.

  Catches errors for FileNotFound (returns 0) and JSONDecodeError (returns -1).
  '''

  CONFIG = None
  try:
    with open(path) as f: # Attempt to load the config file
      CONFIG = json.load(f)
      f.close()
  except FileNotFoundError: # If the file cannot be found, return 0
    return 0
  except json.decoder.JSONDecodeError:
    logger.error("Config file could not be decoded. Please provide a valid JSON file.")
    return -1
  
  return CONFIG
  

def saveConfig(path, config):
  '''
  Attempts to save the passed config at the passed path.

  Returns 1 on success and -1 on a FileNotFound error.
  '''

  logger.debug("Saving config...")
  try:
    with open(path, 'w') as outfile:
      json.dump(config, outfile, indent=2)
      outfile.close()
  except FileNotFoundError:
    logger.error("Could not save or create config")
    return -1
  
  logger.debug("Config saved")
  return 1


# 
def createConfig(path):
  '''
  Creates JSON config file with the specified name and path.
  Defaults to the name config.json and stores at root.
  '''

  logger.error("Creating config...")
  try:
    with open(path, 'w') as outfile:
      json.dump(DEFAULT_CONFIG, outfile, indent=2)
      outfile.close()
  except FileNotFoundError:
    logger.error("Could not create config. The path specified is inavlid")
    return -1
  
  logger.error("Config file was created. Please fill it out with your settings.")
  
  
def updateConfig(path, key, value):
  '''
  Updates a config file at the passed path with the specified key : value pair.

  Returns 1 on success and -1 on failure (Key doesn't exist or was unable to save file).
  All errors are logged.
  '''

  logger.warning("Updating %s with key: %s and value: %s", path, key, value)
  CONFIG = openConfig(path)
  if CONFIG == 0 or CONFIG == -1:
    logger.error("Could not load config for key/value update")
    return CONFIG
  
  if CONFIG.get(key) != None:
    CONFIG[key] = value
  else:
    logger.error("Could not update config. Passed key does not exist!")
    return -1
  
  res = saveConfig(path, CONFIG)
  if res == -1:
    logger.error("Could not save updated config!")
    return -1
  
  return 1
    

# 
def validateConfig(conf):
  '''Attempts to validate passed dictionary object according to config standards.'''

  # Defining properties of a valid config
  url_regex = re.compile(
  r'^(?:http|ftp)s?://' # http:// or https://
  r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
  r'localhost|' #localhost...
  r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
  r'(?::\d+)?' # optional port
  r'(?:/?|[/?]\S+)$', re.IGNORECASE)
  
  # Checking for a dict object
  if not isinstance(conf, dict):
    logger.error("Config passed to validation was a %s object, not a dictionary object (JSON)", type(conf))
    return -1
  
  # Checking that there is at least the number of default keys in config
  if len(conf) < DEFAULT_CONFIG_LENGTH:
    logger.error("Config does not contain all required fields")
    return -1
  
  # Testing that all DEFAULT_CONFIG keys are present in passed config
  for key in DEFAULT_CONFIG.keys():
    try:
      conf[key]
    except KeyError:
      logger.error("Config does not contain key %s", key)
      return -1
  
  # Checking for supported source
  if conf.get("Source") not in SOURCE_LIST:
    #Checking that the source isn't blank
    if conf.get("Source") == '':
      logger.error("Please fill in the source with one of the appropriate value: [%s]" % ', '.join(map(str, SOURCE_LIST)))
      return -1
    #If the source if filled, we report that it is an unsupported value
    logger.error("Image source is unsupported. Please use one of sources: [%s]" % ', '.join(map(str, SOURCE_LIST)))
    return -1

  # Checking for valid forecast/graph days
  if not isinstance(conf.get("DaysToForecast"), int) or not isinstance(conf.get("DailyReportDaysToGraph"), int) or not isinstance(conf.get("WeeklyReportDaysToGraph"), int):
    logger.error("DaysToForecast/Graph is not an int value")
    return -1
  elif not conf.get('DaysToForecast') >= 0 or not conf.get('DailyReportDaysToGraph') >= 0 or not conf.get('WeeklyReportDaysToGraph') >= 0:
    logger.error('DaysToForecast/Graph must be greater than zero')
    return -1

  # Checking that LastPACSDateChecked is a valid value (string or boolean)
  if not isinstance(conf.get("LastPACSDateChecked"), bool):
    if not isinstance(conf.get("LastPACSDateChecked"), str):
      logger.error("LastPACSDateChecked is not boolean or string")
      return -1
  
  # Checking that Orthanc config values are valid
  if conf.get("Source") == 'ORTHANC':
    logging.debug("Orthanc source found during validation. Checking for approriate URL...")
    if conf.get("OrthancRESTAddress") in ['', None] or re.match(url_regex, conf["OrthancRESTAddress"]) is None:
      logger.error("The Orthanc REST Server address '%s' is malformed. Please edit the config with an appropriate URL.", conf["OrthancRESTAddress"])
      return -1
    else:
      try:
        int(conf.get("LastImageNumber"))
      except ValueError:
        return -1
  
  logging.debug("Config passed validation")
  
  return 1

  