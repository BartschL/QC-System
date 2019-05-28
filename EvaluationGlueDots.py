# -*- coding: utf-8 -*-
"""
Created on Mon Nov  7 14:51:48 2016

Evaluation of Glue Dots

computes: Area of Glue to No Glue Area Ratio
Counts Number of Glue Dots
Checks Similarity with good (maybe artificial) sample

INPUT: List of single preprocessed ASIC images, 
    list of single unprocessed ASIC images, 
    path to averaged glue dot image,
    dimension(width, height) of the Trainingset for PCA,
    path to Principle Components as Path object
OUTPUT: List of Strings containing OK / NOT OK 
    for every img in input list

@author: Ludwig Bartsch - SCIPP / TU Berlin
"""
#import cv2
from Eval_CountBlackPixels import CountBlackPixels as Count
from Eval_BlobDetector import BlobDetector 
from EvalByWarp import EvalByWarp
from EvalByPCA import EvalByPCA as EvalPCA

def EvaluationGlueDots(listOprocessed, listOPreprocessed, path2PerfectDot, dimension, 
                       path2PC): 
    evaluated = [['Status',
                  'AreaRatio',
                  'BlobNumber', 
                  'ShapeSimilarityWarpNeg',
                  'ShapeSimilarityWarpPos',
                  'ShapeSimilarity_PCA']]
    
    # specify criteria for good / bad
    upperAreaRatio = 0.35
    lowerAreaRatio = 0.1
    
    # evaluate all images
    for img in listOprocessed: 
        listOEvaluated = ['', 0, 0, 0, 0, 0]        
        # get results from eval functions
        totalPixelNo, blackPixelNo = Count(img)
        areaRatio = blackPixelNo / totalPixelNo
        blobNumber = BlobDetector(img)
        negPixelNumber, posPixelNumber, cc = EvalByWarp(img, path2PerfectDot)
        
        # store results
        listOEvaluated[1] = areaRatio
        listOEvaluated[2] = blobNumber
        listOEvaluated[3] = negPixelNumber
        listOEvaluated[4] = posPixelNumber
        listOEvaluated[5] = cc
        
        if areaRatio < lowerAreaRatio or areaRatio > upperAreaRatio: 
            #evaluated.append('NOT OK', 'Area'+str(areaRatio))
            listOEvaluated[0] = str('NOT OK')
        elif not blobNumber == 5: 
            #evaluated.append('NOT OK - Number'+str(blobNumber))
            listOEvaluated[0] = str('NOT OK')
        else:
            #evaluated.append('OK - AreaRatio: '+str(areaRatio)+' BlobCount: '+str(blobNumber))
            listOEvaluated[0] = str('OK')
        
        # append 5 criteria to result list
        evaluated.append(listOEvaluated)
        #line = line+1
    # use unprocessed for PCA    
    #for index, img in enumerate(listOunprocessed):
        # result from PCA
        #PCASimilarity = EvalPCA(img, dimension, path2PC)
        #evaluated[index][5] = PCASimilarity
        
    return evaluated