'''
CTQA Encryption
Encryption functions
'''

from cryptography.fernet import Fernet
import os, sys

# Logging
import logging
from ctqa import logutil
logger = logging.getLogger(logutil.MAIN_LOG_NAME)

LOCATION = os.path.abspath(os.path.dirname(sys.argv[0]))


def get_fernet_key():
  '''Load key from file. If not present, we create it.'''
  key = None
  keypath = os.path.join(LOCATION, 'ek')
  if not os.path.isfile(keypath):
    key = Fernet.generate_key()
    with open(keypath, 'wb') as outfile:
      outfile.write(key)
  else:
    with open(keypath, 'rb') as infile:
      key = infile.read()

  # Create a Fernet key from the base key
  return Fernet(key)


def save_password(password):
  password_encoded = password.encode()
  f = get_fernet_key()
  encrypted = f.encrypt(password_encoded)
  datapath = os.path.join(LOCATION, 'data', 'enc')
  with open(datapath, 'wb') as outfile:
    outfile.write(encrypted)


def get_password():
  f = get_fernet_key()
  datapath = os.path.join(LOCATION, 'data', 'enc')
  password = ""
  try:
    with open(datapath, 'rb') as infile:
      encoded_password = infile.read()
      password = f.decrypt(encoded_password).decode("utf-8")
  except Exception as e:
    logger.error(str(e))
  
  return password
  