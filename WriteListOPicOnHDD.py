# -*- coding: utf-8 -*-
"""
Created on Wed Nov  2 14:56:26 2016

Helper function that prints a list 
of images in a specified location. 
Images files are numbered in the order 
in its position in the list. (so if 
List is sorted in a specific way, 
numbering should reflect that sorting)

INPUT: list of images, path as a string object
    to convert it to Path object in pathlib
OUTPUT: printed images in the location

@author: Ludwig Bartsch - SCIPP / TU Berlin
"""

import cv2
import numpy as np
from pathlib import Path
#import os # to create directory if necessary

def WriteListOPicOnHDD(listOPic, path): 
    location = Path(path)
    # checking if folder in location exists, 
    # if not -> create
    location.mkdir(exist_ok = True, parents = True)
    
    imgNumber = 1 # start numbering of Image    
    for img in listOPic: 
        assert type(img) == np.ndarray # structure as image? 
        if img.dtype == 'uint16': 
            filename = 'sepASIC_'+str(imgNumber)+'.tif'
        else:       
            filename = 'sepASIC_'+str(imgNumber)+'.jpg'
        filelocation = Path(str(location), filename)
        cv2.imwrite(str(filelocation), img)
        imgNumber = imgNumber + 1