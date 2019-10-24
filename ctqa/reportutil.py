"""
Report Utility

Generates and saves a CT machine's report based off of audit data.
"""
import logging
from ctqa import logutil
# Explicitly disabling matplotlib to prevent log spam
logging.getLogger('matplotlib').setLevel(logging.WARNING)
import matplotlib
# Using simplified mpl backend due to exclusive png creation
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.pyplot import figure
import datetime
import numpy as np
import json
import os, sys
from ctqa import datautil
from ctqa import profileutil
from ctqa import notifications

#Logger init
logger = logging.getLogger(logutil.MAIN_LOG_NAME)


def generateReport(dataPath, config, title, upperlimit, lowerlimit, report_type="daily"):
  """
  Retrieves audit data from the data path, organizes a site's data into a displayable format,
  and creates a PNG graph at the passed save location.
  """

  logger.debug("Generating report: " + title)

  # Config variable assignment
  savelocation = config.get("ReportLocation")
  forecastdays = config.get("DaysToForecast")
  if report_type == "daily":
    graphdays = config.get("DailyReportDaysToGraph")
  else:
    graphdays = config.get("WeeklyReportDaysToGraph")

  # Getting data
  jsonData = datautil.load(dataPath)
  if jsonData == -1:
    print('Unable to load json data')
    return -1

  # Selecting center roi data and organizing
  centerrois = []
  centerdates = []

  for date in jsonData['Homogeneity'].keys():
    try:
      centerrois.append(jsonData['Homogeneity'][date]['CENTER']['MEAN'])
      centerdates.append(mdates.datestr2num(date))
    except KeyError as e:
      logger.error("Unable to find key when parsing Homogeneity data", exc_info=True)

  # Loop through collected dates and omit any submitted before now - graphdays ago
  temprois = []
  tempdates = []
  datenow = mdates.date2num(datetime.datetime.now())
  for i in range(0, len(centerdates)):
    if centerdates[i] > (datenow - graphdays):
      temprois.append(centerrois[i])
      tempdates.append(centerdates[i])
  centerrois = temprois
  centerdates = tempdates

  months = mdates.MonthLocator()  # every month
  days = mdates.WeekdayLocator()
  monthsFmt = mdates.DateFormatter('%Y-%m')

  axes = plt.subplot()
  plt.plot_date(x=centerdates, y=centerrois, fmt='o', label='Center ROI Means', zorder=10)
  axes.xaxis.set_major_locator(months)
  axes.xaxis.set_major_formatter(monthsFmt)
  axes.xaxis.set_minor_locator(days)

  # Setting axis bounds
  plt.xlim((datenow - graphdays, datenow + forecastdays + 5))

  # Calibration levels
  plt.axhline(upperlimit, color='red', linewidth=1, label='Control Limits')
  plt.axhline(lowerlimit, color='red', linewidth=1)
  # Warning levels
  plt.axhline(upperlimit/2, color='orange', linewidth=1)
  plt.axhline(lowerlimit/2, color='orange', linewidth=1)
  # Center line
  plt.axhline(0, color='black', linewidth=1)

  # Adding axes labels
  plt.xlabel("Date")
  plt.ylabel("ROI Mean Values")

  # Rotating x-axis 45 degrees
  plt.xticks(rotation=45)

  # Setting image size
  fig = plt.gcf()
  # Dimensions for image defined in inches
  fig.set_size_inches(8,5,forward=True) # foward=True => Propagates changes to gui window

  # Gathering points taken in the last month
  lastdates = []
  lastrois = []
  for i in range(0, len(centerdates)):
    if centerdates[i] > (datenow - 30):
      lastdates.append(centerdates[i])
      lastrois.append(centerrois[i])

  # Fitting regression for decalibration prediction if we have enough data
  # Aiming for at least 3 points of data in the last month.
  forecastend = None
  if len(lastdates) > 2:
    # Fitting linear polynomial
    fit = np.polyfit(lastdates, lastrois, 1) # Fitting to dates/rois to a single degree polynomial
    # Plotting best fit line with a two week forecast
    forecasttime = lastdates[(len(lastdates)-1)] + forecastdays
    forecaststart = (lastdates[0]*fit[0]) + fit[1]
    forecastend = (forecasttime*fit[0]) + fit[1] # y = mx + b
    # Starting plot at the first value in lastdates
    plt.plot_date(x=[lastdates[0], forecasttime], y=[forecaststart, forecastend], label='Forecast Trend', fmt="--o", zorder=5)

  # Creating legend
  handles, labels = axes.get_legend_handles_labels()
  strdates = list(jsonData["Homogeneity"].keys())
  if len(strdates) >= 1:
    # Creating blank rectangle for date holder
    blankrectangle = matplotlib.patches.Rectangle((0, 0), 1, 1, fc="w", fill=False, edgecolor='none', linewidth=0)
    handles.append(blankrectangle)
    # Getting last point date as string
    strdates.sort()
    lastdatepoint = strdates[len(strdates)-1]
    lastdatepoint = "Last Point: %s/%s/%s" % (lastdatepoint[0:4], lastdatepoint[4:6], lastdatepoint[6:8])
    labels.append(lastdatepoint)
  axes.legend(handles, labels)

  # Title
  plt.title(title)
  # Packing layout
  plt.tight_layout()

  # Setting location for export to reports folder, local to executable
  file = title + '.png'
  loc = os.path.abspath(savelocation)
  # Ensuring the save location exists
  os.makedirs(loc, exist_ok=True)
  file_loc = os.path.join(loc, file)

  # Saving png image to savelocation
  plt.savefig(file_loc, dpi=300)
  # Clearing plot. MUST DO THIS UNLESS YOU WANT THE OLD PLOT TO REMAIN FOR ANOTHER RUN
  plt.close()

  return forecastend


def regenerateReports(dataPath, config, profiles, report_type="daily"):
  """Finds all data folders and updates reports based on existing data"""
  # Getting report names and paths to the data
  pathitems = os.listdir(dataPath)
  subnames = []
  for item in pathitems:
    itempath = os.path.join(dataPath, item)
    if os.path.isdir(itempath):
      subnames.append(item)

  # Generating reports
  for site in subnames:
    # Put together data.json location
    sitepath = os.path.join(dataPath, site)
    
    # Getting site profile stats
    siteprofile = profiles[site]
    upperlimit = siteprofile.get("UpperHomogeneityLimit")
    lowerlimit = siteprofile.get("LowerHomogeneityLimit")

    # Generating daily or weekly reports
    sitesplit = site.split("-")
    shortitle = sitesplit[3] + '-' + sitesplit[2] + '-' + sitesplit[0]
    if report_type == "daily":
      # Get title from site name
      title = 'DAILY-' + shortitle
      # Create report
      generateReport(sitepath, config, title, upperlimit, lowerlimit)
    elif report_type == "weekly":
      # Get title from site name
      title = 'WEEKLY-' + shortitle
      # Create report
      generateReport(sitepath, config, title, upperlimit, lowerlimit, report_type="weekly")
