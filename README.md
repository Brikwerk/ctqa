<p align="center">
  <a href="" rel="noopener">
 <img width=200px height=200px src="https://i.imgur.com/XXOE0B4.png" alt="CTQA logo"></a>
</p>

<h3 align="center">CTQA</h3>

<div align="center">

  [![Stars](https://img.shields.io/github/stars/brikwerk/ctqa.svg)]() 
  [![GitHub Issues](https://img.shields.io/github/issues/brikwerk/ctqa.svg)](https://github.com/brikwerk/ctqa/issues)
  [![GitHub Pull Requests](https://img.shields.io/github/issues-pr/brikwerk/ctqa.svg)](https://github.com/brikwerk/ctqa/pulls)
  [![License](https://img.shields.io/badge/license-MIT-blue.svg)](/LICENSE)

</div>

---

<p align="center"> This utility aims to perform automated QA testing on CT machines for technologists.
    <br> 
</p>

## Table of Contents
- [About](#about)
- [Feature List](#feature_list)
- [Getting Started](#getting_started)
- [Usage](#usage)
- [Built Using](#built_using)
- [Authors](#authors)
- [Acknowledgments](#acknowledgement)

## About <a name = "about"></a>
CTQA specializes in identifying the position of a phantom within an image and taking homogeneity measurements specific to the vendor. These measurements are tracked over time and any deviations are sent as notifications to the relevant parties.

*Please Note:* This project requires usage of an Orthanc Server instance to act as an intermediary PACS server for CT machines to submit to.

You can view Orthanc [here](https://orthanc-server.com) and download it [here](https://orthanc-server.com/download.php).

### Feature List <a name = "feature_list"></a>
+ Automated Phantom detection
+ Automated Homogeneity Testing
+ Homogeneity Value Drift Prediction
+ Notifications and Reports through email or a custom method
+ Configurable homogeneity value limits
+ Daily and Weekly Reports
+ Subscribe to specific notification levels (Eg: Failures and Warnings only)

### Screenshots


## Getting Started <a name = "getting_started"></a>
These instructions help you get a copy of the project up and running on your local machine for development and testing purposes. 

See [the wiki's installation section](https://github.com/Brikwerk/ctqa/wiki/Installation) for notes on how to deploy the project on a live system.

### Prerequisites
+ Python 3.5+
+ An accompanying Pip installation
+ Virtualenv (Recommended)

### Installing
If you'd like to setup a virtual environment and install all required packages, navigate to the project root and run the following command:

```
env-setup.bat
```

Otherwise, install all packages through the standard command:

```
pip install -r requirements.txt
```

After the package installations have finished, the application can be launched with the following command:

```
python run.py
```

The appropriate configuration files will be generated in the project root during the initial application launch (or if they aren't present). You can choose to follow through with the application's setup or choose to configure manually.

Details for setting up and configuring the utility can be found on [the wiki](https://github.com/Brikwerk/ctqa/wiki).

Development documentation can be found under "docs/build/html" from the project root.

### Compiling the Executable
To compile CTQA, run:

```
pyinstaller run.spec
```

or for a binary with a console debug output:

```
pyinstaller run-debug.spec
```

## Running the tests <a name = "tests"></a>
CTQA currently uses PyTest to check the validity and accuracy of tests run. The testing suite can be run with the following command:

```
pytest
```

Tests can be found under the "test" directory from the project root.

## Usage <a name="usage"></a>
Add notes about how to use the system.

## Built Using <a name = "built_using"></a>
- [PyInstaller](http://www.pyinstaller.org) - Application Wrapper
- [Tkinter](https://wiki.python.org/moin/TkInter) - Application Framework
- [OpenCV](https://opencv.org) - Phantom Detection

## Author <a name = "authors"></a>
- [@brikwerk](https://github.com/brikwerk)

## Acknowledgements <a name = "acknowledgement"></a>
- Giampaolo Rodola' for usage of LogWatcher