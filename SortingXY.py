# -*- coding: utf-8 -*-
"""
Created on Thu Oct 13 10:34:49 2016

Sorts a input list, containing x = heigth and 
y = width positions as two seperate lists, by 
sorting lists first by x and than by y values. 
Or the other way around if xy = False. Third 
variant sort by heigth first, but if heigth 
values are to close together, sorty by Y values. 

INPUT:  list of two list containing x and y 
        positions, xy as boolean for sorting order,
        groupByXsortByY as boolean for appliing third
        order with modified merge sort
OUTPUT: sorted list of two list with x, y coordinates 

@author: Ludwig Bartsch, SCIPP - TU Berlin
"""

import math

def SortingXY(listOPositions, xy = True, groupByXsortByY = False):
    if not groupByXsortByY:     
        if xy: 
            # sorting height after width positions -> so [[4,2,4],[c,a,a]] 
            # becomes [[2,4,4][a,a,c]]
            byX, byY = (list(x) for x in zip(*sorted(zip(
                listOPositions[0], listOPositions[1]))))
        else: # sort by y value (for image positions y = width)
            byY, byX = (list(x) for x in zip(*sorted(zip(
                listOPositions[1], listOPositions[0]))))
    else: 
        # Sort first by X then by Y, but if differences between X values small
        # sort it by Y
        byX, byY = msort(listOPositions[0], listOPositions[1])                    
    return [byX,byY]
    


"""
Helper Function for SortingXY. Modified MergeSort to sort two lists. 
First sort list 1, if values in list1 are close together sort it by 
list 2 so (79,450)(83, 251)(100,251) becomes (83,251)(79,450)(100,251). 
How close can be changed by epsilon. 

INPUT: two list of ints, epsilon distance between two points
"""
def msort(xList, yList, epsilon = 20):
    resultX = []
    resultY = []
    if len(xList) < 2:
        return xList, yList
    mid = int(len(xList)/2)
    xLeftList, yLeftList = msort(xList[:mid], yList[:mid]) #y
    xRightList, yRightList = msort(xList[mid:], yList[mid:]) #z
    
    while (len(xLeftList) > 0) or ( len(xRightList) > 0):
        if len(xLeftList) > 0 and len(xRightList) > 0:
            if(math.fabs(xLeftList[0]-xRightList[0])<epsilon):
                if yLeftList[0] > yRightList[0]: 
                    resultX.append(xRightList[0])
                    xRightList.pop(0)
                    resultY.append(yRightList[0])
                    yRightList.pop(0)
                else: 
                    resultX.append(xLeftList[0])
                    xLeftList.pop(0)
                    resultY.append(yLeftList[0])
                    yLeftList.pop(0)
            else: 
                if xLeftList[0] > xRightList[0]: 
                    resultX.append(xRightList[0])
                    xRightList.pop(0)
                    resultY.append(yRightList[0])
                    yRightList.pop(0)
                else: 
                    resultX.append(xLeftList[0])
                    xLeftList.pop(0)
                    resultY.append(yLeftList[0])    
                    yLeftList.pop(0)
        elif len(xRightList) > 0:
            for i in xRightList:
                resultX.append(xRightList.pop(0))
                resultY.append(yRightList.pop(0))
        else:
            for i in xLeftList:
                resultX.append(xLeftList.pop(0))
                resultY.append(yLeftList.pop(0))
    return resultX, resultY