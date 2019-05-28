# -*- coding: utf-8 -*-
"""
Created on Fri Oct 28 14:18:35 2016

ASIC pad extraction is handled in this file. 
It takes in the input image with glue dots on 
ASIC pads, that needed to be seperated as single 
images. The ASIC locations are either loaded from 
a file, or if the layout changed, are loaded from 
a image with marked ASIC pads and stored for later 
use. 

INPUT: image file with glue dots on ASIC pads for 
    extraction, Boolean for new Layout -> compute 
    new coordinates
OUTPUT: matrix of single ASIC pads image. matrix
    shape corresponds to the ASIC positions on the 
    panel

@author: Ludwig Bartsch, SCIPP / TU Berlin
"""

#import cv2
from extractCorners import extractCorners
from CutOut import CutOut


def SeperateASICs(warpedImg, markedASIC): 
     
    # get shape and position information from ASIC pads
    ret, labels, stats, centroids = extractCorners(markedASIC)
    # save position information for later use!
    # TODO: ! 
    
    # TODO: load shape and position information    
    
    #warp input image to align it with warped ASIC pic
    #warpedImg = warpImage(img, template)
    # seperated images
    seperatedImages = []
    seperatedImages, positions = CutOut(warpedImg, stats)
        
    return seperatedImages, positions