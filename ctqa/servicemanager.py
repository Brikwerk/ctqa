"""
Service Manager

Detects the OS and installs the CTQA service to run the audit on a regular basis.
"""

import platform
import pywintypes
import win32com
import win32com.shell.shell as shell
import win32event
#TODO: Import chron job module
import os
import sys
from ctqa import confutil

# Getting OS
SYSNAME = platform.system()
# Getting audit exec location
LOCATION = os.path.abspath(os.path.dirname(sys.argv[0]))

#Logging
import logging
from . import logutil
logger = logging.getLogger(logutil.MAIN_LOG_NAME)


def install():
  """Detects the OS and runs the appropriate installation method."""

  logger.warning("Beginning system install")

  if SYSNAME == 'Windows':
    logger.warning("Detected windows system")
    install_windows()
  elif SYSNAME == 'Darwin' or SYSNAME == 'Linux':
    logger.warning('Detected Mac OS or Linux')
  else:
    logger.error("No suitable install procedure found for the OS: %s", SYSNAME)


def install_windows():
  """Attempts to install the CTQA Audit utility as a task in Windows Task Scheduler."""

  params = '/Create /SC Daily /RU System /TN "CTQA" /TR "' + os.path.join(LOCATION, sys.argv[0]) + ' --audit --debug" /ST 07:00'
  params_weekly = '/Create /SC Weekly /RU System /D MON /TN "CTQA-Weekly" /TR "' + os.path.join(LOCATION, sys.argv[0]) + ' --audit --weekly --debug" /ST 07:00'
  logger.debug('Installing with script: ' + params)

  # Attempt to exec as admin. Catch denial of UAC prompt.
  try:
    # Daily audit installation
    dict = shell.ShellExecuteEx(fMask = 256 + 64, lpVerb='runas', lpFile='Schtasks.exe', lpParameters=params)
    hh = dict['hProcess']
    ret = win32event.WaitForSingleObject(hh, -1)
    logger.debug("Shell CTQA Daily Audit installation result: " + str(ret))

    # Weekly audit installation
    dict = shell.ShellExecuteEx(fMask = 256 + 64, lpVerb='runas', lpFile='Schtasks.exe', lpParameters=params_weekly)
    hh = dict['hProcess']
    ret = win32event.WaitForSingleObject(hh, -1)
    logger.debug("Shell CTQA Weekly Audit installation result: " + str(ret))

  except pywintypes.error as e:
    logger.error("Error in UAC prompt for windows installation: " + str(e))

  print(os.path.join(LOCATION, confutil.DEFAULT_CONFIG_LOCATION))
  confutil.updateConfig(os.path.join(LOCATION, confutil.DEFAULT_CONFIG_LOCATION), "ServicesInstalled", True)


def uninstall():
  """Detects the OS and runs the appropriate uninstallation method."""

  logger.warning("Beginning system install")

  if SYSNAME == 'Windows':
    logger.warning("Detected windows system")
    uninstall_windows()
  elif SYSNAME == 'Darwin' or SYSNAME == 'Linux':
    logger.warning('Detected Mac OS or Linux')
  else:
    logger.error("No suitable install procedure found for the OS: %s", SYSNAME)


def uninstall_windows():
  """Attempts to uninstall the CTQA Audit task with the Schtasks command"""

  params = '/delete /TN "CTQA" /f'
  params_weekly = '/delete /TN "CTQA-Weekly" /f'

  logger.debug('Uninstalling with script: ' + params)

  # Attempt to exec as admin. Catch denial of UAC prompt.
  try:
    # Uninstall daily audit
    dict = shell.ShellExecuteEx(fMask = 256 + 64, lpVerb='runas', lpFile='Schtasks.exe', lpParameters=params)
    hh = dict['hProcess']
    ret = win32event.WaitForSingleObject(hh, -1)
    logger.debug("Shell uninstallation result: " + str(ret))

    # Uninstall weekly audit
    dict = shell.ShellExecuteEx(fMask = 256 + 64, lpVerb='runas', lpFile='Schtasks.exe', lpParameters=params_weekly)
    hh = dict['hProcess']
    ret = win32event.WaitForSingleObject(hh, -1)
    logger.debug("Shell uninstallation result: " + str(ret))

  except pywintypes.error as e:
    logger.error("Error in UAC prompt for windows installation: " + str(e))

  confutil.updateConfig(os.path.join(LOCATION, confutil.DEFAULT_CONFIG_LOCATION), "ServicesInstalled", False)
