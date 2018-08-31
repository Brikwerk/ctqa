"""
Image Fetcher

Module for selecting/loading images from the appropriate source/module.
"""

import sys, os
from ctqa.sources import orthanc as orthanc

#Logging
import logging
from ctqa import logutil
logger = logging.getLogger(logutil.MAIN_LOG_NAME)


def resource_path(relative_path):
  '''Fetches application resource paths.'''

  if hasattr(sys, '_MEIPASS'):
    #ifndef __INTELLISENSE__
    return os.path.join(sys._MEIPASS, relative_path)
  return os.path.join(os.path.abspath("."), relative_path)


def getImages(conf):
  '''
  Based off of the Source attribute in passed config, an image source is used to fetch a list of new image paths.
  
  Returns -1 if the source is bad.
  '''

  if conf.get("Source") == 'ORTHANC':
    imgs = orthanc.fetchImages(conf["OrthancRESTAddress"], conf["LastImageNumber"])
    return imgs
  elif conf.get("Source") == 'TEST':
    return getTestImgs()
  else:
    logger.error("Invalid source passed. Please enter a valid source in the configuration.")
    return -1


def getAllImages(conf):
  '''
  Gets a list of all image paths from the image source. The source is based off of the value from passed config.
  
  Returns -1 if the source is bad.
  '''

  if conf.get("Source") == 'ORTHANC':
    imgs = orthanc.fetchImages(conf["OrthancRESTAddress"], conf["LastImageNumber"], profileinit=True)
    return imgs
  elif conf.get("Source") == 'TEST':
    return getTestImgs()
  else:
    logger.error("Invalid source passed. Please enter a valid source in the configuration.")
    return -1


def getSizeOfImages(conf):
  '''
  Gets the size of all images from images source based off of the passed configuration.
  
  Returns -1 if the source is bad.
  '''

  if conf.get("Source") == 'ORTHANC':
    num = orthanc.getSizeOfImages(conf["OrthancRESTAddress"])
    return num
  elif conf.get("Source") == 'TEST':
    return 1.5
  else:
    logger.error("Invalid source passed. Please enter a valid source in the configuration.")
    return -1

def getTestImgs():
  '''Gets application test image paths.'''

  return [
    resource_path("test/data/imgA.dcm"),
    resource_path("test/data/imgB.dcm"), 
    resource_path("test/data/imgC.dcm")
  ]