import smtplib
import imaplib
import poplib
import exchangelib
from . import encryption
from cryptography.fernet import Fernet

# Logging
import logging
from ctqa import logutil
logger = logging.getLogger(logutil.MAIN_LOG_NAME)


def test_connect(address, password, type, server, port):
  if type == "SMTP":
    return smtp_test_connect(address, password, server, port)
  elif type == "Exchange":
    return exchange_test_connect(address, password)
  else:
    return False, "Unknown email connection type supplied"


def smtp_test_connect(address, password, server, port):
  try:
    logger.debug("Attempting SMTP login with user: %s, server: %s, and port: %d" % (address, server, port))
    smtpserver = smtplib.SMTP(server, port)
    smtpserver.ehlo()
    smtpserver.starttls()
    smtpserver.ehlo()
    resp, message = smtpserver.login(address, password)
    logger.debug("SMTP login result: %d %s" % (resp, message.decode("utf-8")))
  except Exception as e:
    logger.error(str(e))
    return False, str(e)

  if resp == 235:
    return True, message.decode("utf-8")
  else:
    return False, message.decode("utf-8")


def exchange_test_connect(address, password):
  logger.debug("Attempting Exchange login with user: %s" % (address))
  try:
    credentials = exchangelib.Credentials(address, password)
    account = exchangelib.Account(address, credentials=credentials, autodiscover=True)
    logger.debug("Connection successful")
    return True, "Connection successful"
  except Exception as e:
    logger.debug("Connection unsuccessful: %s" % str(e))
    return False, str(e)
