#------------------------------------------------------------------------------
# Copyright 2018 Esri
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#------------------------------------------------------------------------------
# Name: orientedimagerytools.py
# Description: This is a support script to ManageOrientedImageryTools.pyt. It has commonoly used code that is called from the GPTool.
# Version: 2.3
# Date Created : 20181009
# Date updated : 20200305
# Requirements: ArcGIS Pro 2.2.4
# Author: Esri Imagery Workflows team
#------------------------------------------------------------------------------

import arcpy
import os
import sys
import traceback
import copy
import math
import json
import csv
import subprocess
import concurrent.futures
from datetime import datetime
from dateutil.parser import parse
from dateutil.parser import parserinfo
import multiprocessing
from pathlib import Path
import requests
from arcgis.gis import GIS
from concurrent.futures import ProcessPoolExecutor
if (sys.version_info[0] < 3):
    import ConfigParser
else:
    import configparser as ConfigParser

multiprocessing.set_executable(os.path.join(sys.exec_prefix, 'pythonw.exe'))
gdalPath = os.path.join(os.path.dirname(os.path.dirname(__file__)),'Dependents/OptimizeRasters/GDAL/bin')
gdalPath = os.path.normpath(gdalPath)

propertiesAsList = []

def createFC(featClassFullName,srs,geometryType):

    wrkSpace = os.path.dirname(featClassFullName)
    featClassName = os.path.basename(featClassFullName)
    try:
        srsObj = arcpy.SpatialReference()
        srsObj.loadFromString(srs)

    except:
        arcpy.AddMessage('Could Not create spatial reference object.')
        sys.exit(1)

    ## ======================================================
    ## Create feature class
    ## ======================================================
    arcpy.AddMessage( "Creating feature class " + featClassName + "...")

    template = "#"
    hasM = "DISABLED"
    hasZ = "DISABLED"

    try:
        if arcpy.Exists(featClassFullName):
            arcpy.AddMessage( "Error: output feature class " + featClassName + " already exists.")
            sys.exit(1)
        else:
            arcpy.CreateFeatureclass_management(wrkSpace,featClassName,geometryType,template,hasM,hasZ,srsObj)
    except arcpy.ExecuteError:
        # Get the tool error messages
        #
        msgs = arcpy.GetMessages(2)

        # Return tool error messages for use with a script tool
        #
        arcpy.AddError(msgs)

        # Print tool error messages for use in Python/PythonWin
        #
        print(msgs)
    except:

        arcpy.AddError('Error creating Featureclass')
        sys.exit(1)


def addfields(featClass):
    ## ======================================================
## Add fields
## ======================================================
    arcpy.AddMessage( "Adding fields...")


# Open comma-delimited file containing field definitions
#    fileFieldDef = open(tableDefFilePath, "r")

# Define fields Here..

    fileFieldDef = []


    fileFieldDef.append('N,16.8,X,NULL')
    fileFieldDef.append('N,16.8,Y,NULL')
    fileFieldDef.append('C,100,Name,NULL')
    fileFieldDef.append('C,100,Point,NULL')
    fileFieldDef.append('N,6,SRS,NULL')
    fileFieldDef.append('C,1000,Image,NULL')
    fileFieldDef.append('D,8,AcquisitionDate,NULL')
    fileFieldDef.append('N,16.8,CamHeading,NULL')
    fileFieldDef.append('N,16.8,CamPitch,NULL')
    fileFieldDef.append('N,16.8,CamRoll,NULL')
    fileFieldDef.append('N,16.8,HFOV,NULL')
    fileFieldDef.append('N,16.8,VFOV,NULL')
    fileFieldDef.append('N,16.8,AvgHtAG,NULL')
    fileFieldDef.append('N,16.8,FarDist,NULL')
    fileFieldDef.append('N,16.8,NearDist,NULL')
    fileFieldDef.append('C,2,OIType,NULL')
    fileFieldDef.append('N,16.8,Order_,NULL')
    fileFieldDef.append('C,200,CamOffset,NULL')
    fileFieldDef.append('C,200,Accuracy,NULL')
    fileFieldDef.append('C,50,ImgPyramids,NULL')
    fileFieldDef.append('C,200,DepthImg,NULL')
    fileFieldDef.append('C,200,CamOri,NULL')

# Loop through each line in file and add field to feature class

    for fieldDef in fileFieldDef:
        shouldAddField = 1
        #print "- " + fieldDef

    # Split line into a list using the comma as the delimiter
        fieldDefList = fieldDef.split(",")

    # Extract elements of list into separate variables
    # Element 1: is the field type, possible values are:
    #           X = Ignore, do not add field
    #           C = Character field
    #           N = Numeric field
    #           D = Date field
    # Element 2: is the field length...
    #   - if field type is C, then field length represents the text width
    #   - if field type is N, then if field length value is integer then field
    #       will be defined as integer. If field length value is float then
    #       field will be defined as float as whole number represents the
    #       field precision and the decimal fraction the field scale.
    #
        fieldDefType = fieldDefList[0]
        fieldDefLen = fieldDefList[1]
        field_alias = fieldDefList[2]  # this is the field name alias
        field_name = fieldDefList[2] # this is the field name
        field_reset = fieldDefList[3]

    # Add fields
        if fieldDefType.upper() != "X":
            if shouldAddField == 1:
            # Determine field type, length, precision, scale
                if fieldDefType.upper() == "C":
                    field_type = "TEXT"
                    field_length = fieldDefLen
                    field_precision = "#"
                    field_scale = "#"
                elif fieldDefType.upper() == "D":
                    field_type = "DATE"
                    field_length = "#"
                    field_precision = "#"
                    field_scale = "#"
                elif fieldDefType.upper() == "N":
                #check if it should be
                # field or integer
                    if fieldDefLen.find(".") > 0:
                        field_type = "FLOAT"
                        field_length = "#"
                        field_precision = fieldDefLen.split(".")[0]
                        field_scale = fieldDefLen.split(".")[1]
                    else:
                        field_type = "LONG"
                        field_length = "#"
                        field_precision = fieldDefLen
                        field_scale = "0"

                try:
                    fieldList = arcpy.ListFields(featClass,field_name)
                    if len(fieldList) == 0:
                        arcpy.AddField_management(featClass, field_name, field_type, field_precision, field_scale, field_length, field_alias)
                    else:
                        arcpy.AddMessage( "The field name: " + field_name + " already exist in the Feature class" + featClass)

                # Add default field value
                #if field_reset.upper() <> "NULL":
                #    arcpy.AssignDefaultToField_management(featClass, field_name, field_reset)

                except:
                    errtime = datetime.now()
                    arcpy.AddMessage( "Exception time: " + str(errtime))

                # Get the traceback object

                # Concatenate information together concerning the error into a message string
                    pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
                    msgs = "ArcPy ERRORS:\n" + arcpy.GetMessages() + "\n"

                # Return python error messages for use in script tool or Python Window
                    arcpy.AddError(pymsg)
                    arcpy.AddError(msgs)

                # Print Python error messages for use in Python / Python Window
                    arcpy.AddMessage( pymsg + "\n")
                    arcpy.AddMessage( msgs)
            else:
                arcpy.AddMessage( "\tSkipping field; not valid for this product.")
        else:
            arcpy.AddMessage( "\tSkipping field...")


def importCSVtoFC(csvTablePath, fcPath, defValues, log):
    fields = arcpy.ListFields(fcPath)
    fieldsToImport = [f.name for f in fields]
    fieldsToSearch = []

    #arcpy.AddMessage(fieldsToSearch)

    csvTableFields = arcpy.ListFields(csvTablePath)
    for csvfld in csvTableFields:
        fieldsToSearch.append(csvfld.name)

    if 'SRS' in fieldsToSearch:
        fieldsToSearch.remove('SRS')
        fieldsToSearch.insert(0,'SRS')
    if 'Y' in fieldsToSearch:
        fieldsToSearch.remove('Y')
        fieldsToSearch.insert(0,'Y')
    if 'X' in fieldsToSearch:
        fieldsToSearch.remove('X')
        fieldsToSearch.insert(0,'X')

    csvFields = tuple(fieldsToSearch)
    #arcpy.AddMessage(str(len(csvFields))+':::'+str(csvFields))

    #fieldsToImport.insert(0,"SHAPE@")
    #fieldsToImport.insert(1,'Name')
    #arcpy.AddMessage(str(len(fieldsToImport))+':::'+str(fieldsToImport))

    fcCursor = arcpy.da.InsertCursor(fcPath,fieldsToImport)
    desc = arcpy.Describe(fcPath)
    fcSRS = desc.spatialReference

    #arcpy.AddMessage('csvFields: '+str(csvFields))

    with arcpy.da.SearchCursor(csvTablePath,csvFields) as inCursor:

        for row in inCursor:

            inX = row[0]
            inY = row[1]
            inSRS = row[2]
            inPtSRS = arcpy.SpatialReference()
            inPtSRS.loadFromString(inSRS)

            aPoint = arcpy.Point()
            aPoint.X = inX
            aPoint.Y = inY

            aPtGeometry = arcpy.PointGeometry(aPoint,inPtSRS).projectAs(fcSRS)
            aPoint = aPtGeometry.centroid


            #Create and populate the list.

            aValueList = []
            aValueList = [None] * (len(fieldsToImport))
            aValueList[fieldsToImport.index('Shape')] = aPoint

            for f in range(0,len(csvFields)):
                if csvFields[f] == 'X' or csvFields[f] == 'Y' or csvFields[f] == 'SRS' or csvFields[f] == 'Omega' or csvFields[f] == 'Phi' or csvFields[f] == 'Kappa':
                    pass
                else:
                    aValue = row[f]
                    if aValue == '' or aValue == None:
                        aValue = None

                    aValueList[fieldsToImport.index(csvFields[f])] = aValue



            #Check for Omega Phi Kappa
            # Below parameters are computed based on the priority -> csv, computed from available params, defualt user params.
            OPK = False
            if csvFields.count('Omega') == 1 and csvFields.count('Phi') == 1 and csvFields.count('Kappa') == 1:
                OPK = True
                omegaVal = row[csvFields.index('Omega')] * (math.pi/180)
                phiVal = row[csvFields.index('Phi')] * (math.pi / 180)
                kappaVal = row[csvFields.index('Kappa')] * (math.pi / 180)

            if ('CamHeading' in csvFields and row[csvFields.index('CamHeading')]):
                camHeading = float(row[csvFields.index('CamHeading')])
            else:
                camHeading = None

            if camHeading == "" or camHeading is None:
                if OPK:
                    camHeading = (math.atan2(-1 * (math.sin(phiVal)), (-1 * (-math.sin(omegaVal)*math.cos(phiVal)))) * 180) / math.pi
                elif defValues.get('CamHeading'):
                    camHeading = float(defValues['CamHeading'])
            if camHeading and camHeading < 0:
                camHeading += 360
            aValueList[fieldsToImport.index('CamHeading')] = camHeading

            if ('CamPitch' in csvFields and row[csvFields.index('CamPitch')]):
                camPitch = float(row[csvFields.index('CamPitch')])
            else:
                camPitch = None
            if camPitch == '' or camPitch == None:
                if OPK:
                    camPitch = math.acos(math.cos(omegaVal)*math.cos(phiVal)) * 180 / math.pi
                elif defValues.get('CamPitch'):
                    camPitch = float(defValues['CamPitch'])
            aValueList[fieldsToImport.index('CamPitch')] = camPitch

            if ('CamRoll' in csvFields and row[csvFields.index('CamRoll')]):
                camRoll = float(row[csvFields.index('CamRoll')])
            else:
                camRoll = None
            if camRoll == '' or camRoll == None:
                if OPK:
                    camRoll = (math.atan2((-1 * ((math.sin(omegaVal)*math.sin(kappaVal)) - (math.cos(omegaVal)*math.sin(phiVal)* math.cos(kappaVal)))), (math.sin(omegaVal)*math.cos(kappaVal)) + (math.cos(omegaVal)* math.sin(phiVal)* math.sin(kappaVal))) * 180) / math.pi
                elif defValues.get('CamRoll'):
                    camRoll = float(defValues['CamRoll'])
            aValueList[fieldsToImport.index('CamRoll')] = camRoll

            if ('AvgHtAG' in csvFields and row[csvFields.index('AvgHtAG')]):
                AvgHtAG = float(row[csvFields.index('AvgHtAG')])
            else:
                AvgHtAG = None
            if (AvgHtAG == '' or AvgHtAG == None) and defValues.get('AvgHtAG'):
                AvgHtAG = float(defValues['AvgHtAG'])
            aValueList[fieldsToImport.index('AvgHtAG')] = AvgHtAG

            if ('HFOV' in csvFields and row[csvFields.index('HFOV')]):
                HFOV = float(row[csvFields.index('HFOV')])
            else:
                HFOV = None
            if (HFOV == '' or HFOV == None) and defValues.get('HFOV'):
                HFOV = float(defValues['HFOV'])
            aValueList[fieldsToImport.index('HFOV')] = HFOV

            if ('VFOV' in csvFields and row[csvFields.index('VFOV')]):
                VFOV = float(row[csvFields.index('VFOV')])
            else:
                VFOV = None
            if (VFOV == '' or VFOV == None) and defValues.get('VFOV'):
                VFOV = float(defValues['VFOV'])
            aValueList[fieldsToImport.index('VFOV')] = VFOV

            if ('NearDist' in csvFields and row[csvFields.index('NearDist')]):
                nearDistance = float(row[csvFields.index('NearDist')])
            else:
                nearDistance = None
            if nearDistance == '' or nearDistance == None:
                # if campitch was empty in the csv and no default value was found
                if (camPitch == None or camPitch == ''):
                    if defValues.get('NearDist'):
                        nearDistance = float(defValues['NearDist'])
                else:
                    if (camPitch > 0 and camPitch < 90 and
                        AvgHtAG != '' and AvgHtAG is not None and
                        VFOV != '' and VFOV != None):
                        nearDistance = AvgHtAG * math.tan((camPitch - (VFOV/2)) * math.pi / 180)
                    elif (camPitch == 0 and
                          AvgHtAG != '' and AvgHtAG is not None and
                          VFOV != '' and VFOV != None):
                        nearDistance = -1 * AvgHtAG * math.sin(VFOV * math.pi / 360)
                    else:
                        nearDistance = 2
            aValueList[fieldsToImport.index('NearDist')] = nearDistance
            if ('FarDist' in csvFields and row[csvFields.index('FarDist')]):
                farDistance = float(row[csvFields.index('FarDist')])
            else:
                farDistance = None
            if farDistance == '' or farDistance == None:
                # if campitch was empty in the csv and no default value was found
                if (camPitch == None or camPitch == ''):
                    if defValues.get('FarDist'):
                        farDistance = float(defValues['FarDist'])
                else:
                    if (camPitch > 0 and camPitch < 90 and
                        AvgHtAG != '' and AvgHtAG is not None and
                        VFOV != '' and VFOV != None):
                        farDistance = AvgHtAG * math.tan((camPitch + (VFOV/2))* math.pi / 180)
                        if farDistance < 0:
                            farDistance = abs(farDistance)
                    elif (camPitch == 0 and AvgHtAG != '' and
                          AvgHtAG is not None and VFOV != '' and VFOV != None):
                        farDistance = AvgHtAG * math.sin(VFOV * math.pi / 360)
                        if farDistance < 0:
                            farDistance = abs(farDistance)
                    else:
                        farDistance = 20
            aValueList[fieldsToImport.index('FarDist')] = farDistance


            try:
                img = row[csvFields.index('Name')]
                if not img:
                    raise Exception('Name not found')
                aValueList[fieldsToImport.index('Name')] = img

            except:

                img = row[csvFields.index('Image')]
                if img.startswith('http'):
                    ossep = '/'
                else:
                    ossep = os.sep

                aNameList = img.split(ossep)
                if len(aNameList) >= 2:
                    aCount = len(aNameList)
                    shortName = aNameList[aCount-2]+ossep+aNameList[aCount-1]
                    aName, anExt = os.path.splitext(shortName)
                    aValueList[fieldsToImport.index('Name')] = aName
                else:
                    aValueList[fieldsToImport.index('Name')] = None


            fcCursor.insertRow(aValueList)
            log.Message('Added row for image {}'.format(aValueList[fieldsToImport.index('Image')]), log.const_general_text)

    del inCursor
    del fcCursor
    del row

def addInitialFields(featureClass):
    fieldDefinitions = []
    fieldDefinitions.append({'fieldType': 'TEXT', 'fieldLength': '100', 'fieldName': 'Name'})
    fieldDefinitions.append({'fieldType': 'TEXT', 'fieldLength': '1000', 'fieldName': 'Image'})
    for fieldDef in fieldDefinitions:
        fieldList = arcpy.ListFields(featureClass, fieldDef['fieldName'])
        if not fieldList:
            arcpy.AddField_management(featureClass, fieldDef['fieldName'], fieldDef['fieldType'],
                                      fieldDef.get('fieldPrecision', '#'), fieldDef.get('fieldScale', '#'),
                                      fieldDef.get('fieldLength', '#'), fieldDef['fieldName'])


def returnLastOID(featureClass):
    count = int(arcpy.GetCount_management(featureClass)[0])
    if not count:
        maxObjectID = 0
    else:
        maxObjectID = arcpy.da.SearchCursor(featureClass, "OBJECTID", sql_clause = (None, "ORDER BY OBJECTID DESC")).next()[0]

    return maxObjectID

def addMissingFields(featureClass,fieldsToAdd):
    addedFields = {}
    fieldDefinitions = {}
    fieldDefinitions['Name'] = {'fieldType': 'TEXT', 'fieldLength': '100'}
    fieldDefinitions['Image']= {'fieldType': 'TEXT', 'fieldLength': '1000'}
    fieldDefinitions['AcquisitionDate'] = {'fieldType': 'DATE'}
    fieldDefinitions['CamHeading'] = {'fieldType': 'FLOAT', 'fieldPrecision': '16',  'fieldScale': '8'}
    fieldDefinitions['CamPitch'] = {'fieldType': 'FLOAT', 'fieldPrecision': '16',  'fieldScale': '8'}
    fieldDefinitions['CamRoll'] = {'fieldType': 'FLOAT', 'fieldPrecision': '16',  'fieldScale': '8'}
    fieldDefinitions['HFOV'] = {'fieldType': 'FLOAT', 'fieldPrecision': '16',  'fieldScale': '8',}
    fieldDefinitions['VFOV'] = {'fieldType': 'FLOAT', 'fieldPrecision': '16',  'fieldScale': '8'}
    fieldDefinitions['AvgHtAG'] = {'fieldType': 'FLOAT', 'fieldPrecision': '16',  'fieldScale': '8'}
    fieldDefinitions['FarDist'] = {'fieldType': 'FLOAT', 'fieldPrecision': '16',  'fieldScale': '8'}
    fieldDefinitions['NearDist'] = {'fieldType': 'FLOAT', 'fieldPrecision': '16',  'fieldScale': '8'}
    fieldDefinitions['OIType'] = {'fieldType': 'TEXT', 'fieldLength': '2'}
    fieldDefinitions['SortOrder'] = {'fieldType': 'FLOAT', 'fieldPrecision': '16',  'fieldScale': '8'}
    fieldDefinitions['CamOffset'] = {'fieldType': 'TEXT', 'fieldLength': '200'}
    fieldDefinitions['Accuracy'] = {'fieldType': 'TEXT', 'fieldLength': '200' }
    fieldDefinitions['ImgPyramids'] = {'fieldType': 'TEXT', 'fieldLength': '50' }
    fieldDefinitions['DepthImg'] = {'fieldType': 'TEXT', 'fieldLength': '200'}
    fieldDefinitions['CamOri'] = {'fieldType': 'TEXT', 'fieldLength': '300'}
    fieldDefinitions['ImgRot'] = {'fieldType': 'FLOAT', 'fieldPrecision': '16', 'fieldScale': '8'}

    if len(fieldsToAdd) >= 1:
        if fieldsToAdd[0].lower() == 'all':
            #add all fields
            for fldName in fieldDefinitions:
                fieldDef = fieldDefinitions[fldName]
                fieldList = arcpy.ListFields(featureClass,fldName)
                if not fieldList:
                    arcpy.AddField_management(featureClass, fldName, fieldDef['fieldType'],
                                              fieldDef.get('fieldPrecision', '#'), fieldDef.get('fieldScale', '#'),
                                              fieldDef.get('fieldLength', '#'), fldName)
                    addedFields.update({fldName: fieldDef['fieldType']})
        else:

            for fldName in fieldsToAdd:
                fieldDef = fieldDefinitions[fldName]
                #if arcpy.ListFields(featureClass,fldName) == []:
                fieldList = arcpy.ListFields(featureClass,fldName)
                if not fieldList:
                    arcpy.AddField_management(featureClass, fldName, fieldDef['fieldType'],
                                              fieldDef.get('fieldPrecision', '#'), fieldDef.get('fieldScale', '#'),
                                              fieldDef.get('fieldLength', '#'), fldName)
                    addedFields.update({fldName: fieldDef['fieldType']})

    return addedFields

def deleteEmptyFields(featureClass, lastObjectId, addedFields):
    fieldNames = [fieldName for fieldName in addedFields]
    doNotDeleteFieldNames = []
    if fieldNames:
        searchCursor = arcpy.da.SearchCursor(featureClass, fieldNames, "OBJECTID > {}".format(lastObjectId))
        for row in searchCursor:
            if len(doNotDeleteFieldNames) == len(fieldNames):
                break
            else:
                for i, fieldName in enumerate(fieldNames):
                    if addedFields[fieldName] == 'TEXT' or addedFields[fieldName] == 'DATE':
                        if row[i]:
                            doNotDeleteFieldNames.append(fieldName)
                    elif addedFields[fieldName] == 'FLOAT':
                        if row[i] != None:
                            doNotDeleteFieldNames.append(fieldName)
        deleteFieldNames = [field for field in fieldNames if field not in doNotDeleteFieldNames]
        if deleteFieldNames:
            arcpy.DeleteField_management(featureClass, deleteFieldNames)


def matchFieldNames(srcTable,tableToMatch):
    srcTableFields = arcpy.ListFields(srcTable)
    matchTableFields = arcpy.ListFields(tableToMatch)

    matchTableFldNames = []

    for srcf in srcTableFields:
        srcFldName = srcf.name
        if ('objectid' in srcFldName.lower() or 'shape' in srcFldName.lower()):
            pass
        else:
            if len(arcpy.ListFields(tableToMatch,srcFldName)) == 1:
                matchTableFldNames.append(srcf.name)


    return (matchTableFldNames)


def return_circle(x,y,r):
    pointList = []
    for i in range(1,360):
        #ang = 2*(math.pi)/(i*360)
        ang = math.radians(i)
        xx = x + r * math.cos(ang)
        yy = y + r * math.sin(ang)
        pointList.append([xx, yy])

    return pointList

def mulmatrix(a,b):

    out = []
    out.append(a[0] * b[0] + a[1] * b[3] + a[2] * b[6])
    out.append(a[0] * b[1] + a[1] * b[4] + a[2] * b[7])
    out.append(a[0] * b[2] + a[1] * b[5] + a[2] * b[8])
    out.append(a[3] * b[0] + a[4] * b[3] + a[5] * b[6])
    out.append(a[3] * b[1] + a[4] * b[4] + a[5] * b[7])
    out.append(a[3] * b[2] + a[4] * b[5] + a[5] * b[8])
    out.append(a[6] * b[0] + a[7] * b[3] + a[8] * b[6])
    out.append(a[6] * b[1] + a[7] * b[4] + a[8] * b[7])
    out.append(a[6] * b[2] + a[7] * b[5] + a[8] * b[8])

    return out

def sign(a):
    if a > 0:
        return 1
    elif a < 0:
        return -1
    return 0

def checkSigns(a,b):
    a0 = sign(a)
    b0 = sign(b)
    if a0 != b0:
        return True
    else:
        return False

def calculateRotationMatrix(camHeading, camPitch, camRoll):
    matrix = []
    matrix.append((math.cos(camHeading) * math.cos(camRoll)) - (math.sin(camHeading) * math.cos(camPitch) * math.sin(camRoll)))
    matrix.append(-1 * (math.sin(camHeading) * math.cos(camRoll)) - (math.cos(camHeading) * math.cos(camPitch) * math.sin(camRoll)))
    matrix.append(-1 * (math.sin(camRoll) * math.sin(camPitch)))
    matrix.append((math.cos(camHeading) * math.sin(camRoll)) + (math.sin(camHeading) * math.cos(camPitch) * math.cos(camRoll)))
    matrix.append(-1 * (math.sin(camHeading) * math.sin(camRoll)) + (math.cos(camHeading) * math.cos(camPitch) * math.cos(camRoll)))
    matrix.append(math.cos(camRoll) * math.sin(camPitch))
    matrix.append(-1 * (math.sin(camHeading) * math.sin(camPitch)))
    matrix.append(-1 * (math.cos(camHeading) * math.sin(camPitch)))
    matrix.append(math.cos(camPitch))
    return matrix;

def scaleAndAdd(a, b, scale,factor):
    out = []
    out.append(a[0] + (b[0] * scale))
    out.append(a[1] + (b[1] * scale))
    out.append(a[2] + (b[2] * (scale/factor)))
    return out

def transformMat3(a, m):
    x, y, z = a
    out = []
    out.append(x * m[0] + y * m[3] + z * m[6])
    out.append(x * m[1] + y * m[4] + z * m[7])
    out.append(x * m[2] + y * m[5] + z * m[8])
    return out

def sub(a, b):
    out = []
    out.append(a[0] - b[0])
    out.append(a[1] - b[1])
    out.append(a[2] - b[2])
    return out

def add(a, b):
    out = []
    out.append(a[0] + b[0])
    out.append(a[1] + b[1])
    out.append(a[2] + b[2])
    return out

def scale(a, factor,limit):
    out = []
    out.append(a[0] * factor)
    out.append(a[1] * factor)
    out.append(a[2] * (factor/limit))
    return out

def returnCoveragePoints(inShapeX,inShapeY,camHeading,camPitch,camRoll,hfov,vfov,avgHtAG,farDist,nearDist,OIType,inspRef):


    outSpRef = arcpy.SpatialReference(3857)

    if inspRef.factoryCode == 102100 or inspRef.factoryCode == 3857:
        WMSF = 1 / math.cos((math.pi / 2) - (2 * math.atan(math.exp((-1 * inShapeY) / 6378137))))
        convert2WebMercator = False
    else:
        WMSF = 1
        convert2WebMercator = True

        inPt = arcpy.Point(inShapeX,inShapeY)
        inPtGeometry = arcpy.PointGeometry(inPt,inspRef)

        inMerPoint = inPtGeometry.projectAs(outSpRef)

        inShapeX = inMerPoint.centroid.X
        inShapeY = inMerPoint.centroid.Y

    radians = math.pi / 180

    if (OIType == "B" or OIType == "D" or OIType == "S" or camHeading < 0 or camHeading == 360):

        radius = farDist * WMSF
        pointList = return_circle(inShapeX,inShapeY,radius)

        shpPart = arcpy.Array()
        shpPolyArray = arcpy.Array()

        for pt in pointList:
            shpPart.add(arcpy.Point(pt[0],pt[1]))

        shpPolyArray.add(shpPart)
        polygon = arcpy.Polygon(shpPolyArray,outSpRef)
        if convert2WebMercator:
            polygon = polyShape.projectAs(inspRef)

    else:

        if hfov > 150:
            camPitch = 90
            camRoll = 0
            threshold = 5
        else:
            threshold = 150

        camHeadings = []
        divide = math.ceil(hfov/threshold)
        if divide % 2 == 0:
            for a in range(0, math.floor(divide/2)):
                d = hfov * (2 * a + 1)/(divide*2)
                camHeadings.extend([camHeading - d, camHeading + d])
        else:
            camHeadings.append(camHeading)
            for a in range(1, math.floor(divide/2)):
                d = a*hfov/divide;
                camHeadings.extend([camHeading - d, camHeading + d])
        camHeadings.sort()
        nearDist = 0 if (nearDist < 0 or not nearDist)  else nearDist * WMSF
        if (camPitch + vfov / 2 >= 90):
            farDist = (farDist or 20) * WMSF
        else:
            if farDist:
                farDist = farDist * WMSF;
            else:
                farDist = avgHtAG * WMSF / math.cos(camPitch * radians)
        shpPolyArray = arcpy.Array()
        for g in range(0, len(camHeadings)):
            matrix = calculateRotationMatrix(camHeadings[g] * radians, camPitch * radians, camRoll * radians)
            gc = []
            gp=[]
            viewingVector = [0,0,-1]
            viewingVector = transformMat3(viewingVector, matrix)
            cfar = scaleAndAdd([inShapeX, inShapeY, avgHtAG], viewingVector, farDist, WMSF)
            Hfar = 2 * math.tan(vfov * radians / 2) * farDist
            Wfar = 2 * math.tan((hfov/divide) * radians / 2) * farDist
            upVector = [0, 1, 0]
            upVector = transformMat3(upVector, matrix)
            rightVector = [1, 0, 0]
            rightVector = transformMat3(rightVector, matrix)
            gc.append(add(cfar, sub(scale(upVector, Hfar / 2, WMSF), scale(rightVector, Wfar / 2, WMSF))))
            gc.append(add(cfar, add(scale(upVector, Hfar / 2, WMSF), scale(rightVector, Wfar / 2, WMSF))))
            gc.append(sub(cfar, sub(scale(upVector, Hfar / 2, WMSF), scale(rightVector, Wfar / 2, WMSF))))
            gc.append(sub(cfar, add(scale(upVector, Hfar / 2, WMSF), scale(rightVector, Wfar / 2, WMSF))))
            for b in gc:
                dist = math.sqrt(math.pow(b[2] - avgHtAG,2) + math.pow(math.sqrt(math.pow(b[0] - inShapeX,2) + math.pow(b[1] - inShapeY,2))/WMSF,2)) * WMSF
                dv = scale(sub([b[0],b[1],b[2]], [inShapeX, inShapeY, avgHtAG]), 1 /dist, 1 / WMSF)
                factor = avgHtAG/(avgHtAG - b[2])
                tempgc = {
                             'x':(1-factor) * inShapeX + factor * b[0],
                             'y': (1-factor) * inShapeY + factor * b[1],
                             'z':(1-factor) * avgHtAG + factor * b[2]
                         }
                tempDist = math.sqrt(math.pow(tempgc['z'] - avgHtAG,2) + math.pow(math.sqrt(math.pow(tempgc['x'] - inShapeX,2) + math.pow(tempgc['y'] - inShapeY,2))/WMSF,2)) * WMSF
                tempDV = scale(sub([tempgc['x'],tempgc['y'],tempgc['z']], [inShapeX, inShapeY, avgHtAG]), 1/tempDist, 1/WMSF)
                if checkSigns(dv[0],tempDV[0]) and checkSigns(dv[1],tempDV[1]) and checkSigns(dv[2],tempDV[2]):
                    gp.append({'x': b[0],'y':b[1],'z':0})
                else:
                    if b[2] >= 0:
                        gp.append({'x': b[0],'y':b[1],'z':0})
                    else:
                        gp.append(tempgc)
            shpPart = arcpy.Array()
            shpPart.add(arcpy.Point(gp[0]['x'], gp[0]['y'], 0))
            shpPart.add(arcpy.Point(gp[1]['x'], gp[1]['y'], 0))
            shpPart.add(arcpy.Point(gp[2]['x'], gp[2]['y'], 0))
            shpPart.add(arcpy.Point(gp[3]['x'], gp[3]['y'], 0))
            shpPart.add(arcpy.Point(gp[0]['x'], gp[0]['y'], 0))
            shpPolyArray.add(shpPart)

        polygon = arcpy.Polygon(shpPolyArray, outSpRef)

        if convert2WebMercator:
            polygon = polygon.projectAs(inspRef)

    return polygon


def get_exif_data(image):
    """Returns a dictionary from the exif data of an PIL Image item. Also converts the GPS Tags"""
    exif_data = {}
    try:
        info = image._getexif()
        if info:
            for tag, value in info.items():
                decoded = TAGS.get(tag, tag)
                if decoded == "GPSInfo":
                    gps_data = {}
                    for t in value:
                        sub_decoded = GPSTAGS.get(t, t)
                        gps_data[sub_decoded] = value[t]

                    exif_data[decoded] = gps_data
                else:
                    exif_data[decoded] = value

        return exif_data
    except:
        e = sys.exc_info()[1]
        arcpy.AddError(e.args[0])

def _get_if_exist(data, key):
    if key in data:
        return data[key]
    else:
        return None

def _convert_to_degress(aValue):
    """Helper function to convert the GPS coordinates stored in the EXIF to degress in float format"""
    value = aValue.split()

    DEC = (float(value[0]) + (float(value[1]) * 1/60) + (float(value[2]) * 1/60 * 1/60))

    return DEC

def returnDate(dateTimeStr):
    try:
        if ' ' in dateTimeStr:
            dateTimeSplit = dateTimeStr.split(' ')
            modifiedDate = dateTimeSplit[0].replace(':','-')
            newSplit = dateTimeStr.split(' ')[1:]
            newSplit.insert(0, modifiedDate)
            dateTimeStr = ' '.join(newSplit)
        elif 'T' in dateTimeStr:
            dateTimeSplit = dateTimeStr.split('T')
            modifiedDate = dateTimeSplit[0].replace(':','-')
            newSplit = dateTimeStr.split('T')[1:]
            newSplit.insert(0, modifiedDate)
            dateTimeStr = 'T'.join(newSplit)
        parserInfo = parserinfo(dayfirst=False, yearfirst=True)
        dateObj = parse(dateTimeStr, parserInfo, ignoretz=True)
    except Exception as e:
        arcpy.AddWarning("{} is not in the required format.".format(dateTimeStr))
        return None
    return dateObj

def get_lat_lon(exif_data):
    """Returns the latitude and longitude, if available, from the provided exif_data (obtained through get_exif_data above)"""
    #print (exif_data)
    lat = None
    lon = None


    gps_latitude = _get_if_exist(exif_data, "EXIF_GPSLatitude")
    gps_latitude_ref = _get_if_exist(exif_data, 'EXIF_GPSLatitudeRef')
    gps_longitude = _get_if_exist(exif_data, 'EXIF_GPSLongitude')
    gps_longitude_ref = _get_if_exist(exif_data, 'EXIF_GPSLongitudeRef')

    #arcpy.AddMessage(gps_latitude_ref+':'+str(gps_latitude)+'-'+gps_longitude_ref+':'+str(gps_longitude))

    if gps_latitude and gps_latitude_ref and gps_longitude and gps_longitude_ref:
        lat = _convert_to_degress(gps_latitude)
        if gps_latitude_ref != "N":
            lat = 0 - lat

        lon = _convert_to_degress(gps_longitude)
        if gps_longitude_ref != "E":
            lon = 0 - lon
    #arcpy.AddMessage('lat:'+str(lat)+'-'+'lon:'+str(lon))

    return lat, lon

def getDefaultValuesFromSource(exif_data):
    # returns a dictionary of default parameters calculated from the image source
    sourceDefaultDict = {}
    camHeading = _get_if_exist(exif_data, 'EXIF_GPSImgDirection')
    if camHeading is None:
        camHeading = _get_if_exist(exif_data, 'drone-dji:GimbalYawDegree')
        if camHeading is None:
            camHeading = _get_if_exist(exif_data, 'CamHeading')

    camHeading = toFloat(camHeading)

    if camHeading == None:
        camHeading = -1
    else:

        if camHeading <= 0:
            camHeading = camHeading + 360

    sourceDefaultDict['CamHeading'] = camHeading

    camPitch = _get_if_exist(exif_data, 'drone-dji:GimbalPitchDegree')

    if camPitch is not None:
        camPitch = 90 + float(camPitch)
    else:
        camPitch = _get_if_exist(exif_data, 'CamPitch')

    camPitch = toFloat(camPitch)
    sourceDefaultDict['CamPitch'] = camPitch

    camRoll = _get_if_exist(exif_data, 'drone-dji:GimbalRollDegree')
    if camRoll is None:
        camRoll = _get_if_exist(exif_data, 'CamRoll')

    camRoll = toFloat(camRoll)
    sourceDefaultDict['CamRoll'] = camRoll

    focalLength35mm = _get_if_exist(exif_data, 'EXIF_FocalLengthIn35mmFilm')
    if  focalLength35mm != None and focalLength35mm != '0':

        focalLength35mm = focalLength35mm.replace('mm','')
        focalLength35mm = float(focalLength35mm)


        HFOV = 2 * math.atan(18/focalLength35mm)
        HFOV = math.degrees(HFOV)
        HFOV = toFloat(HFOV)
        sourceDefaultDict['HFOV'] = HFOV

        VFOV = 2 * math.atan(12/focalLength35mm)
        VFOV = math.degrees(VFOV)
        VFOV = toFloat(VFOV)
        sourceDefaultDict['VFOV'] = VFOV
    else:
        projType = _get_if_exist(exif_data, 'ProjectionType')
        if projType == 'equirectangular':
            HFOV = 360
            sourceDefaultDict['HFOV'] = HFOV
            VFOV = 90
            sourceDefaultDict['VFOV'] = VFOV
        else:
            HFOV = None
            sourceDefaultDict['HFOV'] = HFOV

            VFOV = None
            sourceDefaultDict['VFOV'] = VFOV

    avgHtAG = _get_if_exist(exif_data, 'drone-dji:RelativeAltitude')

    if avgHtAG is None:
        avgHtAG = None
    else:
        avgHtAG = toFloat(avgHtAG)

    sourceDefaultDict['AvgHtAG'] = avgHtAG
    if avgHtAG != None and camPitch != None and VFOV != None:
        if (camPitch - (VFOV/2)) >85:
            farDist= 10*avgHtAG
        else:
            farDist = avgHtAG * math.tan(( camPitch + (VFOV/2))*math.pi/180)
    else:
        farDist = None

    sourceDefaultDict['FarDist'] = farDist
    if avgHtAG != None and camPitch != None and VFOV != None:
        nearDist = avgHtAG * math.tan(( camPitch - (VFOV/2))* math.pi/180)
    else:
        nearDist = None
    sourceDefaultDict['NearDist'] = nearDist
    return sourceDefaultDict

def getTableDefaults(sourceDefaults, userDefaults):
    # Retuns the default parameters to be filled in the table. Computed from the defualt parameter values entered by the user and the corresponding values from the source.
    tableDefaults = {}
    for userDefault in userDefaults:
        if userDefault['isDefault']:
            tableDefaults[userDefault['name']] = None
        else:
            if userDefault['value']:
                tableDefaults[userDefault['name']] = userDefault['value']
            else:
                tableDefaults[userDefault['name']] = sourceDefaults.get(userDefault['name'])
    return tableDefaults

def getOICDefaults(userDefaults):
    # Returns the default parameters to be persisted in the oic file, based on the user input.
    oicDefaults = {}
    for userDefault in userDefaults:
        if userDefault['isDefault']:
            oicDefaults[userDefault['name']] = userDefault['value']
    return oicDefaults

def importExifDataFromImages(inputTable, imgList, outsrs, valueDefaults, log):
    nameFldChk = arcpy.ListFields(inputTable,'Name')
    if len(nameFldChk) == 1:
        #importFields = ['SHAPE@','Name','Point','Image','AcquisitionDate','CamHeading','CamPitch','CamRoll','HFOV','VFOV','AvgHtAG','FarDist','NearDist','OIType','Order_','CamOffset','Accuracy','ImgPyramids','DepthImg','CamOri']
        importFields = ['SHAPE@','Name','Image','AcquisitionDate','CamHeading','CamPitch','CamRoll','HFOV','VFOV','AvgHtAG','FarDist','NearDist','OIType','SortOrder','CamOffset','Accuracy','ImgPyramids','DepthImg','CamOri','ImgRot']
    else:
        #importFields = ['SHAPE@','Point','Image','AcquisitionDate','CamHeading','CamPitch','CamRoll','HFOV','VFOV','AvgHtAG','FarDist','NearDist','OIType','Order_','CamOffset','Accuracy','ImgPyramids','DepthImg','CamOri']
        importFields = ['SHAPE@','Image','AcquisitionDate','CamHeading','CamPitch','CamRoll','HFOV','VFOV','AvgHtAG','FarDist','NearDist','OIType','SortOrder','CamOffset','Accuracy','ImgPyramids','DepthImg','CamOri','ImgRot']

    fcCursor = arcpy.da.InsertCursor(inputTable,importFields)
    imgList = [img for img in imgList if img]
    imgCount = len(imgList)
    cntrCut = round((imgCount * 10) / 100)
    cntr = -1
    imgCntr = 0
    #Multi processing
    with concurrent.futures.ProcessPoolExecutor() as executor:
        for img, imgDict in zip(imgList, executor.map(getImageInfo, imgList)):
                exif_data = imgDict['exif_data']
                errMsg = imgDict['error']
                cntr = cntr + 1
                imgCntr = imgCntr + 1

                if exif_data == {}:
                    if errMsg:
                        arcpy.AddWarning(errMsg)
                        log.Message(str(errMsg), log.const_warning_text)
                    else:
                        arcpy.AddWarning("Incomplete EXIF data. Could not add image: "+os.path.basename(img))
                        log.Message("Incomplete EXIF data. Could not add image: {}".format(os.path.basename(img)), log.const_warning_text)
                else:
                    yCoord, xCoord = get_lat_lon(exif_data)
                    if yCoord == xCoord == None:
                        arcpy.AddWarning("Could not extract coordinate info to add image: "+os.path.basename(img))
                        log.Message("Could not extract coordinate info to add image: {}".format(os.path.basename(img)), log.const_warning_text)
                        continue
                    else:

                        if cntr == cntrCut:
                            arcpy.AddMessage('Extracted Data for '+str(imgCntr)+' of '+str(imgCount))
                            log.Message("Extracted Data for {} of {}".format(str(imgCntr), str(imgCount)), log.const_general_text)
                            cntr = 0

                        aValueList = []

                        aPoint = arcpy.Point()
                        aPoint.X = xCoord
                        aPoint.Y = yCoord

                        inSRS = arcpy.SpatialReference(4326)
                        #inSRS.factoryCode = 4326

                        aPtGeometry = arcpy.PointGeometry(aPoint,inSRS).projectAs(outsrs)
                        aPoint = aPtGeometry.centroid

                        aValueList.append(aPoint)

                        if len(nameFldChk) == 1:
                            if img.startswith('http'):
                                ossep = '/'
                            else:
                                ossep = os.sep

                            aNameList = img.split(ossep)
                            if len(aNameList) >= 2:
                                aCount = len(aNameList)
                                shortName = aNameList[aCount-2]+ossep+aNameList[aCount-1]
                                aName, anExt = os.path.splitext(shortName)
                                aValueList.append(aName)
                            else:
                                aValueList.append(None)

                        #aValueList.append(str(xCoord)+','+str(yCoord))

                        aValueList.append(img)

                        aDateTime = _get_if_exist(exif_data, 'EXIF_DateTime')
                        if aDateTime is not None:
                            aDateTime = returnDate(aDateTime)
                        else:
                            aDateTime = _get_if_exist(exif_data, 'EXIF_DateTimeOriginal')
                            if aDateTime is not None:
                                aDateTime = returnDate(aDateTime)

                        aValueList.append(aDateTime)
                        # below method returns a dictionary of default parameters calculated from the image source
                        sourceDefaults = getDefaultValuesFromSource(exif_data)
                        OIType = valueDefaults['OIType'][0]
                        aValueList.extend([sourceDefaults['CamHeading'], sourceDefaults['CamPitch'],
                                           sourceDefaults['CamRoll'], sourceDefaults['HFOV'],
                                           sourceDefaults['VFOV'], sourceDefaults['AvgHtAG'],
                                           sourceDefaults['FarDist'], sourceDefaults['NearDist'],
                                           OIType])
                        order = 0
                        aValueList.append(order)
                        camOffset = None
                        aValueList.append(camOffset)
                        accuracy = None
                        aValueList.append(accuracy)
                        imgPyramids = None
                        aValueList.append(imgPyramids)
                        depthImg = None
                        aValueList.append(depthImg)
                        aValueList.append(None)
                        imgRot = _get_if_exist(exif_data, 'EXIF_Orientation')
                        if imgRot is not None:
                            try:
                                imgRot = int(imgRot)
                                if imgRot == 1:
                                    imgRot = 0
                                elif imgRot == 3:
                                    imgRot = 180
                                elif imgRot == 6:
                                    imgRot = 90
                                elif imgRot == 8:
                                    imgRot = 270
                                else:
                                    imgRot = None
                            except:
                                imgRot = None
                        else:
                            imgRot = None
                        aValueList.append(imgRot)

                        fcCursor.insertRow(aValueList)
                        log.Message('Inserted row for: {}'.format(img), log.const_general_text)

    del fcCursor


def returnImageExifData(imageFN):
    ret = {}
    i = Image.open(imageFN)
    info = i._getexif()
    for tag, value in info.items():
        decoded = TAGS.get(tag, tag)
        ret[decoded] = value
    return ret


def returnImageList(inputFolder,extens):


    fileList = []

    # Walk the tree
    for dirpath, dirnames, files in os.walk(inputFolder):

        # Loop through the file names for the current step
        for name in files:
            for ext in extens:
                if ext.lower() in name.lower():
                    if name.lower().endswith(ext.lower()):
                        fileList.append(os.path.join(dirpath, name))

    return fileList

def returnImageList_TextFile(txtFile):
    aFile = open(txtFile,'r')
    imagelist = []
    with aFile as f:
        for line in f:
            imagelist.append(line.strip('\n'))

    aFile.close()
    return imagelist

def exifToDictionary(imageInfo):
    stringList = imageInfo.splitlines()

    aDict = {}
    try:
        for aStr in stringList:
            if ('=' in aStr):
                keyvaluepair = aStr.split('=')
                akey = keyvaluepair[0].lstrip().rstrip()
                aValue = keyvaluepair[1].replace('(','')
                aValue = aValue.replace(')','')
                aValue = aValue.replace('"','')
                aDict[akey] = aValue
                #arcpy.AddMessage(aKey+' '+str(aValue))

        return aDict
    except:
        return aDict

def getImageInfo(imgName):
    gdalInfoEXE = os.path.join(gdalPath,'gdalinfo.exe')
    imgDict = {}

    if imgName.startswith('http'):
        imgName = '/vsicurl/'+imgName
    else:
        imgName = imgName.strip("'")
    if ' ' in imgName:
        imgName = "\"" + imgName + "\""
    allArgs = []
    allArgs.append(gdalInfoEXE)
    allArgs.append('-mdd all')
    allArgs.append(imgName)
    with open('C:/Users/Alex/Desktop/testtest.txt', 'r+') as tt:
        tt.write(str(allArgs))
    try:
        thePipe = subprocess.Popen(' '.join(allArgs),shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE) #,encoding='utf-8')
        retMsg = '/'
        fullMessage = ''

        retMsg = thePipe.stdout.read()
        errMsg = thePipe.stderr.read()
        retMsgAsList = retMsg.splitlines()
        for msg in retMsgAsList:

            msg = msg.strip()
            if msg != '':
                try:
                    msg = msg.decode("utf-8")
                    fullMessage = fullMessage+msg+'\n'
                except:
                    continue

        imageInfo = exifToDictionary(fullMessage)
        if 'equirectangular' in fullMessage:
            imageInfo['ProjectionType'] = 'equirectangular'

        if 'ns.sensefly.com' in fullMessage:

            xmpString = readXMPString(fullMessage,'ns.sensefly.com',"Camera:Yaw")
            if xmpString != '':
                imageInfo['CamHeading'] = float((xmpString.split('=')[1]).strip().replace('"', ''))

            xmpString = readXMPString(fullMessage,'ns.sensefly.com',"Camera:Pitch")
            if xmpString != '':
                imageInfo['CamPitch'] = float((xmpString.split('=')[1]).strip().replace('"', ''))

            xmpString = readXMPString(fullMessage,'ns.sensefly.com',"Camera:Roll")
            if xmpString != '':
                imageInfo['CamRoll'] = float((xmpString.split('=')[1]).strip().replace('"', ''))

        subprocess.Popen.kill(thePipe)
        imgDict['exif_data'] = imageInfo
        imgDict['error'] = errMsg
        return imgDict

    except Exception as e:
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]

        pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
        msgs = "ArcPy ERRORS:\n" + arcpy.GetMessages() + "\n"

    # Return python error messages for use in script tool or Python Window
        arcpy.AddError(pymsg)
        arcpy.AddError(msgs)

        return {'exif_data':{}, 'error':str(e)}


def returnFieldNames(typeName):
    typesFolder = os.path.join(os.path.dirname(os.path.dirname(__file__)),'Types')
    typesFN = os.path.join(typesFolder,typeName+'.oictype')
    typesFile = open(typesFN,'r')

    typesData = json.load(typesFile)
    #for keys in

def readXMPString(mainString,chkkstring,searchString):
    if chkkstring in mainString:
        chkStrIndex = mainString.find(searchString)
        mainstrlen = len(mainString)
        returnVal = ''

        while (True):
            if chkStrIndex >= mainstrlen:
                break
            else:
                nextChar = mainString[chkStrIndex]
                returnVal = returnVal+nextChar
                if nextChar == ' ':
                    break
                chkStrIndex = chkStrIndex + 1


        return returnVal


def toFloat(chkNum):
    if type(chkNum) == str:
        chkNum = chkNum.strip('(').strip(')')
    try:
        chkNum = float(chkNum)
        return chkNum
    except:
        return chkNum

def loadOIC(oicpath, log, currentProject=None):
    if not currentProject:
        currentProject = arcpy.mp.ArcGISProject('CURRENT')
    activeMap = currentProject.activeMap
    groupLyrTemplate = os.path.join(os.path.dirname(os.path.realpath(__file__)),'OrientedImageryGroup.lyrx')

    with open(oicpath) as oicTFile:
        oicDict = json.load(oicTFile)

    oicPointFC = oicDict["properties"]["PointsSource"]

    if oicPointFC.startswith('\\'):
        pass
    elif ':' in oicPointFC:
        pass
    elif '.gdb' in oicPointFC.split('\\')[0]:
        oicPointFC = os.path.join(os.path.dirname(oicpath),oicPointFC)

    oicCovFC = oicDict["properties"]["CoverageSource"]
    if oicCovFC.startswith('\\'):
        pass
    elif ':' in oicCovFC:
        pass
    elif '.gdb' in oicCovFC.split('\\')[0]:
        oicCovFC = os.path.join(os.path.dirname(oicpath),oicCovFC)

    oicCatName = oicDict["properties"]["Name"]

    aGrpLayer = arcpy.mp.LayerFile(groupLyrTemplate)
    activeMap.addLayer(aGrpLayer,'TOP')

    oiGroupLayer = activeMap.listLayers('*')[0]

    oicPointLyr = activeMap.addDataFromPath (oicPointFC)
    oicPointLyr.name = "Exposure Points"
    oicCovLyr = activeMap.addDataFromPath (oicCovFC)
    oicCovLyr.name =  'Coverage Map'

    updatePointLayerSymbology(oicPointLyr)
    arcpy.AddMessage("Updated Symbology")

    updateCoverageLayerSymbology(oicCovLyr)
    log.Message("Updated Symbology", log.const_general_text)

    log.Message("Adding layers to the group.", log.const_general_text)
    activeMap.addLayerToGroup(oiGroupLayer,oicPointLyr, 'AUTO_ARRANGE')
    activeMap.addLayerToGroup(oiGroupLayer,oicCovLyr, 'AUTO_ARRANGE')

    activeMap.removeLayer(oicPointLyr)
    activeMap.removeLayer(oicCovLyr)

    oiGroupLayer.name = oicCatName


def updatePointLayerSymbology(oicPointLyr):
    ptsym = oicPointLyr.symbology
    cirSymList = ptsym.renderer.symbol.listSymbolsFromGallery('Circle')
    for cSym in cirSymList:
        if '1' in cSym.name:
            ptsym.renderer.symbol = cSym

    ptsym.renderer.symbol.color = {'RGB' : [76, 230, 0, 100]}
    ptsym.renderer.symbol.size = 10
    oicPointLyr.symbology = ptsym

def updateCoverageLayerSymbology(oicCovLyr):
    sym = oicCovLyr.symbology
    sym.renderer.symbol.color = {'RGB' : [76, 230, 0, 50]}
    sym.renderer.symbol.outlineColor = {'RGB' : [76, 230, 0, 50]}
    oicCovLyr.symbology = sym

def isActiveMap():
    aprx = arcpy.mp.ArcGISProject("CURRENT")
    activeMap  = aprx.activeMap
    if activeMap is None:
        return False
    else:
        if activeMap.mapType != 'MAP':
            return False
        else:
            return True

def createOIC(outSrs, outGDB, outOICBaseName, params, log):
    with open('C:/Users/Alex/Desktop/testtest.txt', 'r+') as tt:
        tt.write('{}, {}, {}, {}, {}'.format(outSrs, outGDB, outOICBaseName, params, log))
    outGDBFolderLocation = os.path.dirname(outGDB)
    outGDBFolderName = os.path.dirname(outGDB)
    oicPointFC = str(Path(outGDB) / '{}_ExposurePoints'.format(outOICBaseName))

    oicCovFC = str(Path(outGDB) / '{}_CoverageMap'.format(outOICBaseName))

    ptTemplate = os.path.join(os.path.dirname(os.path.realpath(__file__)),'ExposurePoints.lpkx')
    polyTemplate = os.path.join(os.path.dirname(os.path.realpath(__file__)),'CoverageMap.lpkx')

    log.Message('Creating point and polygon feature classes..', log.const_general_text)
    arcpy.AddMessage('Creating point and polygon feature classes..')

    arcpy.CreateFeatureclass_management(outGDB,outOICBaseName+'_ExposurePoints',"POINT",'#',"DISABLED","DISABLED",outSrs)
    addInitialFields(os.path.join(outGDB, '{}_ExposurePoints'.format(outOICBaseName)))
    arcpy.CreateFeatureclass_management(outGDB,outOICBaseName+'_CoverageMap',"POLYGON",polyTemplate,"DISABLED","DISABLED",outSrs)

    oicTemplateFile = os.path.join(os.path.dirname(os.path.realpath(__file__)),'OIC_Template.json')
    grpJsonFile = os.path.join(outGDBFolderLocation,outOICBaseName+'.OIC')

    with open(oicTemplateFile) as oicTFile:
        oicDict = json.load(oicTFile)

    oicDict["properties"]["Name"] =  outOICBaseName
    oicDict["properties"]["PointsSource"] = oicPointFC
    oicDict["properties"]["CoverageSource"] = oicCovFC
    oicDict["properties"]["Description"] = params['description'].valueAsText
    oicDict["properties"]["Tags"] = params['tags'].valueAsText
    oicDict["properties"]["Copyright"]["text"] = params['copyright'].valueAsText or ""

    with open(grpJsonFile, 'w') as outfile:
        json.dump(oicDict, outfile)

    try:
        currProj = arcpy.mp.ArcGISProject("CURRENT")
        loadOIC(grpJsonFile, log)
    except:
        pass


def returnParametersAsJson(parValues):
    parValuesj = {}
    if parValues:
        for keyValueList in parValues:
            aKey = keyValueList[0]
            aVal = keyValueList[1]
            parValuesj[aKey] = aVal
    return parValuesj

def returnTypes():
    oicTypeLoc = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))),'Types')
    oicTypes = []
    for root, dirs, files in os.walk(oicTypeLoc):
        for file in files:
            if file.endswith('.py'):
                oicTypes.append(file)
                #print file

    onlyTypes = []
    for pyfiles in oicTypes:
        pyoicType = pyfiles.replace('.py','.oictype')
        if os.path.isfile(os.path.join(oicTypeLoc,pyoicType)):
            onlyTypes.append(pyfiles.replace('.py',''))

    return onlyTypes

def returnParameters(oictype):

    oicTypeFN = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))),'Types\\'+oictype+'.oictype')
    with open(oicTypeFN) as oicTypeFile:
        oicTypeJson = json.load(oicTypeFile)
    oicInput = oicTypeJson.get('Input')
    oicParameters = oicTypeJson.get('Parameters')
    paramList = []
    if oicParameters:
        for key in oicParameters:
            paramList.append([key, oicParameters[key]])

    return ([oicInput, paramList])

def getImageryTypesFromInputType(inputType):
    try:
        oicTypeFilePath = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))),'Types', inputType+'.oictype')
        with open(oicTypeFilePath) as oicTypeFile:
            oicTypeJSON = json.load(oicTypeFile)
        defaultAttributes = oicTypeJSON.get('DefaultAttributes') or {}
        defaultAttributes = {'{}_{}'.format(inputType, key): val for key,val in defaultAttributes.items()}
        return defaultAttributes
    except Exception as e:
        return {}

def getImageryTypeFromOIC(oicFilePath):
    try:
        with open(oicFilePath) as oicFile:
            oicJSON = json.load(oicFile)
        defaultAttributes = oicJSON['properties']['DefaultAttributes']
        defaultAttributes = {
                                "LoadedFromOIC": {
                                                     "CamHeading": defaultAttributes["CamHeading"],
                                                     "CamPitch": defaultAttributes["CamPitch"],
                                                     "CamRoll": defaultAttributes["CamRoll"],
                                                     "HFOV": defaultAttributes["HFOV"],
                                                     "VFOV": defaultAttributes["VFOV"],
                                                     "AvgHtAG": defaultAttributes["AvgHtAG"],
                                                     "FarDist": defaultAttributes["FarDist"],
                                                     "NearDist": defaultAttributes["NearDist"],
                                                     "OIType": defaultAttributes["OIType"],
                                                     "MaxDist": oicJSON['properties']["MaxDistance"],
                                                     "ImgRot": defaultAttributes.get('ImgRot')
                                                 }
                            }
        return defaultAttributes
    except Exception as e:
        return {}

def getOICInput(params):
    #get the input parameters(file, folder, filter) based on enabled parameters.
    inputParams = {
                      "file": "",
                      "folder": "",
                      "filter": ""
                  }
    if params['inputFile'].enabled:
        inputParams["file"] = params['inputFile'].valueAsText
    if params["inputFolder"].enabled:
        inputParams["folder"] = params["inputFolder"].valueAsText
    if params["fileFilter"].enabled:
        inputParams["filter"] = params["fileFilter"].valueAsText
    return inputParams

def getDefaultValues(parameters):
    # get default parameters with name, value and "default" checkbox value
    defaultValues = {}
    for index, defaultParam in enumerate(parameters):
        #if defaultParam.category == 'Default Parameters':
        if index >= 8:
                defaultValues.update({defaultParam.name: defaultParam.valueAsText})
    return defaultValues

def getOICFilePath(params):
    #get the oic file path from the selected group layer
    grpLayer = params['inputOIC'].value
    if not grpLayer:
        return None
    grpLayers = grpLayer.listLayers()
    for gLyr in grpLayers:
        gLyrDec = arcpy.Describe(gLyr)
        if gLyrDec.shapeType == 'Point':
            outPath = gLyrDec.catalogPath
            break
    oicFilePath = os.path.join(os.path.dirname(os.path.dirname(outPath)),grpLayer.name+'.OIC')
    return oicFilePath

def updateDEM(oicPath, demURL, renderingRuleEnabled, renderingRule):
    ps = ''
    with open(oicPath) as oicFile:
        oicDict = json.load(oicFile)
    if not renderingRuleEnabled:
        oicDict['properties']['DEMPrefix'] = '|'.join(['E', demURL])
    else:
        prefixParts = ['I', ps, demURL]
        if renderingRule:
            if demURL != 'https://elevation3d.arcgis.com/arcgis/rest/services/WorldElevation3D/Terrain3D/ImageServer':
                prefixParts.append(renderingRule)
        oicDict['properties']['DEMPrefix'] = '|'.join(prefixParts)
    with open(oicPath, 'w') as oicFile:
        json.dump(oicDict, oicFile)

def getCustomParamKeys(valList):
    keys = []
    for val in valList:
        keys.append(val[0])
    return set(keys)

def addImagesToOIC(params, defValues, log, isInputOICFile):
    with open('C:/Users/Alex/Desktop/testtest3.txt', 'r+') as tt:
        for a in params:
            tt.write(a)
            tt.write('\n')
            tt.write(str(params[a].value))
            tt.write('\n')
            tt.write(str(params[a].valueAsText))
        tt.write('addImages')
        tt.write(str(params))
        tt.write('\n')
        tt.write(str(defValues))
        tt.write('\n')
        tt.write(str(log))
        tt.write('\n')
        tt.write(str(isInputOICFile))
    if not isInputOICFile:
        grpLayer = params['inputOIC'].value
        if not grpLayer:
            return None
        grpLayers = grpLayer.listLayers()
        for gLyr in grpLayers:
            gLyrDec = arcpy.Describe(gLyr)
            if gLyrDec.shapeType == 'Point':
                outPath = gLyrDec.catalogPath
                break
        oicFileName = os.path.join(os.path.dirname(os.path.dirname(outPath)),grpLayer.name+'.OIC')
    else:
        oicFileName = params['inputOIC'].valueAsText
        with open(oicFileName) as oic:
            inputOICJSON = json.load(oic)
            outPath = inputOICJSON['properties']['PointsSource']
    try:
        lastObjectId = returnLastOID(outPath)
        addedFields = addMissingFields(outPath,['All'])
    except Exception as e:
        arcpy.AddMessage(str(e))
        arcpy.AddMessage(type(e))
    if params['dem'].valueAsText:
        updateDEM(oicFileName, params['dem'].valueAsText, params['renderingRule'].enabled, params['renderingRule'].valueAsText)
    customType = params['inputType'].valueAsText
    log.Message('Input type: ' + customType, log.const_general_text)
    customValues = params['customParameters'].value
    log.Message('Extracting parameters..', log.const_general_text)
    customValuesAsJson = returnParametersAsJson(customValues)
    log.Message('Extracting input parameters..', log.const_general_text)
    inputParams = getOICInput(params)
    try:
        import oic_types
        typeApp = oic_types.OICType(customType)
        if (typeApp.init()):
            typeApp.run(outPath, customValuesAsJson, inputParams, defValues, log)
        else:
            arcpy.AddMessage('There was an error running the {} tool.',format(customType))
            log.Message('There was an error running the {} tool.',format(customType), log.const_general_text)
        deleteEmptyFields(outPath, lastObjectId, addedFields)
    except Exception as errormsg:
        arcpy.AddMessage("Call OIC Types:"+str(errormsg))
        log.Message("Call OIC Types:"+str(errormsg), log.const_critical_text)


    if (arcpy.ProductInfo() == 'ArcView'):
        pass
    else:
        arcpy.RecalculateFeatureClassExtent_management(outPath)

    with open(oicFileName) as oicTFile:
        oicDict = json.load(oicTFile)
    keyList = defValues.keys()
    valueList = []
    for k in keyList:
        if k == 'OIType':
            oicDict["properties"]["DefaultAttributes"][k] = defValues[k][0] if defValues[k] else ''
        elif k == 'MaxDistance':
            oicDict['properties']['MaxDistance'] = defValues[k] if defValues[k] else ''
        else:
            oicDict["properties"]["DefaultAttributes"][k] = defValues[k] if defValues[k] else ''

    with open(oicFileName, 'w') as outfile:
        json.dump(oicDict, outfile)


def MOI_getAvailableBuckets(ctlProfileType, ctlProfileName):
    try:
        import OptimizeRasters
        if (ctlProfileType.valueAsText):
            inputSourceType = ctlProfileType.valueAsText.lower()
            storageType = OptimizeRasters.Store.TypeAmazon
            if (inputSourceType.startswith('local')):
                return []
            elif (inputSourceType.find('azure') != -1):
                storageType = OptimizeRasters.Store.TypeAzure
            elif (inputSourceType.find('google') != -1):
                storageType = OptimizeRasters.Store.TypeGoogle
            ORUI = OptimizeRasters.OptimizeRastersUI(ctlProfileName.value, storageType)
            if (not ORUI):
                raise Exception()
            return ORUI.getAvailableBuckets()
    except:
        pass
    return []

def MOI_config_Init(parentfolder, filename):
    if (not parentfolder or
            not filename):
        return None
    global config
    global awsfile
    config = ConfigParser.RawConfigParser()
    homedrive = os.getenv('HOMEDRIVE')
    homepath = os.getenv('HOMEPATH')
    homefolder = os.path.join(homedrive, homepath)
    awsfolder = os.path.join(homefolder, parentfolder)
    if (filename == '*.json'):  # google cs filter
        for r, d, f in os.walk(awsfolder):
            for service in f:
                config.add_section(os.path.join(r, service).replace('\\', '/'))
            break
        return config
    awsfile = os.path.join(awsfolder, filename)
    if os.path.exists(awsfile) == True:
        print (awsfile)
        try:
            config.read(awsfile)
        except:
            pass
        return config
    else:
        if os.path.exists(os.path.dirname(awsfile)) == False:
            os.makedirs(os.path.dirname(awsfile))
        mode = 'w+'
        tmpFile = open(awsfile, mode)
        with open(awsfile, mode) as tmpFIle:
            tmpFIle.close
        return config

def MOI_CreateORJob(orjobFN,orJobHeader,imageList):

    mode =  'w+'
    tmpFile = open(orjobFN, mode)

    allKeys = orJobHeader.keys()
    for aKey in allKeys:
        lineToWrite = '# '+aKey+'='+orJobHeader[aKey] +'\n'
        tmpFile.write(lineToWrite)

    tmpFile
    for imgFN in imageList:
        tmpFile.write(imgFN+'\n')

    tmpFile.close()

def updateOICProperties(originalJson,updateList):

    updateDict = {}

    for ll in updateList:
        updateKey = ll[0]
        if ':' in updateKey:
            #print 'before:'+updateKey
            strList = updateKey.split(':')
            #print len(strList)
            updateKey = strList[(len(strList)-1)]
            #print 'after:'+updateKey
            if not updateDict.get(strList[0]):
                updateDict[strList[0]] = {}
            updateDict[strList[0]][updateKey] = ll[1]
        else:
            updateDict[updateKey] = ll[1]
    originalJson.get('properties').update(updateDict)
    return originalJson

def returnValidURLFormat(url):
    return url.replace('\\', '/')

def isUserSignedIn():
    tokenDict = arcpy.GetSigninToken()
    if tokenDict:
        token = tokenDict.get('token')
        if token:
            return True
    return False

def createVectorTilePackageFromOIC(inputOIC, log):
    try:
        templateFolder = os.path.dirname(os.path.realpath(__file__))
        projectTemplate = arcpy.mp.ArcGISProject(os.path.join(templateFolder,'ProjectTemplate.aprx'))
        projectTemplate.importDocument(os.path.join(templateFolder,'MapTemplate.mapx'), False)
        mapList = projectTemplate.listMaps('MapTemplate')
        inputMap = mapList[0]
        loadedLayers = inputMap.listLayers("*")
        if len(loadedLayers) > 0:
            for loadedLayer in loadedLayers:
                if loadedLayer.name != 'WorldMercatorExtent':
                    inputMap.removeLayer(loadedLayer)
        WMELayerList = inputMap.listLayers('WorldMercatorExtent')

        if (len(WMELayerList) == 0):

            WMEFC = os.path.join(projectTemplate.defaultGeodatabase,'WorldMercatorExtent')
            if arcpy.Exists(WMEFC):
                aExtentLayer = inputMap.addDataFromPath(WMEFC)
                sym = aExtentLayer.symbology
                sym.renderer.symbol.color = {'RGB' : [76, 230, 0, 100]}
                sym.renderer.symbol.outlineColor = {'RGB' : [76, 230, 0, 100]}
                aExtentLayer.symbology = sym
            else:
                WMETemplate = os.path.join(templateFolder,'WorldMercatorExtent.lpkx')
                print(WMETemplate)
                inputMap.addDataFromPath(WMETemplate)
        self.loadOIC(inputOIC, log, projectTemplate)
        with open(inputOIC) as oic:
            inputOICJSON = json.load(oic)
            coverageFeatureClassPath = inputOICJSON['properties']['CoverageSource']
        gLyrsourceDir = os.path.dirname(os.path.dirname(coverageFeatureClassPath))
        if gLyrsourceDir != None:

            outFileName = os.path.join(gLyrsourceDir, os.path.splitext(os.path.basename(inputOIC))[0] +'.vtpk')

            #arcpy.AddMessage(aCount)
            aCount = int(arcpy.GetCount_management(coverageFeatureClassPath)[0])
            if aCount == 0:
                arcpy.AddWarning( 'No records found in the Coverage Map Layer. The Coverage Map will be blank. To rectify run Create Coverage Features first and re-run this tool.')
                log.Message('No records found in the Coverage Map Layer. The Coverage Map will be blank. To rectify run Create Coverage Features first and re-run this tool.', log.const_warning_text)
            else:
                WMELayerList = inputMap.listLayers('WorldMercatorExtent')
                if (len(WMELayerList) == 1):
                    inputMap.removeLayer(WMELayerList[0])

                arcpy.CreateVectorTilePackage_management (inputMap, outFileName, "ONLINE", "","INDEXED")

                arcpy.AddMessage('Vector Tile Package created for '+grpLayer.name)
                log.Message('Vector Tile Package created for {}'.format(grpLayer.name), log.const_general_text)
    except Exception as e:
        log.Message('Error in creating vector tile package from OIC:{}'.format(str(e)), log.const_critical_text)
        arcpy.AddMessage('Error in creating vector tile package from OIC:{}'.format(str(e)))

def getImageryTypesFromCSV():
    csvPath = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'DefaultValues.csv')
    imageryTypes = {}
    try:
        with open(csvPath, newline='') as csvfile:
            reader = csv.DictReader(csvfile, skipinitialspace=True)
            for row in reader:
                row = dict(row)
                imageryType = {row['Type']: {
                                  'OIType': row['OIType'],
                                  'CamHeading': row['CamHeading'],
                                  'CamPitch': row['CamPitch'],
                                  'CamRoll': row['CamRoll'],
                                  'HFOV': row['HFOV'],
                                  'VFOV': row['VFOV'],
                                  'AvgHtAG': row['AvgHtAG'],
                                  'NearDist': row['NearDist'],
                                  'FarDist': row['FarDist'],
                                  'MaxDist': row['MaxDist'],
                                  'ImgRot': row['ImgRot']
                              }}
                imageryTypes.update(imageryType)
    except Exception as e:
        return {}
    return imageryTypes

def updateFeatureDefinition(featureServiceItemId, updateDefinition):
    gis = GIS(arcpy.GetActivePortalURL(), token=arcpy.GetSigninToken()['token'])
    featureServiceItem = gis.content.get(featureServiceItemId)
    featureLayer = featureServiceItem.layers[0]
    return featureLayer.manager.update_definition(updateDefinition)

def addAttachment(args):
    featureServiceItemId = args[0]
    objectId = args[1]
    path = args[2]
    sharedList = args[3]
    try:
        gis = GIS(arcpy.GetActivePortalURL(), token=arcpy.GetSigninToken()['token'])
        featureServiceItem = gis.content.get(featureServiceItemId)
        featureLayer = featureServiceItem.layers[0]
        attachmentJSON = featureLayer.attachments.add(objectId, path)
        if not attachmentJSON:
            return {"attachmentId": 0, "error": "Error in adding attachment"}
        if attachmentJSON.get('error'):
            sharedList.append(objectId)
            return {"attachmentId": 0, "error": attachmentJSON.get('error').get('message')}
        return {"attachmentId": attachmentJSON.get('addAttachmentResult').get('objectId'), "error": ""}
    except Exception as e:
        sharedList.append(objectId)
        return {"attachmentId": 0, "error": str(e)}

def addAttachmentsToFeatureService(featureClassPath, featureServiceItemId, attachments, log):
    #Add attachments in parallel
    manager = multiprocessing.Manager()
    sharedList = manager.list()
    attachmentsLength = len(attachments)
    args = [(featureServiceItemId, attachment['id'], attachment['path'], sharedList) for attachment in attachments]
    count = 0
    with concurrent.futures.ProcessPoolExecutor() as executor:
        for arg, attachmentResponse in zip(args, executor.map(addAttachment, args)):
            objectId = arg[1]
            attachmentId = attachmentResponse.get('attachmentId')
            error = attachmentResponse.get('error')
            if error:
                log.Message("Error in adding attachment for object id: {}. Error:{}".format(objectId, error), log.const_warning_text)
            if attachmentId:
                count += 1
                arcpy.AddMessage("Added attachment {} of {}".format(count, attachmentsLength))
                log.Message("Added attachment {} of {}".format(count, attachmentsLength), log.const_general_text)
        executor.shutdown(wait=True)
    objectIds = [id for id in sharedList]
    return objectIds

def addAttachmentsWithRetry(featureClassPath, featureServiceItemId, log):
    #Adding attachments to feature service. If adding attachment failes, retries upto 5 times.
    objectIds = []
    numberOfRetries = 5
    for n in range(numberOfRetries):
        attachments = getObjectIdAndImagePaths(featureClassPath, objectIds)
        objectIds = addAttachmentsToFeatureService(featureClassPath,
                                                  featureServiceItemId, attachments, log)
        if objectIds:
            if n < (numberOfRetries - 1):
                log.Message("{} attachments failed to attach. Retrying..".format(len(objectIds)), log.const_general_text)
                arcpy.AddMessage("{} attachments failed to attach. Retrying..".format(len(objectIds)))
            elif n == (numberOfRetries - 1):
                log.Message("{} attachments failed to attach even after retrying".format(len(objectIds)), log.const_general_text)
                arcpy.AddMessage("{} attachments failed to attach even after retrying".format(len(objectIds)))
        if not objectIds:
            break
    if objectIds:
        log.Message("All complete..", log.const_general_text)
        arcpy.AddMessage("All complete..")

def updateImagePaths(featureServiceItemId, log):
    try:
        #Updates image path for rows with attachmnets to FA
        gis = GIS(arcpy.GetActivePortalURL(), token=arcpy.GetSigninToken()['token'])
        featureServiceItem = gis.content.get(featureServiceItemId)
        featureLayer = featureServiceItem.layers[0]
        attachments = featureLayer.attachments.search('1=1')
        objectIds = set([attachment['PARENTOBJECTID'] for attachment in attachments])
        updatelist = []
        for objectId in objectIds:
            updatelist.append({'attributes': {'objectid': objectId, 'image': 'FA'}})
        featureLayer.edit_features(updates=updatelist)
    except Exception as e:
        log.Message("Error in updating image paths {}".format(str(e)), log.const_critical_text)

def getObjectIdAndImagePaths(featureClassPath, objectIds=[]):
    #Returns object ids and image paths for the input object ids. If no objectids are passed, returns for all.
    imagePaths = []
    cursor = arcpy.da.SearchCursor(featureClassPath, ['OBJECTID', 'Image'])
    for row in cursor:
        if os.path.exists(row[1]):
            if objectIds and row[0] in objectIds:
                imagePaths.append({'id': row[0],
                               'path': row[1]})
            if not objectIds:
                imagePaths.append({'id': row[0],
                                    'path': row[1]})
    return imagePaths

def isServiceNameAvailable(serviceName, log, serviceType='Feature Service'):
    orgId = arcpy.GetPortalDescription().get('id')
    portalURL = arcpy.GetActivePortalURL().strip('/')
    token = arcpy.GetSigninToken()['token']
    checkServiceNameURL = '{}/sharing/rest/portals/{}/isServiceNameAvailable'.format(portalURL, orgId)
    params = {
                 'name': serviceName,
                 'type': serviceType,
                 'token': token,
                 'f': 'json'
            }
    try:
        response = requests.post(checkServiceNameURL, params, verify=False)
        responseJSON = response.json()
    except Exception as e:
        log.Message("Could not check for the availability of the service {}. {}".format(serviceName, str(e)),
                    log.const_critical_text)
        return
    return responseJSON.get('available')

def getCurrentTimeStampStr():
    timeStr = datetime.now().isoformat(timespec='seconds').replace('-','').replace(':','')
    return timeStr

def getFeatureServiceNameFromOIC(oicFilePath, oicFileName):
    with open(oicFilePath) as oicFile:
        oicJson = json.load(oicFile)
    if oicJson['properties']['ServiceURL']:
        if 'rest/services/Hosted/' in oicJson['properties']['ServiceURL']:
            serviceName = oicJson['properties']['ServiceURL'].split(
                'rest/services/Hosted/')[1].split('/FeatureServer')[0]
        else:
            serviceName = oicJson['properties']['ServiceURL'].split('rest/services/')[1].split('/FeatureServer')[0]
    else:
        serviceName = '{}_ExposurePoints'.format(oicFileName)
    return serviceName

def getServiceNameFromOICJson(oicJSON, serviceType):
    serviceName = ''
    urlNodeName = ''
    if serviceType == 'FeatureServer':
        urlNodeName = 'ServiceURL'
    elif serviceType == 'VectorTileServer':
        urlNodeName = 'OverviewURL'
    if oicJSON['properties'][urlNodeName]:
        if 'rest/services/Hosted/' in oicJSON['properties'][urlNodeName]:
            serviceName = oicJSON['properties'][urlNodeName].split(
                'rest/services/Hosted/')[1].split('/{}'.format(serviceType))[0]
        else:
            serviceName = oicJSON['properties'][urlNodeName].split(
                'rest/services/')[1].split('/{}'.format(serviceType))[0]
    return serviceName

def isReferenceOIC(oicFilePath, oicFileName):
    try:
        with open(oicFilePath) as oicFile:
            oicJson = json.load(oicFile)
        if not oicJson['properties']['ServiceURL']:
            return False
        if not oicJson['properties']['PointsSource']:
            return True
        pointsFCName = os.path.basename(oicJson['properties']['PointsSource'])
        derivedOICName = pointsFCName.split('_ExposurePoints')[0]
        if derivedOICName != oicFileName:
            return True
        return False
    except Exception as e:
        return False
