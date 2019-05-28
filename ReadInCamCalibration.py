# -*- coding: utf-8 -*-
"""
Created on Thu Oct 20 11:36:34 2016

Read in the Calibration Data for the camera that 
came out of the calibration script from opencv. 
Data contains, camera matrix and distortion coeff. 

This program, reads txt file with the values and
creates the right format for the data. 

mtx as 3x3 matrix [[1.0 2.0 3.0],
                   [4.0 5.0 6.0],
                   [7.0 8.0 9.0]]

dist as list of floats [[1.0 2.0 3.0 4.0 5.0]]

mtx and dist have to be numpy arrays!!!

INPUT: file location as Path-object from pathlib
OUTPUT: numpy arrays mtx and dist with structure
    mentioned above
    
@author: Ludwig Bartsch - SCIPP / TU Berlin
"""
import numpy as np

def ReadInCamCalibration(path2CalData):
    path = path2CalData    
    f = open(str(path), 'r')
    readInMatrix = False
    readInCoeff = False
    firstLineIsText = False
    coeff = []
    matrix = []    
    # go through all the lines
    for line in f: 
        if '#mtx' in line: 
            # set where to save and dont save first lines cause it is text
            firstLineIsText = True 
            readInMatrix = True
            readInCoeff = False
        if '#dist' in line: 
            firstLineIsText = True
            readInCoeff = True
            readInMatrix = False
        
        if readInCoeff: 
            if firstLineIsText: 
                firstLineIsText = False
            else: 
                if line and not line.isspace():  # only non empty lines
                    coeff.append(line)                
        if readInMatrix: 
            if firstLineIsText: 
                firstLineIsText = False
            else:
                if line and not line.isspace(): # only non empty lines
                    matrix.append(line)  
                   
    # parsing and changing into numpy array        
    if coeff: 
        asFloatCoeff = ParsingValues(coeff)
    else: 
        asFloatCoeff = []
    if matrix: 
        asFloatMatrix = ParsingValues(matrix)
    else: 
        asFloatMatrix = []
        
    return np.array(asFloatMatrix), np.array(asFloatCoeff)
    

def ParsingValues(listOStrings): 
    asList = []    
    for string in listOStrings: 
        clearedFromSpecialChar = string.replace('\n','') 
        if clearedFromSpecialChar or not clearedFromSpecialChar.isspace() : 
            #clearedFromSpecialChar = clearedFromSpecialChar('\t','')
            splitItUp = clearedFromSpecialChar.split(';')
            
            if splitItUp:                
                asFloats = [float(i) for i in splitItUp]
                asList.append(asFloats)
    return asList
        