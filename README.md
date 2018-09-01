# CTQA: CT Quality Assurance

## Description
An application for automated CT quality assurance.

Currently compatible with Orthanc PACS server instances.

# Getting Started

## Running CTQA

Note for windows users: An illustrated guide exists under the docs folder

1. Please download a compatible release distribution from [here](https:/github.com/brikwerk/ctqa/releases)

2. Extract the executable to a sensible location. Please keep in mind that the windows distribution of CTQA will create extra files and folders.

3. Follow the PDF included in the zip file for installation instructions. If you unable to locate the PDF, a version is available at the root of the repository ('ctqa-install.pdf').

## Setting up the Development Environment

1. Run either env-setup.bat or env-setup.sh (The scripts setup a virtual environment under .env, install all required modules to it, and activate the environment).

2. For quicker access to the environment on windows, type "activate" at the root.

3. To compile CTQA, run:

'''
pyinstaller run.spec
'''

or for a binary with a console debug output:

'''
pyinstaller run-debug.spec
'''

# Notes:
CTs used with this utility must output DICOM tags StationName, Manufacturer, ManufacturerModelName, and InstitutionName. These attributes are used to recognize a CT from given images.
