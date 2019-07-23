import smtplib
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
import datetime
import os
import exchangelib
from exchangelib import Credentials, Account, Mailbox, Message, HTMLBody, FileAttachment
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


def smtp_connect(address, password, server, port):
  smtpserver = smtplib.SMTP(server, port)
  smtpserver.ehlo()
  smtpserver.starttls()
  smtpserver.ehlo()
  resp, message = smtpserver.login(address, password)
  return smtpserver, resp, message


def smtp_test_connect(address, password, server, port):
  try:
    logger.debug("Attempting SMTP login with user: %s, server: %s, and port: %d" % (address, server, port))
    smtpserver, resp, message = smtp_connect(address, password, server, port)
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


def send_mail(config, data, event_type):
  # Checking for valid email config to execute on
  if config["Email"] == "":
    logger.warning("No suitable email found in config. Skipping over sending notification mail.")
    return

  logger.debug("Creating email content")
  # Creating email content
  attachments = None
  subject = None
  body = None
  recipients = None

  if event_type == "daily":
    logger.debug("Sending daily event")
    attachments = data
    subject = "CTQA: Daily Reports"
    body = "%d daily report(s) from the CTQA utility are attached.\nDate/time Run: %s" % (len(data), str(datetime.datetime.now()))
    recipients = config["DailyRecipients"]

  elif event_type == "weekly":
    logger.debug("Sending weekly event")
    attachments = data
    subject = "CTQA: Weekly Reports"
    body = "%d weekly report(s) from the CTQA utility are attached.\nDate/time Run: %s" % (len(data), str(datetime.datetime.now()))
    recipients = config["WeeklyRecipients"]

  elif event_type == "warning":
    logger.debug("Sending warning event")
    attachments=[data["reportLocation"]]
    filename = os.path.basename(data["reportLocation"]).split(".")[0]
    roi_value = data["roiValue"]
    forecast_days = data["forecastDays"]
    subject = "CTQA: WARNING"
    body = "Drift detected in site: %s.\nRegion of interest value: %f\nForecast Days: %d\nDate/time Run: %s"  % (filename, roi_value, forecast_days, str(datetime.datetime.now()))
    recipients = config["WarningRecipients"]

  elif event_type == "failure":
    logger.debug("Sending failure event")
    attachments=[data["reportLocation"]]
    filename = os.path.basename(data["reportLocation"]).split(".")[0]
    roi_value = data["roiValue"]
    subject = "CTQA: FAILURE"
    body = "Failure detected in site: %s.\nRegion of interest value: %f\nDate/time Run: %s"  % (filename, roi_value, str(datetime.datetime.now()))
    recipients = config["FailureRecipients"]

  # Emailing
  if config["EmailServerType"] == "SMTP":
    logger.debug("Sending email through SMTP")
    send_mail_smtp(config, recipients, subject, body, attachments)
  elif config["EmailServerType"] == "Exchange":
    logger.debug("Sending email through Exchange")
    send_mail_exchange(config, recipients, subject, body, attachments)
  else:
    logger.warning("No method found for Email Server Type in config")
  

def send_mail_smtp(config, recipients, subject, body, attachments):
  # Gathering email account details
  user = config["Email"]
  password = encryption.get_password()
  server = config["EmailServer"]
  port = config["EmailServerPort"]

  # Assembling email message
  msg = MIMEMultipart()
  msg['Subject'] = subject
  msg['From'] = user
  msg['To'] = recipients

  # Attaching body to message
  text = MIMEText(body)
  msg.attach(text)

  # Attaching images
  for image_path in attachments:
    img_data = open(image_path, 'rb').read()
    image = MIMEImage(img_data, name=os.path.basename(image_path))
    msg.attach(image)

  # Attempting to send the message
  try:
    # Attempting a connection
    connection, resp, message = smtp_connect(user, password, server, port)
    if not resp == 235:
      logger.error("Unable to connect to SMTP server: " + str(message.decode("utf-8")))
    logger.debug("SMTP connection successful")
    connection.sendmail(user, recipients, msg.as_string())
  except Exception as e:
    logger.error("Unable to send mail through SMTP: " + str(e))
    return


def send_mail_exchange(config, recipients, subject, body, attachments):
  # Gathering email account details
  user = config["Email"]
  password = encryption.get_password()

  # Connecting to Exchange account
  account = None
  try:
    credentials = Credentials(user, password)
    account = Account(user, credentials=credentials, autodiscover=True)
    logger.debug("Exchange connection successful")
  except Exception as e:
    logger.error("Could not connect to Exchange Email: " + str(e))
    return
  
  # Constructing message
  message = Message(account=account,
    subject=subject,
    body=body,
    to_recipients=recipients.replace(", ", ",").split(","))

  # Attaching files
  for image_path in attachments:
    with open(image_path, 'rb') as f:
      repImage = FileAttachment(name=os.path.basename(image_path), content=f.read())
    message.attach(repImage)

  # Sending
  message.send_and_save()
