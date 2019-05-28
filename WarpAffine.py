# -*- coding: utf-8 -*-
"""
Created on Sun Oct 30 19:16:22 2016
Affine warp to align an image with a template. 
Uses EnhancedCorrelation Coefficients (ECC) 
Maximization to compute transformation matrix 
to transform img onto the template. Both images
must be from the same object and not too 
different. 

In order to work the images must not be too big. 
This version resizes image with a resizefactor, 
computes the transformation matrix, modifies the 
matrix to adapt it it bigger size and use the 
matrix on the big original to align it to 
template. WORKS WITH TRANSLATION, MAYBE NOT WITH 
AFFINE!!! (resizefactor only applied to last 
column in matrix, not for the rotation part in 
the first part. Quality was not satisfiing in 
AFFINE mode )


INPUT: template image, img with glue dots, 
    resizeFactor (to change size of image)
OUTPUT: image that is aligned with template
    matrix of transformation

TODO: parameters in function declaration??

@author: Ludwig Bartsch, SCIPP / TU Berlin)
"""

import cv2
import numpy as np
from pathlib import Path

def WarpAffine(template, img, 
               outputLocation = Path.cwd(), 
                resizeFactor = 0.303): 
    if (len(img.shape) == 3): # if image is color convert 2 b&w
        # Convert images to grayscale
        imgGray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    else: 
        imgGray = img
    if (len(template.shape) == 3):
        templateGray = cv2.cvtColor(template,cv2.COLOR_BGR2GRAY)
    else: 
        templateGray = template
    # dimensions for the resized image to calc transformation matrix
    dimTemp = (int(templateGray.shape[1]*resizeFactor), 
           int(templateGray.shape[0]*resizeFactor))    
    dimImg = (int(imgGray.shape[1]*resizeFactor), 
              int(imgGray.shape[0]*resizeFactor))
    
    # resize 
    templSmall = cv2.resize(templateGray, dimTemp)
    imgSmall = cv2.resize(imgGray, dimImg)
    # try canny edge detector to find warp / may be more robust
    # quality depends on minVal, maxVal parameter in cv2.Canny
    #edgeASIC = cv2.Canny(markedASICGray, 150, 350)
    #edgeInput = cv2.Canny(inputGray, 150, 350)    
    
    sizeTemplate = templateGray.shape
    
    # Define the motion model 
    # alternatives: cv2.MOTION_TRANSLATION / cv2.MOTION_HOMOGRAPHY
    warp_mode = cv2.MOTION_AFFINE
    
    # Define 2x3 or 3x3 matrices and initialize the matrix to identity
    if warp_mode == cv2.MOTION_HOMOGRAPHY :
        warp_matrix = np.eye(3, 3, dtype=np.float32)
    else :
        warp_matrix = np.eye(2, 3, dtype=np.float32)
        
    # Specify the number of iterations.
    number_of_iterations = 800
 
    # Specify the threshold of the increment
    # in the correlation coefficient between two iterations
    termination_eps = 1e-4;
    
    # Define termination criteria
    criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 
                number_of_iterations, termination_eps)
    # set cc to negative, in order to have acceptable value for printing results
    # in case warping fails -> 0 no correlation
    cc = 0
    # resize images    
    try: 
        # Run the ECC algorithm. The results are stored in warp_matrix.
        (cc, warp_matrix) = cv2.findTransformECC(templSmall, imgSmall,
                            warp_matrix, warp_mode, criteria)
        
        # apply scaling factor to translation part of the matrix
        warp_matrix[:,2] = warp_matrix[:,2]*(1/resizeFactor)
        
        if warp_mode == cv2.MOTION_HOMOGRAPHY :
            # Use warpPerspective for Homography 
            imgWarped = cv2.warpPerspective (img, warp_matrix, 
                                               (sizeTemplate[1],
                                                sizeTemplate[0]), 
                                                flags=cv2.INTER_LINEAR + 
                                                cv2.WARP_INVERSE_MAP +
                                                cv2.WARP_FILL_OUTLIERS)
        else :
            # Use warpAffine for Translation, Euclidean and Affine
            imgWarped = cv2.warpAffine(img, warp_matrix, 
                                         (sizeTemplate[1],
                                          sizeTemplate[0]), 
                                           fillval=(255, 255, 255, 255),
                                            flags=cv2.INTER_LINEAR+ 
                                            cv2.WARP_INVERSE_MAP+
                                            cv2.WARP_FILL_OUTLIERS)
        # create output folder if not already there
        outputPath = Path(outputLocation)
        outputPath.mkdir(exist_ok = True, parents = True)
        # create filenames for saving warped and marked ASIC image                                    
        fileLocationWarped = Path(str(outputLocation),'01_warpedImage.jpg') 
        fileLocationMarked = Path(str(outputLocation),'02_markedASIC.jpg')
        # saving files
        cv2.imwrite(str(fileLocationWarped), imgWarped)
        cv2.imwrite(str(fileLocationMarked), template)    
        # TODO: Better Results with changing parameter cv2.INTER_LINEAR flags specified
        # in documentation for cv2.resize() ??
    except: 
        pass
        imgWarped = img
        warp_matrix = [-1]
    # return imgWarped, warp_matrix
    return imgWarped, warp_matrix, round(cc, 3)