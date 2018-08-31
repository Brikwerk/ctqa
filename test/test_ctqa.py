# Tests for CTQA
from ctqa import confutil, imgfetch, logutil
from ctqa import audit
import json
import os
import pytest

# Constants
EXAMPLE_CONFIG = confutil.DEFAULT_CONFIG
EXAMPLE_CONFIG['Source'] = 'ORTHANC'
EXAMPLE_CONFIG['OrthancRESTAddress'] = 'http://localhost'
PROFILE = {
  "ctbaytest-GE MEDICAL SYSTEMS-DISCOVERY CT750 HD-TEST HOSPITAL": {
    "StationName": "ctbaytest",
    "Manufacturer": "GE MEDICAL SYSTEMS",
    "ManufacturerModelName": "DISCOVERY CT750 HD",
    "InstitutionName": "TEST HOSPITAL",
    "HomogeneityPosition": 0,
    "LinearityPosition": 0,
    "Baseline": {
      "STD": 4.79,
      "CENTER": -0.8,
      "NORTH": 1.15,
      "SOUTH": 1.2,
      "EAST": 1.27,
      "WEST": 1.2
    }
  }
}

### Testing for confutil.py ###

@pytest.fixture(scope='session', autouse=True)
def cleanup():
  '''Creating fixture to run after tests and cleanup'''

  if os.path.isfile("testconf.json"):
    os.remove('testconf.json')


def test_config_creation():
  '''Test for creating a valid json config'''

  confutil.createConfig("testconf.json")
  try:
    with open('testconf.json', 'w') as f: # Attempt to load the config.json file
      assert True
      f.close()
    os.remove("testconf.json")
  except FileNotFoundError: # If the file cannot be found, create it and write default to it
    assert False

  
def test_config_load():
  '''Test for loading a valid config file'''

  with open("testconf.json", 'w') as outfile:
    json.dump(EXAMPLE_CONFIG, outfile, indent=2)
    outfile.close()
  
  loadedConfig = confutil.loadConfig("testconf.json")
  assert EXAMPLE_CONFIG == loadedConfig
  
  #Teardown
  os.remove("testconf.json")
  

def test_save_config():
  '''Test for saving to a valid config file'''

  # Setup
  confName = "testconf.json"
  res = confutil.createConfig(confName)
  if res == -1:
    assert False
  
  res = confutil.saveConfig(confName, EXAMPLE_CONFIG)
  if res == -1:
    assert False
  loadedConfig = confutil.loadConfig(confName)
  assert loadedConfig == EXAMPLE_CONFIG
  
  # Teardown
  os.remove(confName)
  

def test_open_config():
  '''Testing for config opening'''

  # Setup
  with open("testconf.json", 'w') as outfile:
    json.dump(EXAMPLE_CONFIG, outfile, indent=2)
    outfile.close()
    
  config = confutil.openConfig("testconf.json")
  assert config == EXAMPLE_CONFIG
  
  #Teardown
  os.remove("testconf.json")
  

def test_open_config_no_file():
  '''Testing for detection of bad open'''

  config = confutil.openConfig("testconf.json")
  assert config == 0
  
# Testing for update of config
def test_update_config():
  # Setup
  confutil.createConfig("testconf.json")
  
  res = confutil.updateConfig("testconf.json", "Source", "ORTHANC")
  if res != 1:
    assert False
  
  config = confutil.openConfig("testconf.json")
  assert config["Source"] == "ORTHANC"
  
  os.remove("testconf.json")
  

def test_update_config_bad_key():
  '''Testing for detection of bad update'''

  # Setup
  confutil.createConfig("testUpdateConfig.json")
  
  res = confutil.updateConfig("testUpdateConfig.json", "TEST", "TEST")
  assert res == -1
  
  os.remove("testUpdateConfig.json")
  

  
### Testing for roi_select.py ###

def test_roi_imgA():
  '''Test for ROI selection correctness with imgA.dcm test image'''

  # Setup
  res = audit.run(PROFILE, ["test/data/imgA.dcm"])
  mean = res['Homogeneity']['ctbaytest-GE MEDICAL SYSTEMS-DISCOVERY CT750 HD-TEST HOSPITAL']['20180531']['CENTER']['MEAN']
  assert mean == 1.1279000594883997


def test_roi_imgB():
  '''Test for ROI selection correctness with imgB.dcm test image'''


  # Setup
  res = audit.run(PROFILE, ["test/data/imgB.dcm"])
  mean = res['Homogeneity']['ctbaytest-GE MEDICAL SYSTEMS-DISCOVERY CT750 HD-TEST HOSPITAL']['20180601']['CENTER']['MEAN']
  assert mean == 1.5484830458060679


def test_roi_imgC():
  '''Test for ROI selection correctness with imgC.dcm test image'''
  # Setup
  res = audit.run(PROFILE, ["test/data/imgC.dcm"])
  mean = res['Homogeneity']['ctbaytest-GE MEDICAL SYSTEMS-DISCOVERY CT750 HD-TEST HOSPITAL']['20180602']['CENTER']['MEAN']
  assert mean == 115.53896490184414
