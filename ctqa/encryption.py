'''
CTQA Encryption
Encryption functions
'''

from cryptography.fernet import Fernet
import os, sys

LOCATION = os.path.abspath(os.path.dirname(sys.argv[0]))


def get_fernet_key():
  '''Load key from file. If not present, we create it.'''
  key = None
  keypath = os.path.join(LOCATION, 'ek')
  if not os.path.isfile(keypath):
    key = Fernet.generate_key()
    with open(keypath, 'wb') as outfile:
      outfile.write(key)
      outfile.close()
  else:
    with open(keypath, 'rb') as infile:
      key = infile.read()
      infile.close()

  # Create a Fernet key from the base key
  return Fernet(key)
  del(key)