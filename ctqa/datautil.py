'''
Data Utility

Handles the saving and loading of CT QA data (audit results).
'''


# Imports
import json, io, os, sys

# Logging
import logging
from ctqa import logutil
logger = logging.getLogger(logutil.MAIN_LOG_NAME)


def save(DATA, savelocation):
  '''
  Saves all site's data from a dict object to the passed location
  
  Returns -1 if JSON data is malformed.
  '''

  for site in DATA['Homogeneity'].keys():
    # Checking if site has a directory under the 'data' directory
    folderpath = os.path.join(savelocation, site)
    if not os.path.exists(folderpath):
      os.makedirs(folderpath)
      print('Created:', folderpath)
    
    # Checking if the site contains a data.json file, if not we create it
    if not os.path.isfile(folderpath + '/data.json'):
      with open(folderpath + '/data.json', 'w') as outfile:
        tempdict = {'Homogeneity':{}, 'Linearity':{}}
        json.dump(tempdict, outfile, indent=2)
        outfile.close()

    # Load data.json file from folder path
    jsonData = load(folderpath)
    if jsonData == -1:
      return -1

    # Read new data into jsonData
    # Reading homogeneity data into jsonData
    for day in DATA['Homogeneity'][site].keys():
      dataset = DATA['Homogeneity'][site][day]
      jsonData['Homogeneity'][day] = dataset

    # Dumping jsonData back out
    with open(folderpath + '/data.json', 'w') as outfile:
      json.dump(jsonData, outfile, indent=2)
      outfile.close()


def load(folderpath):
  '''
  Loads CT QA data from the file on the passed path.

  Returns -1 if JSON data is malformed.
  '''
  jsonData = None
  with open(folderpath + '/data.json') as infile:
    try:
      jsonData = json.load(infile)
    except json.JSONDecodeError:
      logger.error('Unable to decode data.json file for site ' + str(folderpath))
      return -1
    except io.UnsupportedOperation:
      logger.error('Unable to load data.json file for site ' + str(folderpath))
      return -1
    finally:
      infile.close()
  if jsonData == None:
    logger.error('Unable to decode or load data.json file for site ' + str(folderpath))
    return -1

  return jsonData