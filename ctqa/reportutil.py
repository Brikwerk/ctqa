'''
Report Utility

Generates and saves a CT machine's report based off of audit data.
'''

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


def generateReport(dataPath, savelocation, title, graphdays, forecastdays, report_type="daily"):
  '''
  Retrieves audit data from the data path, organizes a site's data into a displayable format,
  and creates a PNG graph at the passed save location.
  '''

  # Getting data
  jsonData = datautil.load(dataPath)
  if jsonData == -1:
    print('Unable to load json data')
    return -1

  # Selecting center roi data and organizing
  centerrois = []
  centerdates = []

  for date in jsonData['Homogeneity'].keys():
    centerrois.append(jsonData['Homogeneity'][date]['CENTER']['MEAN'])
    centerdates.append(mdates.datestr2num(date))

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

  plt.plot_date(x=centerdates, y=centerrois, fmt='o', label='Center ROI Means', zorder=10)
  plt.axes().xaxis.set_major_locator(months)
  plt.axes().xaxis.set_major_formatter(monthsFmt)
  plt.axes().xaxis.set_minor_locator(days)

  plt.ylim((-6, 6))
  # Calibration levels
  plt.axhline(4, color='red', linewidth=1, label='Control Limits')
  plt.axhline(-4, color='red', linewidth=1)
  # Warning levels
  plt.axhline(2, color='black', linewidth=1)
  plt.axhline(-2, color='black', linewidth=1)
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
  handles, labels = plt.axes().get_legend_handles_labels()
  plt.axes().legend(handles, labels)

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


def regenerateReports(dataPath, reportsPath, daysToGraph, daysToForecast, report_type="daily"):
  '''Finds all data folders and updates reports based on existing data'''
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

    # Generating daily or weekly reports
    if report_type == "daily":
      # Get title from site name
      title = 'DAILY-' + site.split('-')[3] + '-' + site.split('-')[2] + '-' + site.split('-')[0]
      # Create report
      generateReport(sitepath, reportsPath, title, daysToGraph, daysToForecast)
    elif report_type == "weekly":
      # Get title from site name
      title = 'WEEKLY-' + site.split('-')[3] + '-' + site.split('-')[2] + '-' + site.split('-')[0]
      # Create report
      generateReport(sitepath, reportsPath, title, daysToGraph, daysToForecast, report_type="weekly")
