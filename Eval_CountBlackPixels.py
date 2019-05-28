# -*- coding: utf-8 -*-
"""
Created on Mon Oct 24 11:37:32 2016

Calulates the area of the black pixels in the 
picture by counting. 

INPUT: b&w(!) image 
OUTPUT: number of total pixels & black pixels

@author: Ludwig Bartsch - SCIPP / TU Berlin
"""

import cv2

def CountBlackPixels(img): 
    
    nonZeroPixels = cv2.findNonZero(img) # returns coord of nonzero
    numberOPixels = img.size
    #count number o nonzero coordinates to get black pixels in b&w pix
    return numberOPixels, (numberOPixels - len(list(zip(nonZeroPixels)))) 