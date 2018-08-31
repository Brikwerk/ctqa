# CTQA: CT Quality Assurance

## Description
An application for automated CT quality assurance.

Currently compatible with Orthanc PACS server instances.

# Getting Started

## Running CTQA

Note for windows users: An illustrated guide exists under the docs folder

1. Please download a compatible release distribution from [here](https:/github.com/Brikwerk/ctqa/releases)

2. Extract the executable to a sensible location. Please keep in mind that the windows distribution of CTQA will create extra files and folders.

3. Run the executable. It's recommended to agree/follow the first run setup.

4. Once you're finished with setting up, press the "Manual Audit" button and follow the log to make sure everything is correct. The manual audit should go through all new images and record the results.

5. If all goes well with the manual audit (data/reports generated), click the "Install Service" button. This will install the CTQA audit functionality as a scheduled task (Windows) or Chron job (Linux/Mac).

6. You will be prompted for administrative access as CTQA installs itself. Please agree to this prompt to continue.

## Setting up the Development Environment

1. Run either env-setup.bat or env-setup.sh (The scripts setup a virtual environment under .env, install all required modules to it, and activate the environment)

2. For quicker access to the environment on windows, type "activate" at the root

# Notes:
CTs used with this utility must output DICOM tags StationName, Manufacturer, ManufacturerModelName, and InstitutionName. These attributes are used to recognize a CT from given images.