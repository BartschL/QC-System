# -*- coding: utf-8 -*-
"""
Created on Sun Nov 20 16:58:17 2016

Computes the similarity of images with 
the Principle Component Analysis. First 
the saved principle components from the
trainingset is loaded. The input image
is processed in the same way as the 
trainingset, to archive same dimensions, ect. 

The input image is then projected onto 
the eigenspace with the loaded pca. 
As a measurement for similarity the components 
of the projected vector are summed up. (except 
the first n components, where n is the number of 
trainingsets)

INPUT: Image to compute similarity
    Pathobject to computed principle components
    Pathobject to computed mean
    Pathobject to number of used training images 
    dimensions to fit the input image to 
    the size of the trainingset images

@author: Ludwig Bartsch - SCIPP / TU Berlin
"""
import cv2
import numpy as np
from pathlib import Path

# HELPER FUNCTION!
def ProjectOnPC(principleComp, listOImages, mean, dimensions): 
    """
    Helper Function to work on the listOImages to 
    calculate the projected vectors from the input 
    images onto the principle components from the 
    trainingset. 
    INPUT: principleComponents principleComp(pxp), 
        list of images to project on PC (Nxp)
        mean from trainingset (p,1)
    """    
    
    # one image or list of images? 
    # demean image with mean of trainingset
    if listOImages.shape[0] == principleComp.shape[0]: 
        demeaned = listOImages - mean
    else:
        demeaned = np.apply_along_axis(lambda x: x-mean,1,listOImages)
    # project each picture onto the PC - (Nxp)
    if listOImages.shape[0] == principleComp.shape[0]:
        projected = np.dot(principleComp.T,demeaned)
    else:
        projected = np.apply_along_axis(lambda x: np.dot(principleComp.T,x),1,demeaned)    

    return projected


# EVAL FUNCTION
def EvalByPCA(img, dimension, path2PC):
    width = dimension[0]
    height = dimension[1]    
    
    # cut edges from input image to make sure only gold pad
    # in background
    img = img[10:img.shape[0]-10, 10:]    
    
    
    # resize img
    resized = cv2.resize(img, (width, height), 
                         interpolation = cv2.INTER_LINEAR)
                         
    # denoise        
    if(img.dtype == 'uint16'):
        denoisedImage = resized
    else: 
        denoisedImage = cv2.fastNlMeansDenoisingColored(resized,None,5,5,5,15)
    
    # if color change to b&w    
    if len(denoisedImage.shape) == 3: 
        denoisedImage = cv2.cvtColor(denoisedImage, cv2.COLOR_BGR2GRAY)
    
    # substract mean to get rid of background information
    mean = denoisedImage.mean()
    demeaned = denoisedImage - mean*np.ones([denoisedImage.shape[0], 
                                             denoisedImage.shape[1]])
    #demeaned[np.where(demeaned < 0)] = 0
        
    # reshape to long vector [width*height]
    ImgAsVector = demeaned.ravel() 
    

    # create paths
    path2Mean = Path(str(path2PC),'mean.npy') 
    path2eigVe = Path(str(path2PC),'eigVe.npy')
    path2NumberTrainingsets = Path(str(path2PC),'numberOTrainingsetImg.npy')
    path2maxBoundary = Path(str(path2PC),'maxBoundary.npy')     
    path2minBoundary = Path(str(path2PC),'minBoundary.npy')    
    
    # load mean from npy file
    #with open(str(path2Mean)) as mean_file:    
    mean = np.load(str(path2Mean))
    assert (len(ImgAsVector) == len(mean) ) # same dimension
    
    # load principle components     
    #with open(str(path2PC)) as PC_file:    
    eigVe = np.load(str(path2eigVe))
    
    # load number of trainingsets used for pca TODO: NotUsed? 
    #trainingsetNumber = np.load(str(path2NumberTrainingsets))
    
    # load boundarys of good images
    minBoundary = np.load(str(path2minBoundary))
    maxBoundary = np.load(str(path2maxBoundary))    
    
    # convert 2 numpy array    
    #eigVe = np.asarray(US)    
    
    projectedImage = ProjectOnPC(eigVe, ImgAsVector, mean, (width, height))
    
    # ignore first N=Number of TrainingImages cause it contains 
    # the most variations. "Good" and "Bad" images have a lot of variation
    # here. Just take the rest. Images different from trainingset images 
    # will have difference here
    # cutProjectedImg = projectedImage[(5/6 * len(projectedImage)):]
    
    # eval by adding number if a projected component is outside of
    # max/min boundary of set of good images
    
    eval = 0
    for index, value in enumerate(projectedImage):    
        if value > maxBoundary[index] or value < minBoundary[index]:
            eval += 1
    return eval
    # sum up absolute values of cut projection as measurement
    #return np.sum(np.absolute(cutProjectedImg))