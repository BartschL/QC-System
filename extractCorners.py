# -*- coding: utf-8 -*-
"""
Created on Fri Oct 28 15:32:30 2016

Takes the warped image with marked ASIC pads
and extracts the corners of the marked ASIC pads
as coordinates. ASIC pads should be within HSV 
color range(opencv) e.g.:
    [132][200][200] [155][255][255] 

The input img is taken and only the pixels 
in color range [lowerRange, upperRange] are 
taken. The result is a mask with only white 
pixels on the positions of the marked ASIC 
pads. 
After that connectedComponentsWithStats() is
used to compute the locations of the marked 
regions in image. 

Returns these coordinates as in groups of four 
(corners of a rectangle) which are also sorted by
its location. 

INPUT:  warped (alignable) image with marked ASIC pads
        lowerRange - bottom limit of Color Range in HSV 
            that is extracted from the picture
        upperRange - top limit in HSV values
        lowerRange, upperRange HAVE TO BE np.array([])
@author: Ludwig Bartsch - SCIPP / TU Berlin
"""

import cv2
import numpy as np
from SortingXY import SortingXY as SortingXY
from Sharpen import Sharpen

def extractCorners(img, lowerRange = np.array([132,200,200]), 
                        upperRange = np.array([155,255,255])): 
    # conversion to HUE SATURATION and VALUE
    #img = cv2.GaussianBlur(img,(5,5),10.0)
    img = Sharpen(img, degreeOSharpness = 4)    
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
    # rotation could damage corners of marked ASIC pads, blur improve results
    #hsv = cv2.GaussianBlur(hsv,(3,3),10.0)

    ############# Prep for finding corners ###############
    # set HUE value for purple to pint, SATURATION and VALUE can be anything in
    # allowed range, choosen color range easy to write as an intervall in HSV and 
    # is not visible in the current hybrid layout
    # CAREFULL: Colorrange for HSV in OpenCV is different from e.g. GIMP. 
    # In OpenCV: H = [0,180], S= [0,255], V = [0,255]
    
       
    # just take purpelish areas
    mask = cv2.inRange(hsv, lowerRange, upperRange)
    cv2.imwrite('maskedASICPositions.jpg', mask)
    ######### Description of conncetedComponentsWithStats() #####
    #label: size of input img, each entry has value as it's label
    #centroid: matrix with x and y location of each centroid, 
    # row corresponds to label number
    # stats: stats for each label: cv2.CC_STAT_LEFT , cv2.CC_STAT_TOP, 
    # cv2.CC_STAT_WIDTH, cv2.CC_STAT_HEIGHT, cv2.CC_STAT_AREA
    # ret: number of labels
    ret, labels, stats, centroids = cv2.connectedComponentsWithStats(mask)
    
    """
    # changed from harris Corner detection to connectedComponentsWithStats    
    ############# Find Corners ###########
    
    # find Harris corners
    gray = np.float32(mask)
    # Number of Corner findings depends on params in cornerHarris!!
    # lowering the last param leads to multiple solutions for one corner. 
    # for now cv2.cornerHarris(img, 2,3,0.14) works pretty well    
    dst = cv2.cornerHarris(gray,3,3,0.14) 
    
    # threshold to get corners instead of lines
    ret, dst = cv2.threshold(dst,0.005*dst.max(),255,0) 
    dst = np.uint8(dst)
    
    # further refine corner detection 
    # multiple solutions -> see as centroid
    ret, labels, stats, centroids = cv2.connectedComponentsWithStats(dst)
    
    # define the criteria to stop and refine the corners
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.001)
    corners = cv2.cornerSubPix(hsv,np.float32(centroids),(5,5),(-1,-1),criteria)    
    print(type(corners))
    
    # extract positions of corners as pixel index/coordinate
    cornerOASICpads = cv2.findNonZero(corners)
    #cv2.imwrite('foundCornersOASICs.jpg', dst)
    cv2.imwrite('testpictodel.jpg', dst)    
    
    # unpack as two lists of width and height positions
    cornerWidth = list((x[:][0][0] for x in cornerOASICpads))
    cornerHeigth = list((x[:][0][1] for x in cornerOASICpads))
    
    # sort
    cornerWidthSorted, cornerHeightSorted = SortingXY([cornerWidth, cornerHeigth], 
                                                   xy = False) # sort by height first
    
    # CHECK IF CORRECT NUMBER O CORNERS                                         
    if not (len(cornerHeightSorted) % 4 == 0): # 
        raise Exception(
    "Number of found corners is not a multiple of 4 -> not all rectangles recognizable. "+ 
    "Vertical number of corners in image is: "+ str(len(cornerHeightSorted)))
        
    # check symmetrie by histogram of heigths and widths. if first and last bucket
    # unequal number of entries or any entries inbetween -> geometry does not
    # include identical rectangles
   
    buckets = np.histogram(cornerWidthSorted,4)
    if (buckets[0][0]!= buckets[0][-1]):
        raise Exception(
        "Symmetry condition of recognized rectangles of the Marked ASICs not fullfilled. Maybe not all points were correctly identified. ")
    del buckets
       
    # regroup into 4 corners per ASIC pad 
    rectangleHeightPos = list(zip(*[iter(cornerHeightSorted)]*4) )
    rectangleWidthPos = list(zip(*[iter(cornerWidthSorted)]*4) )     
    """
    return (ret, labels, stats, centroids)                                          