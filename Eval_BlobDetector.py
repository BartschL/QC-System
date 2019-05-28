# -*- coding: utf-8 -*-
"""
Created on Wed Sep 28 11:15:21 2016

Detects Blobs in image and returns the 
number of blobs found in the image. 
Possible to return coordinates of blobs.

Parameters for blob recognition: 
Area in Pixel
Circularity in [0,1]  - roundness (detect rectangles if set to 0 ?)
Convexity in [0,1] - convex / concave
Inertia in [0,1] - round or ellipse?

INPUT: b&w image
OUTPUT: number of detected blobs

@author: L.Bartsch - SCIPP / TU Berlin
"""

import cv2

def BlobDetector(img): 
    #########################################################
    ################# PARAMS FOR BLOB DETECTOR ##############
    #########################################################

    # Set up the SimpleBlobdetector with default parameters.
    params = cv2.SimpleBlobDetector_Params()
         
    # Change thresholds
    params.minThreshold = 110
    params.maxThreshold = 255
    
    #params.filterByColor = True
    #params.SetblobColor = 255     
         
    # Filter by Area.
    params.filterByArea = True
    params.minArea = 70
         
    # Filter by Circularity 
    # hexagon has more circularity than rectangle
    params.filterByCircularity = True
    params.minCircularity = 0.4
         
    # Filter by Convexity / circle has convexity 1
    params.filterByConvexity = True
    params.minConvexity = 0.6
         
    # Filter by Inertia / ellipse has inertia [0,1[ circle has 1
    params.filterByInertia =True
    params.minInertiaRatio = 0.4
    
    
    # Set up the detector with default parameters.
    detector = cv2.SimpleBlobDetector_create(params)
    
    # Detect blobs.
    #img = 255-mask
    keypoints = detector.detect(img)
    
    return len(keypoints)
