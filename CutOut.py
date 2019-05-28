# -*- coding: utf-8 -*-
"""
Created on Sat Oct 29 19:46:43 2016

Cut out the images from the warped input image. 

INPUT:  img: warped image so it is aligned with marked 
        ASIC pic 
        positionInfo: from connectedComponentsWithStats()
        containing Positions of ASIC pads in matrix (each
        row containing: leftmost pixel, topmost pixel, 
        width, heigth and area)
        
OUTPUT: list of sections from image img, as specified in 
        the positionInfo matrix, 
        (all entries in positionInfo which area deviates 
        too much from average area are not used - unwanted 
        artifacts)

@author: Ludwig Bartsch, SCIPP / TU Berlin
"""
#import math
import numpy as np
import statistics
#import operator

def CutOut(img, positionInfo): 
    
    # delete not wanted entries like the background by eval 
    #size differences
    averageArea = statistics.median(positionInfo[:][:,4])
    
    # every area with more than 5000 pixels difference from 
    # average pixel number in image is discarded (presumably only background
    # has that amount of pixel difference) 
    # ATTENTION: if value too low not all positions are accepted -> marked 
    # ASIC pad size differs - > warping of image also changes size of images, 
    # leading to size differences which mess up at this point
    positions = [item for item in positionInfo if 
                ( np.absolute(item[4]-averageArea) < 5000) ]
    
    # sort positions by height and by width
    #sortedPos = sorted(positions, key = operator.itemgetter(1,0))    
    sortedPos = sorted(positions, key = lambda x: (x[1], -x[0]))    
    
    # list of seperated images
    seperatedImages = []
    
    for line in sortedPos: 
        singleASICpad = img[line[1]:(line[1]+line[3]), line[0]:(line[0]+line[2])]
        seperatedImages.append(singleASICpad)
        
    return seperatedImages, sortedPos