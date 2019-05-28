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
import json
import time

#custom imports
from FirstPreprocessing import FirstPreprocessing as FirstPreProc
from WarpAffine import WarpAffine as Warp
from SeperateASICs import SeperateASICs 
from WriteListOPicOnHDD import WriteListOPicOnHDD as WriteOnHDD
from PreprocessingSingleASICs import PreprocessingSingleASICs as PrePro2
from EvaluationGlueDots import EvaluationGlueDots as Eval
from PrintEvalPictures import PrintEvalPictures as PrintEval
from CreateNewPC import CreateNewPC


######################################################
# Glue Dot Pipeline for evaluation of UV Glue on 
# ASIC pads on hybrids on a panel
def process( options ):
    ##################################################
    #TODO: variable filename as input, name output as 
    # input image
    #TODO: Check if correct kind of file / location -> 
    # Move it
    
    # set timestamp for naming folders
    timestamp = str(time.strftime("%m%d%Y_%I%M"))
    # creating Path to move input and load template
    # Default Input Path if no other path in command 
    # line     
    #path2Input = Path(Path.cwd(),options['fileLocation'], options['file2Process']) # change for actuall image location
    path2Input = options['input']
    path2CamCalibration = Path(Path.cwd(), 
        options['fileLocation'], 
        options['file2CamCalibration'])
    path2MarkedAndCalibrated = Path(Path.cwd(), 
        options['fileLocation'], 
        options['file2MarkedASIC'])
    path2MarkedForTransfMatrix = Path(Path.cwd(), 
        options['fileLocation'], 
        options['file2MarkedASICempty'])
    path2OutputData = Path(Path.cwd(), 
        options['outputArea'], 
        timestamp )
    path2EvalAverageDots = Path(Path.cwd(), 
        options['fileLocation'], 
        options['locationEval'], 
        options['filenameAverageDots'])    
    # subfolder in the output of current run for preprocessed images
    path2Preprocessed = Path(Path.cwd(), 
        options['outputArea'], 
        timestamp, 
        options['outputAreaPrePro2']) 
    path2Result = Path(Path.cwd(), 
        options['result'])
    # used for PCA
    path2TrainingData = Path(Path.cwd(), 
        options['fileLocation'], 
        options['locationEval'], 
        options['trainingdata'])
    # used for getting boundarys of good images from projection
    # using PCA
    path2GoodData = Path(Path.cwd(), 
        options['fileLocation'], 
        options['locationEval'], 
        options['goodImg'])    
    # PCA Data saved as JSON file. Filename is hardcoded, location
    # of files is flexible
        
    path2PC = Path(Path.cwd(), 
        options['fileLocation'],
        options['PCAData']) 
#    path2PCmean = Path(Path.cwd(), 
#        options['fileLocation'],
#        options['PCAData'], 
#        'mean.json') # hard coded filename for PCA
    
    # create folder for output: 
    path2OutputData.mkdir(exist_ok = True, parents = True)
    
    # copy input to o utput location
    shutil.copy(str(path2Input), str(path2OutputData)) # copy original file
    
    # bool for new trainingset for Principle Component
    #newTrainingset = True # TODO:  change to nextline!!!! 
    newTrainingset = options['newTrainingset']
    
    ##################################################
    ########### Image Pipeline starts here   #########
    ##################################################
    
    # Preprocessing: undistort and propably sharpening 
    # for input image May be needed: Eval Preprocessing ??
    enhancedImage = FirstPreProc(path2Input, path2CamCalibration, path2OutputData)
    assert type(enhancedImage) == np.ndarray # is valid image format
    assert enhancedImage.size > 0 | len(enhancedImage.shape) == 3 # is valid image, not empty and colorspace
    
    # read in marked ASIC Image / Image must be 
    # undistorted image
    markedASIC = cv2.imread(str(path2MarkedAndCalibrated))
    markedASICempty = cv2.imread(str(path2MarkedForTransfMatrix))
    # check for not emtpy and color image
    assert markedASIC.size > 0 | len(markedASIC.shape) == 3 
    assert markedASICempty.size > 0 | len(markedASICempty.shape) == 3 
    
    
    t = time.time()
    # Image Registration - align preprocessed image 
    # with image used to mark locations of ASIC - use 
    # not markedASIC image - cause Warp will have 
    # difficulties finding transformation matrix
    warpedImg, warpmatrix, corcoef = Warp(markedASICempty, enhancedImage, str(path2OutputData))
    elapsedWarp = time.time() - t
    print('time 2 Warp: '+ str(elapsedWarp))

    t = time.time()    
    # ASIC Seperation - returns a list of images and 
    # a list with position information
    seperatedASICs, sortedPositions = SeperateASICs(warpedImg, markedASIC)
    elapsedSep = time.time() - t    
    print('time 2 Sep: '+ str(elapsedSep))
    if (options['verbose'] == 0):
        WriteOnHDD(seperatedASICs, path2OutputData)
    
    t = time.time()
    # Preprocessing II
    preProcessedASICs = PrePro2(seperatedASICs)
    # save preprocessed in Output folder
    if (options['verbose'] == 0):
        WriteOnHDD(preProcessedASICs, path2Preprocessed)
    elapsedPrePro = time.time() - t
    print('time 2 Preproc: '+ str(elapsedPrePro))
    ##################################################
    ################    Evaluation     ###############
    ##################################################
    t = time.time()
    # set WIDTH and HEIGHT for training images and for 
    # calculation of Principle Components & Similarity
    # measures
    dimensions = (50, 63)
    # if new trainingsset calulate new principle 
    # components, trainingdata, dimension for img and 
    # location to save PCA Data needed
    if newTrainingset: 
        CreateNewPC(path2TrainingData, path2GoodData, dimensions, path2PC) 
    # Evaluate each picture - blob 
    # count, area and shape similarity 
    # Decision Tree  not done yet
    evaluatedPositions = Eval(preProcessedASICs, 
                              seperatedASICs,
                              path2EvalAverageDots, 
                              dimensions, 
                              path2PC)
    if (options['verbose'] == 0):
        with open(options['output'] + '/result.json','w') as data_file:
            json.dump(evaluatedPositions,data_file,indent=4)
    # print colored result pictures
    result = PrintEval(warpedImg, 
                       sortedPositions, 
                       evaluatedPositions, 
                       path2OutputData)       
    elapsedEval = time.time()-t
    print('time 2 Eval: '+ str(elapsedEval))
"""
Command line input for programm for GUI or external
start of image pipeline and evaluation. 
Accepted parameters: 
    * v - verbose TODO!!!
    * h - help
    * i - input
    * o - output
    * ...
"""
def main(argv):
    # File location path - all in subfolders from the 
    # starting

    options = {}
    
    # load options from json file - all default file 
    # locations are within the Eval folder 
    with open('options.json') as data_file:    
        options = json.load(data_file)
    # specify default inputand output folder
    options['input']=Path(Path.cwd(),
                    options['fileLocation'], 
                    options['file2Process'])
    outputdir=options['output']
    # specify what parameters to expect: 
    
    try:
        opts, args = getopt.getopt(argv,"vhi:o:",["ifile=","ofile="])
    except getopt.GetoptError:
        print('python main.py -i <inputfile> -o <outputfile>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
           print('python main.py -i <inputfile> -o <outputfile>')
           sys.exit()
        elif opt in ("-v", "--verbose"):
           options['verbose'] = 0
        elif opt in ("-i", "--ifile"):
           options['input'] = arg
        elif opt in ("-o", "--ofile"):
           outputdir = arg
    print('Input file is "%s"' % options['input'])
    print('Output file is "%s"' % outputdir)
    options['output'] = outputdir
    process( options )

if __name__ == "__main__":
   main(sys.argv[1:])