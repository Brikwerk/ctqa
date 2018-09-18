"""
Orthanc Image Source

Source module that fetches images from a specified Orthanc PACS server instance.
"""

import urllib.request
import shutil
import tempfile
import httplib2
import http
import sys, os
import json
import logging

from ctqa import confutil as confutil
from ctqa import logutil as logutil

if (sys.version_info >= (3, 0)):
    from urllib.parse import urlencode
else:
    from urllib import urlencode
    
#Logger init
logger = logging.getLogger(logutil.MAIN_LOG_NAME)

LOCATION = os.path.abspath(os.path.dirname(sys.argv[0]))


def getSizeOfImages(address):
  '''
  Returns size of all images present on the Orthanc server

  Returns -1 if there is an error with the URL parsing or the HTTP request.
  '''

  try:
    with urllib.request.urlopen(address + '/statistics') as response:
      try:
        res = json.load(response)
        return res['TotalUncompressedSizeMB'] 
      except json.decoder.JSONDecodeError:
        logger.error('Unable to decode ORTHANC statistics page as JSON')
        return -1
  except http.client.InvalidURL:
    logger.error("Unable to decode ORTHANC address")
    return -1
  except urllib.error.URLError as e:
    logger.error(e)
    return -1


def fetchImages(URL, lastImageNumber, profileinit=False):
  '''Retreives image URLs from an Orthanc server instance through the REST API'''

  if not profileinit: # We want only the latest slice if not profile init
    start = lastImageNumber
  else:
    start = 0
  imgURLs = []
  
  # Looping through all images after the passed image number and
  # adding their paths to an array.
  while True:
    r = get(URL + '/changes', {
      'since' : start,
      'limit' : 16   # Retrieve at most 16 changes at once
      })

    if len(r['Changes']) is 0:
      start = r['Last']
      break
    
    start = r['Last']
    for change in r['Changes']:
      # We are only interested interested in the arrival of new instances
      if change['ChangeType'] == 'NewInstance':
        # Store imgs in the imgs array
        path = change['Path']
        imgURLs.append(path)
  
  logger.debug("Fetched Orthanc image urls")
  logger.debug("Downloading images...")
  
  images = []
  for imgurl in imgURLs:
    with urllib.request.urlopen(URL + imgurl + '/file') as response:
      logger.debug("Downloading image from: %s", (URL + imgurl + '/file'))
      with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
          shutil.copyfileobj(response, tmp_file)
          images.append(tmp_file.name)
          
  logger.debug("Retrieved/stored images: %s", images)
  
  # If this isn't a profile initialization run from the auto-profiler
  if not profileinit:
    configpath = os.path.join(LOCATION, confutil.DEFAULT_CONFIG_LOCATION)
    confutil.updateConfig(configpath, "LastImageNumber", start)  
  
  return images


def get(baseURL, data = {}):
  '''
  Gets site contents and attempts to parse them as JSON data.
  
  Optiona data parameter for get requests.
  '''

  getURL = ''
  if len(data.keys()) > 0:
      getURL = '?' + urlencode(data)

  http = httplib2.Http()
  resp, respData = http.request(baseURL + getURL, 'GET')
  
  if not (resp.status in [ 200 ]):
      raise Exception(resp.status)
  else:
      return decodeJSON(respData)
      
      
def decodeJSON(strJSON):
  '''Decodes JSON in a manner safe for Python 2 and 3'''
  try:
      if (sys.version_info >= (3, 0)):
          return json.loads(strJSON.decode())
      else:
          return json.loads(strJSON)
  except:
      return strJSON