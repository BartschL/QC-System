# -*- coding: utf-8 -*-
"""
Created on Tue Nov 2 13:46:46 2016
Main Program for QR-Control of glue dots on a panel with hybrids. 
This part of the programm watches for new input pictures from the 
camera. If there is a new picture it moves it and starts 
processing. 

Image processing is: 
    - Preprocessing to enhance image (undistortion - eventually sharpen)
    - Image Registration 
    - ASIC Seperation
    - further preprocessing(threshold, makedcontour, 
      histogramspreading)
    - send picture to evaluation (Area calculation, Blob counting 
      and Shape Similarities)
    - present results
@author: Ludwig Bartsch - SCIPP / TU Berlin
"""
#####################################################
# standart libs
import time
from pathlib import Path
import shutil
import numpy as np
import cv2
import sys, getopt

#custom imports
#from TemplateMatching import TemplateMatching as TM
from FirstPreprocessing import FirstPreprocessing as FirstPreProc
from WarpAffine import WarpAffine as Warp
from SeperateASICs import SeperateASICs 
from WriteListOPicOnHDD import WriteListOPicOnHDD as WriteOnHDD
from PreprocessingSingleASICs import PreprocessingSingleASICs as PrePro2
from EvaluationGlueDots import EvaluationGlueDots as Eval


def process():
    ######################################################
    #TODO: variable filename as input
    #TODO: Check if correct kind of file / location -> Move it
    
    # set timestamp for naming folders
    timestamp = str(time.strftime("%m%d%Y_%I%M"))
    # creating Path to move input and load template
    path2Input = Path(Path.cwd(),fileLocation, file2Process) # change for actuall image location
    path2CamCalibration = Path(Path.cwd(), fileLocation, file2CamCalibration)
    path2MarkedAndCalibrated = Path(Path.cwd(), fileLocation, file2MarkedASIC)
    path2MarkedForTransfMatrix = Path(Path.cwd(), fileLocation, file2MarkedASICempty)
    path2OutputData = Path(Path.cwd(), outputArea, timestamp )
    # subfolder in the outputfolder of current run for preprocessed images
    path2Preprocessed = Path(Path.cwd(), outputArea, timestamp, outputAreaPrePro2) 
    path2Eval = Path(Path.cwd(), fileLocation, locationOfPerfectDots)
    
    # create folder for output: 
    path2OutputData.mkdir(exist_ok = True, parents = True)
    
    # copy input to output location
    shutil.copy(str(path2Input), str(path2OutputData)) # copy original file
    
    
    ######################################
    ### Image Pipeline starts here   #####
    ######################################
    
    
    # Preprocessing: undistort and propably sharpening for input image
    # May be needed: Eval Preprocessing ??
    enhancedImage = FirstPreProc(path2Input, path2CamCalibration, path2OutputData)
    assert type(enhancedImage) == np.ndarray # is valid image format
    assert enhancedImage.size > 0 | len(enhancedImage.shape) == 3 # is valid image, not empty and colorspace
    
    # read in marked ASIC Image / Image must be ony that did go through 
    # FirstPreProc() - so it must be undistorted image
    markedASIC = cv2.imread(str(path2MarkedAndCalibrated))
    markedASICempty = cv2.imread(str(path2MarkedForTransfMatrix))
    # check for not emtpy and color image
    assert markedASIC.size > 0 | len(markedASIC.shape) == 3 
    assert markedASICempty.size > 0 | len(markedASICempty.shape) == 3 
    
    # Image Registration - align preprocessed image with image used to mark locations
    # of ASIC - use not markedASIC image - cause Warp will have difficulties finding
    # transformation matrix
    warpedImg, warpmatrix = Warp(markedASICempty, enhancedImage, str(path2OutputData))
    
    # ASIC Seperation - returns a list of images and a list with position information
    seperatedASICs, sortedPositions = SeperateASICs(warpedImg, markedASIC)
    WriteOnHDD(seperatedASICs, path2OutputData)
    
    # Preprocessing II
    preProcessedASICs = PrePro2(seperatedASICs)
    # save preprocessed in Output folder
    WriteOnHDD(preProcessedASICs, path2Preprocessed)
    
    # Evaluation
    
    # Evaluate each picture - Decision Tree
    # Decision Tree not done yet
    evaluatedPositions = Eval(preProcessedASICs, path2Eval)
    # BlobCount
    # Area
    # ShapeSimiliarity

def main(argv):
    # File location path - all in subfolders from the starting
    
    options = { 'fileLocation': 'InputData/',
               'file2CamCalibration' : 'CamCalibration/CamCalibration.txt',
               'file2MarkedASIC': 'markedASICpicture/Marked_ASIC_pads.jpg',
               'file2MarkedASICempty': 'markedASICpicture/Marked_ASIC_pads_empty.jpg',
               'file2Process': 'Image2Process/input.jpg',
               'imageInPipeline': 'fileinprocess.jpg',
               'fiducialTemplate': 'TemplatesForTM/Fiducials_withCorner.jpg',
               'goldCircleTemplate': 'TemplatesForTM/goldpad.jpg',
               'processingArea': 'ProcessingArea/',
               'outputArea': 'OutputData/',
               'outputAreaPrePro2': 'Preprocessed/',
               'locationOfPerfectDots': 'Eval/perfectDots.jpg'
    }

    inputfile = ''
    outputfile = ''
    try:
        opts, args = getopt.getopt(argv,"hi:o:",["ifile=","ofile="])
    except getopt.GetoptError:
        print 'test.py -i <inputfile> -o <outputfile>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
           print 'test.py -i <inputfile> -o <outputfile>'
           sys.exit()
        elif opt in ("-i", "--ifile"):
           inputfile = arg
        elif opt in ("-o", "--ofile"):
           outputfile = arg
    print 'Input file is "', inputfile
    print 'Output file is "', outputfile
    process( options )

if __name__ == "__main__":
   main(sys.argv[1:])