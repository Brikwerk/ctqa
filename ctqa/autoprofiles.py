'''
Auto Profiles Module

A module that contains logic for automatically identifying CT reader profiles from a \
linked database.
'''

from . import confutil
from . import profileutil
from . import imgfetch
import os, sys, pydicom

# Constants
LOCATION = os.path.abspath(os.path.dirname(sys.argv[0]))
CONFPATH = LOCATION + '/config.json'
PROFPATH = LOCATION + '/profiles.json'
CONFIG = {}


def getSize():
  '''Gets size of all images from source'''

  # Reload config, in case any changes were made
  CONFIG = confutil.openConfig(CONFPATH)
  if type(CONFIG) == int:
    return -1
  else:
    size = imgfetch.getSizeOfImages(CONFIG)
    return size

# 
def run():
  '''Loops through all images and attempts to find new profiles.'''

  # Reload config, in case any changes were made
  CONFIG = confutil.openConfig(CONFPATH)
  #Ensuring the profileutil has been initialized
  profileutil.init(PROFPATH)
  # Checking for good config
  if type(CONFIG) == dict:
    images = imgfetch.getAllImages(CONFIG)
    for image in images:
      data = pydicom.dcmread(image)

      try:
        # Concatenating readerid from attrbs in data
        readerid = (
          data.StationName+'-'+
          data.Manufacturer.upper()+'-'+
          data.ManufacturerModelName.upper()+'-'+
          data.InstitutionName.upper()
        )
        
        # Checking if we don't have this profileid, if so, we create the profile
        if profileutil.get(PROFPATH, readerid) == None:
          # Assign default profile to new profile and populate
          res = profileutil.newProfile(
            PROFPATH,
            readerid,
            data.StationName,
            data.Manufacturer,
            data.ManufacturerModelName,
            data.InstitutionName
          )

          if res == -1:
            print("ERROR: Bad result from profile save. Please consult the log for more details.")
            break
      # If we don't have all the attributes, skip the image
      except AttributeError as e:
        print('Attribute Error on image in dataset: ', e)
        continue
  else:
    print('AUTO PROFILE CONFIG ERROR')
    return -1
