# -*- coding: utf-8 -*-
"""
Created on Wed Oct 26 12:48:08 2016

@author: User
"""
import cv2
import numpy as np

def Sharpen(img, degreeOSharpness = 4):
    
    if degreeOSharpness > 4 or degreeOSharpness < 1: 
        degreeOSharpness = 2
    # generating the kernel
    if degreeOSharpness == 1: 
        kernel_sharpen = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
    elif degreeOSharpness == 2:
        kernel_sharpen = np.array([[1,1,1], [1,-7,1], [1,1,1]])
    elif degreeOSharpness == 3: 
        kernel_sharpen = np.array([[-1,-1,-1,-1,-1], [-1,2,2,2,-1], 
                                     [-1,2,8,2,-1], [-1,2,2,2,-1], 
                                    [-1,-1,-1,-1,-1]]) / 8.0
    elif degreeOSharpness == 4: 
        kernel_sharpen = np.array([[0,-1,0], [-1,5,-1], [0,-1,0]])
    
    # applying kernel to the input image
    output_1 = cv2.filter2D(img, -1, kernel_sharpen)
    return output_1