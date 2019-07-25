"""
Audit Methods Module

A module that contains data regarding the audits available for a CT machine, sorted \
by manufacturer.
"""

# Imports
import copy

# Constants
METHODS = {
  'GE MEDICAL SYSTEMS': {
    'audit_one': {
      'direction': 'NORTH',
      'spacing': 75,
      'size': 400
    },
    'audit_two': {
      'direction': 'SOUTH',
      'spacing': 75,
      'size': 400
    },
    'audit_three': {
      'direction': 'EAST',
      'spacing': 75,
      'size': 400
    },
    'audit_four': {
      'direction': 'WEST',
      'spacing': 75,
      'size': 400
    },
    'audit_five': {
      'direction': 'CENTER',
      'spacing': 0,
      'size': 400
    },
  },
  'DEFAULT': {
    'audit_one': {
      'direction': 'CENTER',
      'spacing': 0,
      'size': 400
    }
  }
}


def getMethod(manufacturer):
  """Gets audit methods by passed manufacturer string. Uses manufacturer string
  as a key to search the *METHODS* Dictionary object. 
  
  If no suitable manufacturer is found, the default audit methods are used.
  """
  auditMethod = METHODS.get(manufacturer)
  if auditMethod == None:
    return copy.deepcopy(METHODS.get('DEFAULT'))
  else:
    return copy.deepcopy(METHODS.get(manufacturer))


def getAuditDirections(manufacturer):
  """
  The audit directions are gotten based off of the manufacturer string.

  EX: ['NORTH', 'SOUTH', 'EAST', 'WEST', 'CENTER']

  If no manufacturer is found for the passed string, the default is returned.
  """
  auditMethod = METHODS.get(manufacturer)
  if auditMethod == None:
    auditMethod = METHODS.get('DEFAULT')
  directions = []

  for auditKey in auditMethod.keys():
    audit = auditMethod[auditKey]
    direction = audit['direction']
    if direction not in directions:
      directions.append(direction)

  return directions
    
