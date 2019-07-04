"""
| CTQA App Module
| Description: Main CTQA application file. Contains logic for preparing/starting execution.
"""

# Imports
import json
import sys
import os
from ctqa import confutil as conf
from ctqa import imgfetch
from ctqa import audit
from ctqa import datautil
from ctqa import reportutil
from ctqa import notifications

# Logging
import logging
from ctqa import logutil
logger = logging.getLogger(logutil.MAIN_LOG_NAME)

# Constants
LOCATION = os.path.abspath(os.path.dirname(sys.argv[0]))

# Main function
def run(config, profiles, __DEBUG, weekly=False):
  """Main function for preparing and running the CTQA audit."""

  # Checking passed config
  CONFIG = config
  if CONFIG == -1:
    print("Unable to load config. Please consult the log for more details. Exiting...")
    sys.exit()
  elif CONFIG == 0:
    print("config.json was not found. A new copy was created. Please fill this out with the appropriate values.")
    sys.exit()

  # Checking passed profiles
  PROFILES = profiles
  if PROFILES == -1:
    print("Unable to load profiles. Please consult the log for more details. Exiting...")
    sys.exit()
  elif PROFILES == 0:
    print("Unable to find profiles. Please consult the log for more details. Exiting...")
    sys.exit()
  
  #Getting paths to CT dicom files
  imgPaths = imgfetch.getImages(CONFIG)
  logger.debug("Returned images: %s", imgPaths)
  if imgPaths == -1:
    print("Error in image retrieval. Please check the log for details.")
    return -1
  elif imgPaths == None:
    print("None returned from image fetch. Please consult the log for more details.")
    return -1

  # Performing audit
  results = audit.run(PROFILES, imgPaths)
  # Reading out data
  dataFolderLocation = os.path.join(LOCATION, 'data')
  datautil.save(results, dataFolderLocation)

  # Creating reports
  # Iterating through each changed dataset
  for site in results['Homogeneity'].keys():
    # Get path to site folder in data folder
    sitePath = os.path.join(LOCATION, 'data', site)
    # Get title from site name
    dailyTitle = 'DAILY-' + site.split('-')[3] + '-' + site.split('-')[2] + '-' + site.split('-')[0]
    # Create report
    if not weekly:
      # Getting site's upper/lower limits
      upperlimit = PROFILES[site]["UpperHomogeneityLimit"]
      lowerlimit = PROFILES[site]["LowerHomogeneityLimit"]
      prediction = reportutil.generateReport(sitePath, CONFIG, dailyTitle, upperlimit, lowerlimit)
      # Warning if prediction exceeds upper/lower limit
      if prediction != None and (prediction > upperlimit or prediction < lowerlimit):
        notifications.notify_of_warning(site, CONFIG["DaysToForecast"], prediction)
      
      # Recording report generated and location
      reportlocation = os.path.abspath(os.path.join(CONFIG["ReportLocation"], dailyTitle + ".png"))
      notifications.DATA["changedReports"].append(reportlocation)

      # Adding relevant daily report to any events that occured
      if site in notifications.DATA["events"].keys():
        notifications.DATA["events"][site]["reportLocation"] = reportlocation
  # Regnerate reports if weekly no matter what
  if weekly:
    reportutil.regenerateReports(dataFolderLocation, CONFIG, report_type="weekly")
  
  # Set notifications to weekly or daily
  if weekly:
    notifications.DATA["runType"] = "weekly"
  else:
    notifications.DATA["runType"] = "daily"
  logger.debug(notifications.DATA)

  # Sending notifications
  notifications.send_notifications(CONFIG)
  
  # Ensuring test images are deleted
  if CONFIG.get("Source") != "TEST":
    for img in imgPaths:
      try:
        # Removing downloaded temp images
        os.remove(img)
      except FileNotFoundError:
        logger.error("Could not delete temp image: %s", img)
  
  logger.info("Finished")

