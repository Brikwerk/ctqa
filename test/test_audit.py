# Tests for CTQA
from ctqa import confutil, imgfetch, logutil
from ctqa import audit
import json
import os
import pytest

# Constants
PROFILE_A = {
  "ctbaytest-GE MEDICAL SYSTEMS-DISCOVERY CT750 HD-TEST HOSPITAL": {
    "StationName": "ctbaytest",
    "Manufacturer": "GE MEDICAL SYSTEMS",
    "ManufacturerModelName": "DISCOVERY CT750 HD",
    "InstitutionName": "TEST HOSPITAL",
    "HomogeneityPosition": 75,
    "UpperHomogeneityLimit": 4,
    "LowerHomogeneityLimit": -4,
    "LinearityPosition": 0,
    "Baseline": {
      "STD": False,
      "CENTER": False,
      "NORTH": False,
      "SOUTH": False,
      "EAST": False,
      "WEST": False
    }
  }
}

PROFILE_B = {
  "ctbaytest-GE MEDICAL SYSTEMS-DISCOVERY CT750 HD-TEST HOSPITAL": {
    "StationName": "ctbaytest",
    "Manufacturer": "GE MEDICAL SYSTEMS",
    "ManufacturerModelName": "DISCOVERY CT750 HD",
    "InstitutionName": "TEST HOSPITAL",
    "HomogeneityPosition": 80,
    "UpperHomogeneityLimit": 4,
    "LowerHomogeneityLimit": -4,
    "LinearityPosition": 0,
    "Baseline": {
      "STD": False,
      "CENTER": False,
      "NORTH": False,
      "SOUTH": False,
      "EAST": False,
      "WEST": False
    }
  }
}

PROFILE_C = {
  "ctbaytest-GE MEDICAL SYSTEMS-DISCOVERY CT750 HD-TEST HOSPITAL": {
    "StationName": "ctbaytest",
    "Manufacturer": "GE MEDICAL SYSTEMS",
    "ManufacturerModelName": "DISCOVERY CT750 HD",
    "InstitutionName": "TEST HOSPITAL",
    "HomogeneityPosition": 0,
    "UpperHomogeneityLimit": 4,
    "LowerHomogeneityLimit": -4,
    "LinearityPosition": 0,
    "Baseline": {
      "STD": False,
      "CENTER": False,
      "NORTH": False,
      "SOUTH": False,
      "EAST": False,
      "WEST": False
    }
  }
}

  
### Testing for roi_select.py ###

def test_roi_imgA():
  '''Test for ROI selection correctness with imgA.dcm test image'''

  # Setup
  res = audit.run(PROFILE_A, ["test/data/imgA.dcm"], output_rois=False)
  mean = res['Homogeneity']['ctbaytest-GE MEDICAL SYSTEMS-DISCOVERY CT750 HD-TEST HOSPITAL']['20180531']['CENTER']['MEAN']
  assert mean == 1.214158239143367


def test_roi_imgB():
  '''Test for ROI selection correctness with imgB.dcm test image'''


  # Setup
  res = audit.run(PROFILE_B, ["test/data/imgB.dcm"], output_rois=False)
  mean = res['Homogeneity']['ctbaytest-GE MEDICAL SYSTEMS-DISCOVERY CT750 HD-TEST HOSPITAL']['20180601']['CENTER']['MEAN']
  assert mean == 1.5954788816180845


def test_roi_imgC():
  '''Test for ROI selection correctness with imgC.dcm test image'''
  # Setup
  res = audit.run(PROFILE_C, ["test/data/imgC.dcm"], output_rois=False)
  mean = res['Homogeneity']['ctbaytest-GE MEDICAL SYSTEMS-DISCOVERY CT750 HD-TEST HOSPITAL']['20180602']['CENTER']['MEAN']
  assert mean == 112.32718619869125
