# -*- coding: utf-8 -*-
"""
Created on Fri Nov 04 11:34:04 2016

Takes a list of images ( seperated ASIC images ) 
and applies some preprocessing to ensure proper
evaluation of glue dots in possible. 
Histogramm spreading is used to enhance the 
contrast of the glue dots to the background. 
Threshold is applied to seperate glue area 
from background. 

INPUT: List of images
OUTPUT: List of "enhanced" images

@author: L.Bartcsch UCSC
Histogram of a metal plate with glue on it. 
"""

#TODO: computation to enhance blobs leads to bigger 
# area of black pixels so size calculations are to big!!!

import cv2
import numpy as np
from itertools import product

"""
Helper function to map an uint16 image onto an intervall
[2low, 2high] in uint8 format. conversion necessarry to 
use threshold function. 
"""

def map2Intervall(img, lowRange, highRange): 
    high = np.amax(img)
    low = np.amin(img)
    output = np.ndarray(img.shape, dtype = np.uint8)
    h,w = img.shape
    for pos in product(range(h),range(w)):
        pixel = img.item(pos)
        relative = float(pixel - low) / (high-low)
        output[pos] = int(relative*highRange-lowRange)
    return output
    
def PreprocessingSingleASICs(listOImages):
    outputList = []
    #FOR SAVING GRAYSCALED TIFF: i = 0
    for img in listOImages: 
        #FOR SAVING GRAYSCALED TIFF: filename = 'graytiff_'+str(i)+'.jpg'
        if (img.dtype == 'uint8' and len(img.shape)==3):
            # denoise        
            #denoisedImage = cv2.fastNlMeansDenoisingColored(img,None,5,5,5,15)
            denoisedImage = cv2.GaussianBlur(img,(5,5),0)
            grayscaled = cv2.cvtColor(denoisedImage, cv2.COLOR_BGR2GRAY)
        else: 
            
            if(img.dtype == 'uint16'):
                grayscaled = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                # map lowest/highest uint16 value onto [0,255] to apply threshold
                grayscaled = map2Intervall(grayscaled, 0, 255)
                
                #FOR SAVING GRAYSCALED TIFF: cv2.imwrite(filename,grayscaled)
                #FOR SAVING GRAYSCALED TIFF: i = i+1
            
            else: 
                grayscaled = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
            grayscaled = cv2.GaussianBlur(grayscaled,(5,5),0)    
            #grayscaled = cv2.fastNlMeansDenoising(grayscaled, None, 7,7,21)
        # TODO: necessary to denoise image? propably not. Maybe after?         
        #if img.dtype == 'uint16': 
        #    denoisedImage = cv2.fastNlMeansDenoising(img, None, 5,5,5,15)
        #else: 
        #    denoisedImage = cv2.fastNlMeansDenoisingColored(img,None,5,5,5,15)
        
        #TODO: Check if threshold leaves empty or full pix 
        # use histogramspreading and inRange to find glue 
        # spread out the histogram to increase contrast
        #equalized = cv2.equalizeHist(grayscaled)
    
        # just take darker spots in image (TODO: threshold value?)
        #equalized = cv2.inRange(equalized, 45, 255)#, 65536
        
            
        ret3,glueSeperated = cv2.threshold(grayscaled,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
        #else: 
        #    ret3,glueSeperated = cv2.threshold(grayscaled,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
        """ not working"""
        # erosion followed by dilation -> delete white pixels in black area
        kernel = np.ones((3,3), np.uint8)     

        #glueSeperatedEroded = cv2.morphologyEx(glueSeperated, 
        #                                       cv2.MORPH_OPEN, 
        #                                       kernel)
        # dilation followed by erosion -> delete pixel in white area                                       
        #glueSeperatedEroded = cv2.morphologyEx(glueSeperated, 
        #                                       cv2.MORPH_CLOSE, 
        #                                       kernel)          
                                       
        # delete black pixel layers and grow them back to smoothen dots
        glueSeperatedEroded = cv2.erode(glueSeperated, kernel, iterations = 1)
        glueSeperatedEroded = cv2.dilate(glueSeperatedEroded, kernel, iterations = 1)
        
        
        
        
        
        """ # use get connectedComponents to find biggest blobs?
        # get connected components  
        ret, labels, stats, centroids = cv2.connectedComponentsWithStats(glueSeperated)
        
        # iterate over
        """
        """ Leftover from checking result of histogram and procedures
        # Histogram: cv2.calcHist(images, channels, mask, histSize, ranges[, hist[, accumulate]])
        hist = cv2.calcHist([equalized], [0], None, [2],[0,256])
        cv2.imwrite('sample09 _processed.jpg',equalized)
        #plt.hist(equalized.ravel(), 256, [0,256]);  plt.show()
        #plt.safefig('sample7_histo',format='pdf')
        #cv2.waitKey(0) & 0xFF # wait for keyboard input
        #cv2.destroyAllWindows()
        """
        outputList.append(glueSeperatedEroded)
    return outputList 
