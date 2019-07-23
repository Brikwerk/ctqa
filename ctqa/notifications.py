'''
CTQA Notifications
Includes logic to notify users about new reports.
'''

import json, os, sys
from subprocess import Popen
import base64
from . import emailutil

import logging
from ctqa import logutil
logger = logging.getLogger(logutil.MAIN_LOG_NAME)

# Constants
LOCATION = os.path.abspath(os.path.dirname(sys.argv[0]))
global DATA
DATA = {
  "runType": None,
  "events": {},
  "changedReports": []
}


def notify_of_failure(sitename, date, roi_value):
  """Records a failure event within the DATA variable"""
  DATA["events"][sitename] = {
    "type": "failure",
    "date": date,
    "roiValue": roi_value
  }


def notify_of_warning(sitename, forecast_days, predicted_value):
  """Records a warning event within the DATA variable"""
  if not sitename in DATA["events"].keys():
    DATA["events"][sitename] = {
      "type": "warning",
      "forecastDays": forecast_days,
      "roiValue": predicted_value
    }


def send_notifications(config):
  """Sends all recorded notifications"""
  # Sending failure and warning notifications
  for eventkey in DATA["events"].keys():
    event = DATA["events"][eventkey]
    eventstring = json.dumps(event)
    eventstring = encode_json_string(eventstring)

    # If it's a failure event
    if event["type"] == "failure":
      # Looping through paths and sending the failure event to each one
      exec_paths(config["FailureHook"], eventstring, "failure")
      emailutil.send_mail(config, event, "failure")
    
    # If it's a warning event
    elif event["type"] == "warning":
      # Looping through paths and sending the warning event to each one
      exec_paths(config["WarningHook"], eventstring, "warning")
      emailutil.send_mail(config, event, "warning")
  
  # Sending changed daily reports
  if len(DATA["changedReports"]) > 0:
    dailyreports = json.dumps(DATA["changedReports"])
    dailyreports = encode_json_string(dailyreports)
    exec_paths(config["DailyReportHook"], dailyreports, "daily")
    emailutil.send_mail(config, DATA["changedReports"], "daily")

  if DATA["runType"] == "weekly":
    weeklyreports = json.dumps(get_weekly_reports(config))
    weeklyreports = encode_json_string(weeklyreports)
    exec_paths(config["WeeklyReportHook"], weeklyreports, "weekly")
    emailutil.send_mail(config, get_weekly_reports(config), "weekly")


def exec_paths(paths, arg, notificationtype):
  """Executes all defined paths and attaches the appropriate notifications as arguments"""
  paths = paths.split(";")

  # Returning if paths is empty
  if len(paths) == 0:
    return

  for path in paths:
    # Skipping if the path is length zero
    if len(path) == 0:
      continue
    logger.debug("Notifying " + path + " of " + notificationtype + " with argument " + arg)
    runpath = path + ' "' + arg + '" ' + notificationtype
    logger.debug("Running: " + runpath)
    p = Popen(runpath)
    stderr = p.communicate()
    logger.debug(stderr)


def get_weekly_reports(config):
  """Retrieves the paths for all reports"""
  reportslocation = config["ReportLocation"]
  weeklyreports = []
  for file in os.listdir(reportslocation):
    reportpath = os.path.abspath(os.path.join(reportslocation, file))
    if os.path.isfile(reportpath) and "WEEKLY" in file:
      weeklyreports.append(reportpath)
  
  return weeklyreports


def encode_json_string(string):
  """Encodes a JSON string to base64 string format"""
  return base64.urlsafe_b64encode(bytes(string, 'utf-8')).decode("utf-8")
