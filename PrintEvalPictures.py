# -*- coding: utf-8 -*-
"""
Created on Sat Nov 12 22:20:05 2016
Visualize evaluation information in the input image
by coloring the input image to encode the eval information
(good / bad dots per Panel) in the image for easy review. 
Each column in the Eval Array produces an extra output image. 

INPUT: Input Image, List of Positions and Array 
    of Evalresults, Path to Save Result
OUTPUT: b&w copys of Input Image with
    colored locations 
@author: Ludwig Bartsch - SCIPP / TU Berlin
"""
import numpy as np
import cv2
from pathlib import Path
"""
def FindColor(column, mode = "blobs", areaLower = 0.15, areaUpper = 0.35):
    
"""    
"""
    Helper function. Gets a vector with 
    the eval data and trys to find min / max value
    to assing color to the value in the column. 
    Mode changes the coloring. 
    Mode blob: only 5 are green - 4 yellow, rest red
    Mode area: Area within 0.15 and 0.35 green, 0.35-0.4 yellow, rest red
    Mode shapewarp: finding range of values, ...
    Mode shapePCA: finding range of values, within 10% of best, green, within 50% yellow
                    rest red
"""
"""
    color = []
    if mode == "blobs":
        for line in column: 
            if line == 5: 
                color.append("green")
            elif line == 4: 
                color.append("yellow")
            else:
                color.append("red")
    elif mode == "area":
        for line in column: 
            if line >= areaUpper and line <= areaUpper: 
                color.append("green")
            elif line >=areaUpper and line <= areaUpper + 0.1:
                color.append("yellow")
            else: 
                color.append("red")        
    return color
"""
def map2ColorMap(column, inverse = False): 
    """
    Helper Function which maps the values in 
    column to the ColorMap Range(grayscale 0-255)
    invers parameter allows to reverse mapping from
    255-128 instead of 128-255
    """    
    # get params to compute relative values
    # out of the absolutes in column
    minimumInput = min(column)
    maximumInput = max(column)
    print(str(min(column)) + " " + str(max(column)) )
    spanInput = maximumInput - minimumInput
    
    minimumColormap = 125
    #maximumColorMap = 255
    spanOutput = 130
    
    mapped = []
    for line in column: 
        # compute relative values
        relative = float(line - minimumInput) / float(spanInput) 
        # reverse mapping(biggest in column to smallest in mapped)        
        if inverse == True: 
            relative = 1-relative        
        
        mapped.append(relative * spanOutput + minimumColormap)
        
    return mapped

############################################################
"""
    Helper function to take an image and an 
    column vector and first use map2ColorMap()
    to map the eval data onto a colorMap. 
    After that the function iterates over all 
    positions and colors each position according
    to the mapped colors. 
    It copys ASIC area from input image(by info in 
    positions). Blends this with a colored version 
    and writes this image to the original postion 
    in the input image. 
"""
def colorImage(inputImage, positions, columnWithEvalData, reverse = False): 
    
    if inputImage.dtype == 'uint16': 
        inputImage = cv2.convertScaleAbs(inputImage, alpha=(255.0/65535.0))
    
    grayColored = inputImage.copy()
    #grayColored = inputImage
    
    # map the data in columnWithEvalData into grayscale values for the 
    # color map, inverse enables reverse mapping
    mappedEvalValues = map2ColorMap(columnWithEvalData, inverse = reverse)
    # iterate over each position info
    for i, pos in enumerate(positions): 
        dimension = (pos[3], pos[2],3)
        # create image size as size in positions
        coloredImg = np.zeros((dimension), np.uint8)
        coloredImg[:,:,:] = (int(mappedEvalValues[i]), 
                                int(mappedEvalValues[i]), 
                                int(mappedEvalValues[i]) )
        #coloredImg = int(mappedEvalValues[positions.index(pos)])*np.ones(dimension, np.int16)
        #coloredImg = cv2.cvtColor(coloredImg, cv2.COLOR_GRAY2BGR)
        coloredImg = cv2.applyColorMap(coloredImg, cv2.COLORMAP_JET)        
        cutOutASIC = grayColored[pos[1]:pos[1]+pos[3], pos[0]:pos[0]+pos[2],:]
        blended = cv2.addWeighted(cutOutASIC, 0.7, coloredImg, 0.3, 0)
        
        # copy bended image onto input image
        grayColored[pos[1]:pos[1]+pos[3], pos[0]:pos[0]+pos[2]] = blended
    #cv2.imwrite('blended.jpg', grayColored)
    return grayColored

#################################################################

"""
    Helper function to print the value in the evaluatedArray 
    onto the picture at the corresponding location as noted 
    in the positions array. 
"""
def PrintStringOnImage(img, positions, evaluatedArray, rounding = False): 
    font = cv2.FONT_HERSHEY_SIMPLEX
    for index, item in enumerate(evaluatedArray):
        if rounding == True: 
            string = str(round(evaluatedArray[index], 3))    
        else: 
            string = str(evaluatedArray[index])
        cv2.putText(img,string,(positions[index][0],
                                positions[index][1]), 
                                font, 1, (200,255,155), 
                                2, cv2.LINE_AA)

################################################################

"""
    Function to print the values from evaluation as colored
    areas over the ASIC positions in the input image. 
    Color come from jet color map, but goes from green to 
    red only. 
"""
def PrintEvalPictures(img, positions, evaluatedArray, path2Result): 
    # positions array with: cv2.CC_STAT_LEFT , cv2.CC_STAT_TOP, 
    # cv2.CC_STAT_WIDTH, cv2.CC_STAT_HEIGHT, cv2.CC_STAT_AREA
    # information    
    
    # convert 2 grayscale
    grayscale = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # convert b&w 2 color to colorate ASIC pads    
    grayColor = cv2.cvtColor(grayscale, cv2.COLOR_GRAY2BGR)
    
    # extract eval values
    blobs =         [x[2] for x in evaluatedArray[1:]]
    area =          [x[1] for x in evaluatedArray[1:]]
    negPixelNumber = [x[3] for x in evaluatedArray[1:]]
    posPixelNumber = [x[4] for x in evaluatedArray[1:]]
    #shapePCA =      [x[5] for x in evaluatedArray[1:]]
    shapeWarpCC =   [x[5] for x in evaluatedArray[1:]]
    print(shapeWarpCC)
    # color image by colormap according to the values from eval
    outputblobs = colorImage(grayColor, positions, blobs, reverse = True)
    PrintStringOnImage(outputblobs, positions, blobs)
    
    outputarea = colorImage(grayColor, positions, area, reverse = False)
    PrintStringOnImage(outputarea, positions, area, rounding = True)
    
    outputNeg = colorImage(grayColor, positions, negPixelNumber, reverse = False)
    PrintStringOnImage(outputNeg, positions, negPixelNumber)
    
    outputPos = colorImage(grayColor, positions, posPixelNumber, reverse = False)
    PrintStringOnImage(outputPos, positions, posPixelNumber)
    
    #outputPCA = colorImage(grayColor, positions, shapePCA, reverse = True)    
    #PrintStringOnImage(outputPCA, positions, shapePCA)
    
    outputWarpCC = colorImage(grayColor, positions, shapeWarpCC, reverse = True)    
    PrintStringOnImage(outputWarpCC, positions, shapeWarpCC)
    
    cv2.imwrite(str(Path(str(path2Result),'coloredBlobs.jpg')),outputblobs)
    cv2.imwrite(str(Path(str(path2Result),'coloredArea.jpg')),outputarea)    
    cv2.imwrite(str(Path(str(path2Result),'coloredNeg.jpg')), outputNeg)
    cv2.imwrite(str(Path(str(path2Result),'coloredPos.jpg')), outputPos)
    #cv2.imwrite(str(Path(str(path2Result),'coloredPCA.jpg')), outputPCA)
    cv2.imwrite(str(Path(str(path2Result),'coloredWarpCC.jpg')), outputWarpCC)