"""
CTQA Phantom Centering

Provides the functionality for detecting the center of a phantom within an image
"""

import cv2
import pydicom
import numpy as np
import matplotlib.pyplot as plt
import uuid
from os import listdir
from os.path import isfile, join


def threshold_image(original_img, threshold):
  """Applies a threshold to a grayscale image"""
  # original_img is numpy array
  # threshold is Hounsfield units
  img = np.array(original_img)
  img[img > threshold] = 255
  img[img <= threshold] = 0

  return img


def get_circles(pixel_array, threshold=-100):
  """Applies Hough Circles to a grayscale image"""
  # pixel_array should be a 2D Array
  # threshold defaults to 100 Hounsfield units 
  # 100 = the equivalent lower bound of soft tissue

  # Thresholding image
  orig_img = np.array(pixel_array)
  img = threshold_image(orig_img, threshold)
  img = np.uint8(img)

  # Hough circles detection
  circles = cv2.HoughCircles(img,cv2.HOUGH_GRADIENT,2.4,100)
  # returning a single circle's coords
  circle_coords = np.uint16(np.around(circles))[0,:]
  
  return circle_coords


def save_image_circles(pixel_array, circles, path):
  """Saves grayscale image with circle drawn"""
  orig_img = np.uint8(pixel_array)
  cimg = cv2.cvtColor(orig_img,cv2.COLOR_GRAY2BGR)

  for i in circles:
      # draw the outer circle
      cv2.circle(cimg,(i[0],i[1]),i[2],(0,255,0),2)
      # draw the center of the circle
      cv2.circle(cimg,(i[0],i[1]),2,(0,0,255),3)
  
  save_file = join(path, str(uuid.uuid4()) + '.jpg')
  cv2.imwrite(save_file, cimg)


def set_window(pixel_array, window_level, window_width):
  """Sets the window level and width for the image"""
  scale_img = np.array(pixel_array)
  # Getting low and high values
  low = window_level - window_width/2
  high = window_level + window_width/2

  def bin_function(i, window_level, window_width, high, low):
    """Bins image with high and low levels"""
    # Binning pixel
    if i < low:
      i = 0
    elif i > high:
      i = 255
    else:
      i = (((i - (window_level - 0.5)) / (window_width - 1)) + 0.5) * 255;
    return i
  bin_function = np.vectorize(bin_function)
  scale_img = np.uint8(bin_function(pixel_array, window_level, window_width, high, low))

  return scale_img


def get_scaled_image(ds):
  """Retrieves an appropriately scaled image from a pydicom object"""
  # ds should be a pydicom loaded DICOM CT object
  if hasattr(ds, 'RescaleIntercept') and hasattr(ds, 'RescaleSlope'):
      intercept = ds.RescaleIntercept
      slope = ds.RescaleSlope
      img = np.array(ds.pixel_array)
      img = (img*slope) + intercept
  else:
      img = np.array(ds.PixelData)

  return img


if __name__ == "__main__":
  root = 'audit_files'

  for f in listdir(root):
    save_loc = 'phantom_circle_select'
    save_file = join(save_loc, f+'.jpg')
    curr_file = join(root, f)
    if not isfile(curr_file) or f[0] == '.':
      continue

    print(curr_file)
    ds = pydicom.dcmread(curr_file)
    img = get_scaled_image(ds)

    threshold = -100

    # For showing what the threshold image looks like
    # orig_img = np.uint8(threshold_image(img, threshold))

    # For showing a regular CT image
    orig_img = set_window(img, 0, 50)

    cimg = cv2.cvtColor(orig_img,cv2.COLOR_GRAY2BGR)

    # Hough circles detection
    circles = get_circles(img, threshold=threshold)

    for i in circles:
      # draw the outer circle
      cv2.circle(cimg,(i[0],i[1]),i[2],(0,255,0),5)
      # draw the center of the circle
      print(i[0],i[1])
      cv2.circle(cimg,(i[0],i[1]),2,(0,0,255),5)
    
    cv2.imwrite(save_file, cimg)
