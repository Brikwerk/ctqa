'''
Audit Utility

A module that contains logic for running an audit, grouping images \
by series, and running homogeneity/linearity calculations.
'''

# Imports
import pydicom
import numpy as np
from . import profileutil
from . import auditmethods
from . import phantomcenter as phantom
import cv2
import json
import os
import io
import sys
import math
import time

# Logging
import logging
from ctqa import logutil
logger = logging.getLogger(logutil.MAIN_LOG_NAME)

# Constants
SERIES_TO_DISCARD = ["Dose Report", "Res", "LCD", "Dose Record"]
LOCATION = os.path.abspath(os.path.dirname(sys.argv[0]))
PROFPATH = LOCATION + "/profiles.json"
PROFILES = profileutil.openProfiles(PROFPATH)
DATA = {
  "Homogeneity":{},
  "Linearity":{}
}

def run(profiles, imgs):
  '''Main function for running the audit.'''

  if len(profiles) < 1: # If we've got no profiles, exit
    logger.warning('No profiles were found. Exiting audit...')
    return

  #Setting profiles global
  global PROFILES
  PROFILES = profiles

  # Getting grouped images
  series = groupSeries(imgs)

  # Organizing image series
  auditdatasets = getAuditDatasets(series)

  # Auditing images
  auditImages(auditdatasets)
  logger.debug(DATA)
  
  return DATA
  

def groupSeries(imgs):
  '''Function for grouping passed images by their series UID'''
  # Preparing studies dict for returning
  SERIES = {}

  # Iterating through imgs to organize by study
  for img in imgs:
    data = pydicom.dcmread(img)

    try:
      # Ensure that we're organizing the QC image series that we want
      if not data.SeriesDescription in SERIES_TO_DISCARD:
        # Ensuring data has all the tags we need. If not, we discard
        if hasattr(data, 'PixelSpacing') and \
        hasattr(data, 'StudyDate') and \
        hasattr(data, 'StationName') and \
        hasattr(data, 'Manufacturer') and \
        hasattr(data, 'ManufacturerModelName') and \
        hasattr(data, 'InstitutionName') and \
        hasattr(data, 'RescaleSlope') and \
        hasattr(data, 'RescaleIntercept') and \
        hasattr(data, 'pixel_array') and \
        hasattr(data, 'PatientBirthDate'):
          # Checking that the image has NO birthdate
          if data.PatientBirthDate == '':
            # Organizing by Series UID in dict object. Data appended into list.
            seriesUID = data.SeriesInstanceUID
            if SERIES.get(seriesUID) == None: # If list doesn't exist
              SERIES[seriesUID] = []
              SERIES[seriesUID].append(data)
            else: # List does exist
              SERIES[seriesUID].append(data)

    except AttributeError as e: # Passing over any img w/o UID
      logger.error('Attribute Error on image in dataset: ' + str(e))
      continue

  return SERIES


def getAuditDatasets(series):
  '''
  Selects a specified slice from a series based off of a value in 
  a reader's profile
  '''

  AUDIT_IMAGES = []
  global PROFILES

  # Iterating over each study and auditing chosen slices
  for uid in series.keys():
    logger.debug('Series UID: ' + uid + ' ' + str(len(series)) + ' images')
    # Accessing list of images for the series
    instances = series[uid]

    # Concatenating readerid from attrbs in data
    try:
      reader = (
        instances[0].StationName+'-'+
        instances[0].Manufacturer.upper()+'-'+
        instances[0].ManufacturerModelName.upper()+'-'+
        instances[0].InstitutionName.upper()
      )
    except AttributeError as e:
      logger.error(str(e) + ' in series ' + str(uid))
      continue

    # Creating a default profile if the reader doesn't exist
    if not PROFILES.get(reader):
      logger.error(reader + ' not found in profiles. Creating default profile...')
      profileutil.newProfile(
        PROFPATH,
        reader,
        instances[0].StationName,
        instances[0].Manufacturer,
        instances[0].ManufacturerModelName,
        instances[0].InstitutionName)
      PROFILES = profileutil.openProfiles(PROFPATH)

    # Reading profile into local var
    profile = PROFILES[reader]

    # Getting images at preferred slice location
    homogeneityimage = None
    linearityimage = None
    for instance in instances:
      if int(instance[0x20,0x1041].value) == profile["HomogeneityPosition"]:
        homogeneityimage = instance
      if int(instance[0x20,0x1041].value) == profile["LinearityPosition"]:
        linearityimage = instance      

    #Assigning to AUDIT_IMAGES
    AUDIT_IMAGES.append([reader, profile, homogeneityimage, linearityimage])

  return AUDIT_IMAGES


def auditImages(datasets):
  '''
  Retrieves audit method based off of the reader's manufacturer and
  performs appropriate audits based on this.

  Input, *datasets*, is expected to be a 2D array. The function loops
  through each element on the first level and executes the audits based on
  the contents of the second level array.

  Expected Contents of Second Level Array:

  [ MACHINE_NAME , MACHINE_PROFILE , MACHINE_QC_IMAGE ]
  
  **Please Note:** MACHINE_QC_IMAGE is referring to a pydicom dicom object.
  '''

  profile = None
  for dataset in datasets:
    try:
      profile = dataset[1]
      manufacturer = profile["Manufacturer"]
      method = auditmethods.getMethod(manufacturer)

      logger.debug("Auditing " + dataset[0])
      
      performHomogeneityAudit(method, dataset[2])

    except Exception as e:
      if profile:
        logger.error("Error during audit of machine %s" % profileutil.getProfileName(profile))
      logger.error(str(e))
    

#----------------------------------------------------------------------------------
#----------------------------------------------------------------------------------
# HOMOGENEITY METHODS
#----------------------------------------------------------------------------------
#----------------------------------------------------------------------------------


def performHomogeneityAudit(method, img):
  '''
  Prepares a spot in the global data variable (runs setupHomogeneityData) for data
  coming from the audits and runs each audit listed under the method parameter. \
  The output of each method is stored under the StudyDate (DICOM tag).\
  '''

  global DATA
  # Getting reader from img
  reader = None
  try:
    reader = (
      img.StationName+'-'+
      img.Manufacturer.upper()+'-'+
      img.ManufacturerModelName.upper()+'-'+
      img.InstitutionName.upper()
    )
  except AttributeError as e:
    if hasattr(img, "SeriesInstanceUID"):
      logger.error(str(e) + ' in series ' + str(img.SeriesInstanceUID))
    else:
      logger.error(str(e) + ' in image ' + str(img))
    return

  # Getting img date
  date = img.StudyDate
  # Preparing a spot in the dict object for audit results from img
  setupHomogeneityData(method, img, date, reader)
  # Creating alias for data location in DATA global
  dataloc = DATA["Homogeneity"][reader][date]

  # Running homogeneity audit for each audit
  for auditKey in method:
    logger.debug("Running " + auditKey)
    audit = method[auditKey]
    logger.debug("Audit has stats: %s" % audit)

    roi = computeHomogeneity(audit, img)
    if audit["direction"] == "CENTER":
      # Recording center value
      dataloc["CENTER"]["MEAN"] = np.mean(roi)
      dataloc["CENTER"]["STD"] = np.std(roi)
    else:
      # Recording peripheral value
      dataloc["PERIPHERAL"][audit["direction"]] = np.mean(roi)
  
  # Calculating peripheral comparisons for each audit
  centerroi = dataloc['CENTER']['MEAN'] # Getting center roi mean
  for auditKey in method:
    audit = method[auditKey]
    if audit['direction'] != 'CENTER':
      directionroi = dataloc["PERIPHERAL"][audit["direction"]] # Getting direction roi mean
      # Performing comparison between center and periph roi means
      dataloc["PERIPHERAL-COMP"][audit["direction"]] = np.absolute(centerroi - directionroi)


def setupHomogeneityData(method, img, date, reader):
  '''Prepares a spot in the global DATA variable for incoming audit data.'''

  global DATA
  if not isinstance(reader, str):
    logger.error("Passed value %s is not a string" % reader)
    return

  if not DATA["Homogeneity"].get(reader):
    DATA["Homogeneity"][reader] = {}

  if not DATA["Homogeneity"][reader].get(date):
    DATA["Homogeneity"][reader][date] = {}
  
  dataloc = DATA["Homogeneity"][reader][date]
  for auditKey in method.keys():
    audit = method[auditKey]
    direction = audit["direction"]
    if direction == "CENTER":
      dataloc["CENTER"] = {}
    if direction in ["NORTH", "SOUTH", "WEST", "EAST"]:
      # Only creating dicts if the keys aren't present
      if not dataloc.get("PERIPHERAL"):
        dataloc["PERIPHERAL"] = {}
      if not dataloc.get("PERIPHERAL"):
        dataloc["PERIPHERAL-COMP"] = {}


def computeHomogeneity(audit, dataset):
  '''
  Attempts to rescale DICOM pixel data by the DICOM RescaleIntercept/Slope tags.
  After attempted rescale, a region is selected from the pixel \
  data. Which region is dependant on the *audit* parameter. A 1D array of DICOM pixel \
  data is returned.
  '''
  
  scaledData = []
  if dataset.RescaleIntercept and dataset.RescaleSlope:
    scaledData = scalePixelData(dataset.pixel_array, dataset.RescaleIntercept, dataset.RescaleSlope)
  else:
    errMsg = "ERROR: No RescaleIntercept and RescaleSlope values were found"
    logger.error(errMsg)
    scaledData = dataset.pixel_array

  try:
    dataset.PixelSpacing
  except AttributeError:
    logger.error('No Pixel spacing attribute for image %s' % dataset.SeriesInstanceUID)
  
  # # Getting phantom center
  scaled_data = phantom.get_scaled_image(dataset)
  circle_coords = phantom.get_circles(scaled_data)

  centerY = int(circle_coords[0][0])
  centerX = int(circle_coords[0][1])

  # Getting initial config values from image
  # centerX = int(dataset.Rows/2) # Center of image X/Y
  # centerY = int(dataset.Columns/2)

  spacingXROI = audit["spacing"]/dataset.PixelSpacing[1] # For getting different ROIs
  spacingYROI = audit["spacing"]/dataset.PixelSpacing[0]
  halfLengthROI = math.sqrt(audit["size"])/2
  halfLengthXROI = halfLengthROI/dataset.PixelSpacing[1] # For getting  area of ROI
  halfLengthYROI = halfLengthROI/dataset.PixelSpacing[0]

  # Getting top left and bottom right x/y coords depending on audit direction
  if audit["direction"] == "CENTER":
    # Center X/Y points
    yl = int(centerX - halfLengthXROI)
    xl = int(centerY - halfLengthYROI)
    yr = int(centerX + halfLengthXROI)
    xr = int(centerY + halfLengthYROI)
  elif audit["direction"] == "NORTH":
    # Top X/Y Points
    yl = int((centerX - spacingXROI) - halfLengthXROI)
    xl = int(centerY - halfLengthYROI)
    yr = int((centerX - spacingXROI) + halfLengthXROI)
    xr = int(centerY + halfLengthYROI)
  elif audit["direction"] == "SOUTH":
    # Bottom X/Y Points
    yl = int((centerX + spacingXROI) - halfLengthXROI)
    xl = int(centerY - halfLengthYROI)
    yr = int((centerX + spacingXROI) + halfLengthXROI)
    xr = int(centerY + halfLengthYROI)
  elif audit["direction"] == "WEST":
    # Left X/Y Points
    yl = int(centerX - halfLengthXROI)
    xl = int((centerY - spacingYROI) - halfLengthYROI)
    yr = int(centerX + halfLengthXROI)
    xr = int((centerY - spacingYROI) + halfLengthYROI)
  elif audit["direction"] == "EAST":
    # Right X/Y Points
    yl = int(centerX - halfLengthXROI)
    xl = int((centerY + spacingYROI) - halfLengthYROI)
    yr = int(centerX + halfLengthXROI)
    xr = int((centerY + spacingYROI) + halfLengthYROI)

  if not os.path.isdir("./roi_selections"):
    os.mkdir("./roi_selections")

  deleteOldROISelections()

  roi_img_path = './roi_selections/' + dataset.StationName + '.' + dataset.StudyDate + '.jpg'
  if os.path.isfile(roi_img_path):
    img = cv2.imread(roi_img_path)
  else:
    img = phantom.get_scaled_image(dataset)
    img = phantom.set_window(img, 0, 50)
    img = cv2.cvtColor(img,cv2.COLOR_GRAY2BGR)
    print(circle_coords)
    cv2.circle(img,(circle_coords[0][0],circle_coords[0][1]),circle_coords[0][2],(0,255,0),5)

  cv2.rectangle(img, (xl,yl), (xr,yr),(0,0,255),3)
  cv2.imwrite(roi_img_path, img)

  # Performing ROI audit
  roi = selectArea(scaledData, xl, yl, xr, yr)

  return roi

  
def reformROIArray(data, x1, x2):
  '''Loops through flat ROI array and turns into 2d ROI array'''

  counter = 0
  arr = []
  tempArr = []
  length = x2-x1
  for i in range(len(data)):
    if counter == length-1:
      tempArr.append(data[i])
      arr.append(tempArr)
      tempArr = []
      counter = 0
    else:
      tempArr.append(data[i])
      counter = counter + 1
  
  return arr


def scalePixelData(pixelData, rInt, rSlope):
  '''Scales pixel image values linearly by rescale values'''

  scaledPixelData = []
  for pixelRow in pixelData:
    scaledPixelRow = []
    
    for pixelValue in pixelRow:
      pixelScale = (rSlope * pixelValue) + rInt
      scaledPixelRow.append(pixelScale)
      
    scaledPixelData.append(scaledPixelRow)
  
  return scaledPixelData


def deleteOldROISelections():
  """Deletes any old ROI selection graphics"""
  selectionPath = "./roi_selections"
  days = 120
  now = time.time()

  for f in os.listdir(selectionPath):
    filePath = os.path.join(selectionPath, f)
    if os.stat(filePath).st_mtime < now - days * 86400:
      if os.path.isfile(filePath):
        os.remove(filePath)


def selectArea(arr, x1, y1, x2, y2):
  '''Selects a specified area from a 2D array and fills a 1D arr with the values'''

  areaArr = []
  for row in range(y1, y2):
    for col in range(x1, x2):
      areaArr.append(arr[row][col])
  
  return areaArr
