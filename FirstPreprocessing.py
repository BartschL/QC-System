# -*- coding: utf-8 -*-
"""
Created on Thu Oct  6 15:16:01 2016

Preprocessing of input images with hybrids on a panel. Goal 
is to enhance image quality so fiducials may be easier to 
find. 
INPUT: file location as STRING for 
    - image to preprocess
    - calibration parameter txt file and
    - output location to save undistorted image
    (matrix and distortion param)
    
OUTPUT: processed and enhanced image

@author: Ludwig Bartsch - SCIPP / TU Berlin
"""

from pathlib import Path
import cv2 
import numpy as np
#import numpy as np
from ReadInCamCalibration import ReadInCamCalibration as readInCC
from Sharpen import Sharpen
def FirstPreprocessing(path, camCalibrationPath, outputData):
    
    try:
        filelocation = Path(path)   
        if not filelocation.exists():
            raise NameError('File for preprocessing does not exist. ')
        # read in image from path and process
        
        img = cv2.imread(str(path), -1)
        assert type(img) == np.ndarray # is valid image format
        # custom sharpen function degreeOSharpness = 4 looks the best
        # TODO: Necessary to sharpen here?? 
        #img = Sharpen(img, degreeOSharpness = 4)        
        
        ######### UNDISTORT ################
        # initiate undistortion        
        camMatrix, camCoeff = readInCC(camCalibrationPath)
        # init camMatrix
        h,  w = img.shape[:2]
        newcameramtx, roi=cv2.getOptimalNewCameraMatrix(camMatrix,camCoeff,(w,h),1,(w,h))
        
        # undistort
        undst = cv2.undistort(img, camMatrix, camCoeff, None, newcameramtx) 
        
        # enhance image quality if possible 
        #blured = cv2.GaussianBlur(undst,(3,3),10.0)
        #sharp = cv2.addWeighted(undst, 1.5, blured, -0.2, 0, undst)
                
        
        # custom sharpen function degreeOSharpness = 4 looks the best
        sharpened = Sharpen(undst, degreeOSharpness = 4)        
        # create path to save undistorted file for e.g. Manual Marking of ASIC
        
        if(img.dtype == ('uint16')):
            path2SaveUndst = Path(str(outputData), 'undistortedPic.tif')        
        else:
            path2SaveUndst = Path(str(outputData), 'undistortedPic.jpg')
        
        cv2.imwrite(str(path2SaveUndst), sharpened)
        
        # TODO: Crop if image has to much background in it. 
        # TODO: Resize it afterwards to match the size of markedASIC Image        
        
        return sharpened
    except IOError: 
        print('Error in Preprocessing ')
    
    
