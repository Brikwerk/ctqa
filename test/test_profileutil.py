from ctqa import confutil
import json
import os
import pytest

EXAMPLE_CONFIG = confutil.DEFAULT_CONFIG
EXAMPLE_CONFIG['Source'] = 'ORTHANC'
EXAMPLE_CONFIG['OrthancRESTAddress'] = 'http://localhost'

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
