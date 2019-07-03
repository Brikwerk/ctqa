'''
CTQA Notifications
Includes logic to notify users about new reports.
'''

from ctqa import encryption
import json, os, sys

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
  DATA["events"][sitename] = {
    "type": "failure",
    "date": date,
    "roiValue": roi_value
  }


def notify_of_warning(sitename, forecast_days, predicted_value):
  if not sitename in DATA["events"].keys():
    DATA["events"][sitename] = {
      "type": "warning",
      "forecastDays": forecast_days,
      "roiValue": predicted_value
    }
