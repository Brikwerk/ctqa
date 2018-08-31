"""
CTQA Config Utility

Utility for creating/saving/loading/updating a JSON configuration file.
"""
# Imports
import json
import re
import os
import logging
import copy
from ctqa import logutil
# Logger init
logger = logging.getLogger(logutil.MAIN_LOG_NAME)


# Constants
DEFAULT_PROFILE = {
  'StationName':'',
  'Manufacturer':'',
  'ManufacturerModelName':'',
  'InstitutionName':'',
  'HomogeneityPosition':0,
  'LinearityPosition':0,
  'Baseline': {
    'STD':False,
    'CENTER':False,
    'NORTH':False,
    'SOUTH':False,
    'EAST':False,
    'WEST':False
  }
}
MANF_LIST = ['GE MEDICAL SYSTEMS', 'DEFAULT']


def init(path):
  '''Initializes the profiles file to an empty JSON object and saves it.'''

  if not os.path.isfile(path):
    profiles = open(path, 'w+')
    profiles.write('{}')
    profiles.close()


def get(path, key):
  '''Gets the value from the passed key on the passed path'''

  prof = openProfiles(path)
  if type(prof) == dict:
    return prof.get(key)
  else:
    return -1


def keys(path):
  '''
  Returns a list of keys present in the top level of the profiles file.
  
  Returns -1 if the loaded profiles object isn't dict type.
  '''

  prof = openProfiles(path)
  if type(prof) == dict:
    return prof.keys()
  else:
    return -1


def numKeys(path):
  '''
  Returns the number of keys present in the top level of the profiles file.
  
  Returns -1 if the loaded profiles object isn't dict type.
  '''

  prof = openProfiles(path)
  if type(prof) == dict:
    keys = prof.keys()
    return len(list(keys))
  else:
    return -1


def removeProfile(path, key):
  '''Removes profile and returns the values/None. Returns -1 in the event of failure.'''

  prof = openProfiles(path)
  if type(prof) == dict:
    keyres = prof.pop(key, 'None')
    saveres = saveProfiles(path, prof)
    if saveres != 1:
      return saveres
    else:
      return keyres
  else:
    return -1


def getProfileName(profile):
  '''
  Assembles the profile ID based off of the profile keys.
  
  Returns -1 if one of the keys isn't present.
  '''

  if profile.keys() != DEFAULT_PROFILE.keys():
    return -1
  
  try:
    readerid = (
      profile['StationName']+'-'+
      profile['Manufacturer'].upper()+'-'+
      profile['ManufacturerModelName'].upper()+'-'+
      profile['InstitutionName'].upper()
    )
  except KeyError:
    return -1

  return readerid

def getDefaultProfile():
  '''Returns a deep copy of the default profile.'''

  profile = copy.deepcopy(DEFAULT_PROFILE)
  return profile


def validProfile(profile):
  '''Checks a profile for valid values in the present keys.'''

  if not isinstance(profile, dict):
    logger.error('Could not validate profile. Profile is not a dictionary object')
    return False

  for key in profile.keys():
    res = profile.get(key)
    if not isinstance(res, (str,int,dict)):
      logger.error('Could not validate profile. Profile attribute %s was not a valid value' % key)
      return False
    elif res == None:
      logger.error('Could not validate profile. Profile attribute %s cannot be none' % key)
      return False
    elif isinstance(res, str) and not len(res.strip()) > 0:
      logger.error('Could not validate profile. Profile attribute %s cannot be blank' % key)
      return False

  return True


def newProfile(path, readerid, statname, manfct, manfctname, instname):
  '''
  Creates a dict object from the DEFAULT_PROFILE dict object. This new dict object
  is filled out with the passed values and returned.

  If saving or opening the profiles file fails, a -1 is returned.
  '''

  prof = openProfiles(path)

  if type(prof) == dict:
    prof[readerid] = {}
    prof[readerid]['StationName'] = statname
    prof[readerid]['Manufacturer'] = manfct.upper()
    prof[readerid]['ManufacturerModelName'] = manfctname.upper()
    prof[readerid]['InstitutionName'] = instname.upper()
    prof[readerid]['HomogeneityPosition'] = 0
    prof[readerid]['LinearityPosition'] = 0
    prof[readerid]['Baseline'] = {
      'STD':False,
      'CENTER':False,
      'NORTH':False,
      'SOUTH':False,
      'EAST':False,
      'WEST':False
    }


    res = saveProfiles(path, prof)
    if res == 1:
      return prof
    else:
      logger.error("Unable to save new profile " + readerid)
      return -1
  else:
    logger.error("Unable to load profiles file")
    return -1


def openProfiles(path):
  '''
  Attempts to open the profiles file at the passed location.

  If a FileNotFound or JSONDecodeError is encountered, -1 is returned.
  '''

  PROFILES = None
  try:
    with open(path) as f: # Attempt to load the config file
      PROFILES = json.load(f)
      f.close()
  except FileNotFoundError: # If the file cannot be found, return 0
    logger.error("Could not find the file at " + path)
    return 0
  except json.decoder.JSONDecodeError:
    logger.error("Profiles file could not be decoded. Please provide a valid JSON file.")
    return -1
  
  return PROFILES


def saveProfiles(path, profiles):
  '''
  Attempts to save the passed profiles dict object to the passed path.

  If a FileNotFound error is encountered, -1 is returned.
  '''

  logger.debug("Saving profiles...")
  try:
    with open(path, 'w') as outfile:
      json.dump(profiles, outfile, indent=2)
      outfile.close()
  except FileNotFoundError:
    logger.error("Could not save or create profiles")
    return -1
  
  logger.debug("Profiles saved")
  return 1