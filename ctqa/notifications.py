'''
CTQA Notifications
Includes logic to notify users about new reports.
'''

from exchangelib import Credentials, Account, Mailbox, Message, HTMLBody, FileAttachment
from ctqa import encryption
import json, os, sys

import logging
from ctqa import logutil
logger = logging.getLogger(logutil.MAIN_LOG_NAME)

# Constants
LOCATION = os.path.abspath(os.path.dirname(sys.argv[0]))


def mail_reports(repnames):
  '''Gets previously entered credentials and attempts to email report pngs to receiver.'''

  fkey = encryption.get_fernet_key()

  # Reading in binary file
  infile = open(LOCATION + '/data/enc', 'rb')
  token = infile.read()
  infile.close()

  data = fkey.decrypt(token)
  # Decoding bytes
  try:
    data = data.decode('ascii')
  except json.decoder.JSONDecodeError:
    logger.error("enc file could not be decoded. Please provide valid JSON data.")
    return -1

  # Serializing to JSON
  CREDS = json.loads(data)

  if len(CREDS.keys()) < 4:
    logger.error('Too few keys in credentials.')
    return -1

  if len(repnames) < 1:
    logger.error('No reports to generate. Stopping email report generation.')
    return -1

  credentials = Credentials(CREDS['EmailAddress'], CREDS['Password'])
  account = Account(CREDS['EmailAddress'], credentials=credentials, autodiscover=True)

  message = Message(account=account,
              subject='CTQA Reports',
              body='New reports from machines: ' + str(repnames),
              to_recipients=[Mailbox(email_address=CREDS['Receiver'])])

  embedString = '<html><body>New reports from machines: <br>'
  for name in repnames:
    # Rearranging string for report name
    id = name.split('-')[0]
    model = name.split('-')[2]
    hosp = name.split('-')[3]

    repfilename = hosp + '-' + model + '-' + id + '.png'
    repfileloc = os.path.join(LOCATION, 'reports', repfilename)
    logger.warning('Attaching report: ' + repfileloc)

    with open(repfileloc, 'rb') as f:
     repImage = FileAttachment(name=repfilename, content=f.read())
    message.attach(repImage)

    embedString = embedString + '' + name + '<br>'

  embedString = embedString + '</body></html>' 
  print(embedString)
  message.body = HTMLBody(embedString)

  message.send_and_save()