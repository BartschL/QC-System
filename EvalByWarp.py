# -*- coding: utf-8 -*-
"""
Created on Tue Nov  8 13:24:11 2016
Evaluates an image by transforming it
(warp affine) onto a desired image of 
good dots. Subtracts the desired from the 
warped and returns the number of positive 
and negative pixel in image. 
Negative pixel stand for missing glue.
Positive pixel stand for glue in areaes in which
non should be.  

INPUT: Path to average image, input image
OUTPUT: number of negative and positive pixel in image

@author: Ludwig Bartsch - SCIPP / TU Berlin
"""
from pathlib import Path
import cv2
import numpy as np
import math
from Eval_CountBlackPixels import CountBlackPixels
from WarpAffine import WarpAffine

#####################HELPER FUNCTIONS #########################################
"""
evalSubtracted takes in an np.array(dtype = np.int16)
and find the numbers of negative values and the number bigger
than abs(10) [change to np.int16 leaves rounding error and 0 
become ones]

INPUT: subtracted image as np.array(dtype = int16)
OUTPUT: number of negative pixel bigger -10
        number of nonwhite pixel( value bigger 10) 
"""
def evalSubtracted(subtracted):
    temp = subtracted    
    temp[temp < -10] = -32000
    temp[temp > 10] = 32000
    neg = np.count_nonzero(temp == -32000)
    pos = np.count_nonzero(temp == 32000)
    return neg, pos
    
"""
inverting a binary image so black becomes 255 and white 0
INPUT: binary image with 0 as black and 255 as white
OUTPUT: Inverted binary image. 
"""
def invertBinary(image):
    image = (255-image)
    return image
    
###############################################################################

def EvalByWarp(imgToEval, path2AverageImage):

    perfectImg = cv2.imread(str(path2AverageImage))
    
    # resize input to perfect image size
    w = perfectImg.shape[1]
    h = perfectImg.shape[0]
    
    resizedInput = cv2.resize(imgToEval, (w,h), interpolation = cv2.INTER_CUBIC)
    
    # warping of image
    warped, matrix, cc = WarpAffine(perfectImg, resizedInput, resizeFactor = 1)
    # if color img - convert to grayscale
    if (len(warped.shape)==3):
        warped = cv2.cvtColor(warped,cv2.COLOR_BGR2GRAY)
    elif (len(perfectImg.shape)==3):
        perfectImg = cv2.cvtColor(perfectImg,cv2.COLOR_BGR2GRAY)
    
    # invert for subtraction
    warpedInv = invertBinary(warped)    
    perfectInv = invertBinary(perfectImg)
         
    # change of type to allow minus sign for subtraction of images
    newwarped = np.array(warpedInv, dtype = np.int16) 
    newperfect = np.array(perfectInv, dtype = np.int16)
   
    # correct conversion(uint8 to int16) errors 
    mask = np.logical_and(newperfect < 10, newperfect > -10) 
    newperfect[mask] = 0   
    newperfect[newperfect >50] = 255
    mask = np.logical_and(newwarped < 10, newwarped > -10) 
    newwarped[mask] = 0 #   
    newwarped[newwarped > 240] = 255
        
    #subtraction
    subtracted = newwarped - newperfect
    #mask = np.logical_and(subtracted < 10, subtracted > -10) 
    #subtracted[mask] = 0
    
    
    neg = 0
    pos = 0
    neg, pos = evalSubtracted(subtracted)    
       
    
    """
    # change image format to numpy array and allow negative numbers 
    #(for subtraction)
    signed_warped = np.array(warped, dtype = np.int16)    
    #signed_perfect = np.array(perfectImg, dtype = np.int16)    
    
    #substract warped from perfect image. If warped image, 
    # was close to the perfect, the black pixel number in the
    # substracted image is small, if not it is high. 
    substractedImg = signed_warped - perfectImg    
    #add 255 to reach roughly 0, 255 as a value range    
    substractedImg = substractedImg + 255 
    totalPerfect, perfectPixel = CountBlackPixels(perfectImg)
        
    # if warp matrix -1 - no warp possible, images are not same    
    if len(matrix)==1: 
        warpedPixel = 10000000000
    else: 
        #totalWarped, warpedPixel = CountBlackPixels(warped)
        totalWarped, warpedPixel = CountBlackPixels(substractedImg)
    """
    #return math.fabs(warpedPixel-perfectPixel)
    return neg, pos, cc
