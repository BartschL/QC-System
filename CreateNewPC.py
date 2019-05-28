# -*- coding: utf-8 -*-
"""
Created on Wed Dec 07 09:18:14 2016

This function creates a new principle components 
matrix from a set of training data. The principle
components matrix is stored and can be later used 
to measure similarity of a picture with the training 
set pictures. 

This function reads in a file location of training
pictures and a set of dimensions to resize all 
training images to the same size. Result is saved as
numpy(.npy) file  in the input folder
Each image is reshaped as a long vector and vertical
stacked on a matrix X. The mean of all the images is 
calculated and so X can be demeaned. 
After that the eigenvalues of the covariance matrix 
of the stacked matrix can be the principle components 
used to project new data in the eigenspace. 


INPUT: location of trainingset as Path-object, 
    dimension as list of (width, height) - 
    dimensions must be same image ratio as input images
    location to save PCA data
OUTPUT: principle components and mean in npy-File
@author: Ludwig Bartsch - SCIPP / TU Berlin
"""

from pathlib import Path
import glob
import cv2
import numpy as np
import pylab

# HELPER FUNCTIONS!
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

def ReadInPics(path, dimensions):
    """
    Helper function to read in multiple images 
    from a location and process the images so 
    it can be used for PCA and Evaluation. 
    """    
    
    width = dimensions[0]
    height = dimensions[1]
    
    # read in all training images
    path2TrainingSet = Path(str(path), '*.jpg')
    images = glob.glob(str(path2TrainingSet))
    #numberOTrainingImg = len(images) 
    
    for pix in images: 
        img = cv2.imread(pix)
        
        # cut edges in case marked asic image is not perfect
        # only cut left, upper and lower edge. right edge alway golden
        img = img[10:img.shape[0]-10, 10:]
        #################################################################
        # resize but keep aspect ratio # redone for fixed pixel number with 
        # roughly same aspect ratio
        # r = imageWidth / img.shape[1] # ratio of old to new width
        # newDim = (int(imageWidth), int(img.shape[0] * r))
        #################################################################
        #img =img[0:128,0:159]
        resized = cv2.resize(img, (width, height), 
                             interpolation = cv2.INTER_LINEAR)
        
        # denoise        
        denoisedImage = cv2.fastNlMeansDenoisingColored(resized,None,5,5,5,15)
        
        # convert2 Grayscale if color
        if len(denoisedImage.shape) == 3:
            denoisedImage = cv2.cvtColor(denoisedImage, cv2.COLOR_BGR2GRAY)
        
        # substract mean from image
        mean = denoisedImage.mean()
        demeaned = denoisedImage - mean*np.ones([denoisedImage.shape[0], denoisedImage.shape[1]])
        #demeaned[np.where(demeaned < 0)] = 0
        
        # reshape image matrix to long thin vector of all rows
        reshaped = demeaned.ravel()
        #trainingImages.append(reshaped)    
        try:
            matrix = np.vstack((matrix, reshaped))
        except:
            matrix = reshaped
    return matrix


# CREATE Principle Components and necessary boundarys for eval
def CreateNewPC(path2TrainingData, path2GoodData, dimensions, path2SavePCAData): 
    trainingImg = ReadInPics(path2TrainingData, dimensions)
        
    # get mean and demean imagematrix
    mean = np.mean(trainingImg, axis = 0)
    
    # demean by substract mean of all rows in matrix
    matrixDemeaned = pylab.demean(trainingImg, axis = 0)

    # covariance cov = 1/(N-1) XX.T - matrix must be 
    # transposed for it so samples are columns and 
    # features are in rows
    cova = np.cov(matrixDemeaned.T)
    
    # compute eigenvalues and eigenvectors
    eigVa, eigVe = np.linalg.eig(cova)
    # sort by eigenvalues    
    idx = eigVa.argsort()[::-1]
    eigVa = eigVa[idx]
    eigVe = eigVe[idx]
    
    assert np.all( eigVa[:-1] >= eigVa[1:] )  # sorted
    
    # save in numpy file 
    np.save('eigVe', eigVe)
    np.save( str(Path(str(path2SavePCAData), 'eigVe.npy')), eigVe)
    np.save( str(Path(str(path2SavePCAData), 'mean.npy')), mean)
    np.save( str(Path(str(path2SavePCAData),'numberOTrainingsetImg.npy')),trainingImg.shape[0])
    
    # create new matrix of other good images to get
    # boundarys of good projected images
    goodImg = ReadInPics(path2GoodData, dimensions)  
    
    # project on PC
    projectedGoodImg = ProjectOnPC(eigVe, goodImg, mean, dimensions)
    maxGood = np.apply_along_axis(lambda x: (max(x)),0, projectedGoodImg)
    minGood = np.apply_along_axis(lambda x: (min(x)),0, projectedGoodImg)
    
    # save max and min for good projections
    np.save(str(Path(str(path2SavePCAData), 'maxBoundary.npy')), maxGood)
    np.save(str(Path(str(path2SavePCAData), 'minBoundary.npy')), minGood)