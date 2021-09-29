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
# Name: imageService.py
# Description: This is a custom OIC type for imageservice data.
# Version: 2.3
# Date Created : 20181126
# Date updated : 20200402
# Requirements: ArcGIS Pro 2.2
# Author: Esri Imagery Workflows team
#------------------------------------------------------------------------------

import arcpy
import os
import sys
import urllib
import time
import json
import requests
import math
import datetime
import multiprocessing
import concurrent.futures
from concurrent.futures import ProcessPoolExecutor
multiprocessing.set_executable(os.path.join(sys.exec_prefix, 'pythonw.exe'))

class calcOICFieldsVals(object):
    def calcValues(self, interiorOrientation, exteriorOrientation, averageZ, focalLength, cameraZ):
        try:

            omega = math.atan((-1 *exteriorOrientation[7])/ exteriorOrientation[8])
            phi = math.asin(exteriorOrientation[6])
            kappa = math.atan(exteriorOrientation[3]/ exteriorOrientation[0])


            camHeading = (math.atan2(-1 * (math.sin(phi)), (-1 * (-math.sin(omega) * math.cos(phi)))) * 180) / math.pi
            if (camHeading < 0):
                camHeading += 360
            camRoll = (math.atan2((-1 * ((math.sin(omega) * math.sin(kappa)) - (math.cos(omega) * math.sin(phi) * math.cos(kappa)))), (math.sin(omega) * math.cos(kappa)) + (math.cos(omega) * math.sin(phi) * math.sin(kappa))) * 180) / math.pi
            camPitch = (math.acos(math.cos(omega) * math.cos(phi)) * 180 / math.pi)

            if (len(interiorOrientation['coeffX']) != 0 and interiorOrientation['coeffX'][1] != 0):
                HFOV = 2 * ((math.atan((abs(2 * interiorOrientation['coeffX'][0]) + abs(interiorOrientation['coeffX'][1])) / (2 * focalLength))) * 180) / math.pi

            elif (len(interiorOrientation['coeffX']) != 0 and interiorOrientation['coeffX'][2] != 0):
                HFOV = 2 * ((math.atan((abs(2 * interiorOrientation['coeffX'][0]) + abs(interiorOrientation['coeffX'][2])) / (2 * focalLength))) * 180) / math.pi

            else:
                HFOV = None

            if (len(interiorOrientation['coeffY']) != 0 and interiorOrientation['coeffY'][1] != 0):
                VFOV = 2 * (math.atan((abs(2 * interiorOrientation['coeffY'][0]) + abs(interiorOrientation['coeffY'][1])) / (2 * focalLength)) * 180) / math.pi
            elif (len(interiorOrientation['coeffY']) != 0 and interiorOrientation['coeffY'][2] != 0):
                VFOV = 2 * (math.atan((abs(2 * interiorOrientation['coeffY'][0]) + abs(interiorOrientation['coeffY'][2])) / (2 * focalLength)) * 180) / math.pi
            else:
                VFOV = None
            if abs(math.tan(math.pi * camRoll / 180)) > 1:
                newHFOV = VFOV
                newVFOV = HFOV
            else:
                newHFOV = HFOV
                newVFOV = VFOV

            HFOV = newHFOV
            VFOV = newVFOV
            #camRoll = 0

            if VFOV:
                nearDistance = abs(cameraZ - averageZ) * math.tan((camPitch - (VFOV / 2)) * math.pi / 180)
                farDistance = abs((cameraZ - averageZ) * math.tan(((VFOV / 2) + camPitch) * math.pi / 180))
            else:
                nearDistance = 500     #Default values changed as per API code. from 2 to 500
                farDistance = 1000     #Default values changed as per API code. from 20 to 1000

            return camHeading,camPitch,camRoll,HFOV,VFOV,nearDistance,farDistance
        except Exception as exp:
            arcpy.AddMessage(str(exp))
            return False


def __init__(self, nametype):
    self._name = nametype

def returnJson(urlPath):
    try:
        try:
            page = requests.get(urlPath, stream=True, timeout=None, verify=False)
        except:
            arcpy.AddMessage("Retrying..")
            time.sleep(4)
            page = requests.get(urlPath, stream=True, timeout=None, verify=False)
        if'200' in str(page):
            jsDataStr = page.content
            jsData = json.loads(jsDataStr)
            if not jsData:
                return False
            return jsData
        else:
            return False
    except:
        return False

def getIcsCatalogData(args):
    inPath = args[0]
    OID = args[1]
    icsPath = inPath.strip('/') + r'/{0}/info/ics?f=json'.format(str(OID))
    catalogPath = inPath.strip('/') + r"/{0}?f=pjson".format(str(OID))
    icsData = returnJson(icsPath)                   #ics json
    if not icsData:
        return None, None
    catalogData = returnJson(catalogPath)
    return icsData, catalogData

def getOicFilePath(fcPath):
    oicParts = fcPath.split(os.sep)
    oicProjectPath = os.sep.join(oicParts[:-2])
    grpLayerName = '_'.join(oicParts[-1].split('_')[:-1])
    oicFilePath = os.path.join(oicProjectPath, '{}.oic'.format(grpLayerName))
    return oicFilePath

def updateOIC(oicPath, oicDict):
    with open(oicPath, 'w') as oicFile:
        json.dump(oicDict, oicFile)

def getSRSVar(oicFilePath, wkt):
    with open(oicFilePath) as oicFile:
        oicDict = json.load(oicFile)
    variables = oicDict['properties']['Variables']
    wktVars = [k for k in variables if variables[k] == wkt]
    if wktVars:
        return wktVars[0]
    else:
        srsvars = [v for v in variables if v.startswith('isSRS')]
        if not srsvars:
            oicDict['properties']['Variables']['isSRS'] = wkt
            updateOIC(oicFilePath, oicDict)
            return 'isSRS'
        srsvars.sort()
        lastVarCount = srsvars[-1].strip('isSRS')
        if not lastVarCount:
            oicDict['properties']['Variables']['isSRS1'] = wkt
            updateOIC(oicFilePath, oicDict)
            return 'isSRS1'
        else:
            varCount = str(int(lastVarCount) + 1)
            oicDict['properties']['Variables']['isSRS{}'.format(varCount)] = wkt
            updateOIC(oicFilePath, oicDict)
            return 'isSRS{}'.format(varCount)

def main(oicpath, oicparas, inputParams, defValues, log):
    try:
        outPathSRS = arcpy.Describe(oicpath).spatialReference
        inPath = oicparas['InputServiceURL']
        serviceJson =   inPath.strip('/') +'?f=pjson'                                   #for input fields
        queryJson = inPath.strip('/') + r"/query?returnIdsOnly=true&f=json"  # to get the object ids. Need to enhance further for paging

        outPathSRS = arcpy.Describe(oicpath).spatialReference

        #Get field List for input
        fldData = returnJson(serviceJson)
        if not fldData:
            arcpy.AddError("The input URL is invalid.")
            return ("Error in adding images from image service. The input URL is invalid.")
        stringfields = fldData['fields']

        #build a list of input fields
        inputFields = []
        for i in range(0,len(stringfields)):
            fldName = stringfields[i]['name']
            if (fldName == 'Shape') or (fldName == 'Shape_Area') or (fldName == 'Shape_Length') or (fldName == 'OBJECTID')  :        #these fields are to be ignored
                continue
            fldType = stringfields[i]['type'][13:]  #after removing "esriFieldType" string
            try:
                fldLength = stringfields[i]['length'] #not all fields have this parameter
            except:
                fldLength=""
            fldAlias = stringfields[i]['alias']
            inputFields.append(fldName)

            fieldChkList = arcpy.ListFields(oicpath,fldName)    #check if the field exist in the OIC, if not then add it
            #try:
                #if len(fieldChkList) == 0:
                    #arcpy.AddField_management(oicpath, fldName, fldType, "", "", fldLength, fldAlias)
                #else:
                    #arcpy.AddMessage( "The field name: " + fldName + " already exists.")
            #except:
                #continue

        #build the input list of output fields.
        outFldList = arcpy.ListFields(oicpath)
        outFldNameList = []
        for outfld in outFldList:
            if ('OBJECTID' in outfld.name) or ('Shape' in outfld.name):
                pass
            else:
                outFldNameList.append(outfld.name)

        outFldNameList.insert(0,'SHAPE@')

        OIDData = returnJson(queryJson)
        listObjectID = OIDData['objectIds'] #get a list of objectIDs
        outCursor = arcpy.da.InsertCursor(oicpath,outFldNameList)

        #declare class object
        obj = calcOICFieldsVals()
        if len(listObjectID) < 10000:
            batch = 100
        else:
            batch = 1000
        count = 0
        args = [(inPath, OID) for OID in listObjectID]
        with concurrent.futures.ProcessPoolExecutor() as executor:
            for arg, icsCatalogData in zip(args, executor.map(getIcsCatalogData, args)):
                icsData, catalogData = icsCatalogData
                if (not icsData) or (not icsData.get('ics')):
                    continue
                count += 1
                OID = arg[1]
                if icsData != False:
                    geodataXform = icsData['ics']['geodataXform']
                    frameXforms = [val for key,val in geodataXform.items() if type(val) == dict and val.get('type') and val['type'] == 'FrameXform']
                    if not frameXforms:
                        arcpy.AddWarning("Error in getting xform information for oid:{}".format(OID))
                        continue
                    frameXform = frameXforms[0]
                    if frameXform.get('spatialReference') and frameXform.get('spatialReference').get('latestWkid'):
                        inPathSRS = arcpy.SpatialReference(int(frameXform['spatialReference']['latestWkid']))
                        wkid = int(frameXform['spatialReference']['latestWkid'])
                    elif frameXform.get('spatialReference').get('wkt'):
                        inSRS = frameXform['spatialReference']['wkt']
                        inPathSRS = arcpy.SpatialReference()
                        inPathSRS.loadFromString(inSRS)
                        oicFilePath = getOicFilePath(oicpath)
                        wkid = '$_{}_$'.format(getSRSVar(oicFilePath, inSRS))
                    cameraX = float(frameXform['sensorPosition']['x'])
                    cameraY = float(frameXform['sensorPosition']['y'])
                    cameraZ = float(frameXform['sensorPosition']['z'])
                    interiorOrientation = frameXform['interiorOrientation']
                    exteriorOrientation = frameXform['exteriorOrientation']
                    #pixelSize = abs(interiorOrientation['coeffX'][1]) if interiorOrientation['coeffX'][1] else abs(interiorOrientation['coeffX'][2])
                    averageZ = float(frameXform['averageZ'])
                    principalX = float(frameXform['principalPoint']['x'])
                    principalY = float(frameXform['principalPoint']['y'])
                    focalLength = float(frameXform['focalLength'])
                    xmin = float(icsData['ics']['nativeExtent']['xmin'])
                    xmax = float(icsData['ics']['nativeExtent']['xmax'])
                    ymin = float(icsData['ics']['nativeExtent']['ymin'])
                    ymax = float(icsData['ics']['nativeExtent']['ymax'])
                    dx = float(icsData['ics']['dx'])
                    dy = float(icsData['ics']['dy'])

                    iWidth = round(abs(xmax-xmin) / dx)
                    iHeight = round(abs(ymax-ymin) / dy)

                    camHeading,camPitch,camRoll,HFOV,VFOV,nearDistance,farDistance = obj.calcValues(interiorOrientation,
                                                                                                    exteriorOrientation,
                                                                                                    averageZ,
                                                                                                    focalLength,
                                                                                                    cameraZ)


                                #1|WKID_H|WKID_V|X|Y|Z|H|P|R|A0|A1|A2|B0|B1|B2|FL|PPX|PPY|K1|K2|K3
                    A0 = interiorOrientation['inverseCoeffX'][0]
                    A1 = interiorOrientation['inverseCoeffX'][1]
                    A2 = interiorOrientation['inverseCoeffX'][2]
                    B0 = interiorOrientation['inverseCoeffY'][0]
                    B1 = interiorOrientation['inverseCoeffY'][1]
                    B2 = interiorOrientation['inverseCoeffY'][2]

                    K0 = frameXform['konradyParameters'][0]
                    K1 = frameXform['konradyParameters'][1]
                    K2 = frameXform['konradyParameters'][2]

##                    camOri = '|'.join(['1', str(wkid), str(wkid), str(cameraX), str(cameraY), str(cameraZ), str(camHeading), str(camPitch), str(camRoll), str(A0),
##                                       str(A1), str(A2), str(B0), str(B1), str(B2), str(focalLength), str(principalX),
##                                       str(principalY), str(K0), str(K1), str(K2)])
                    camOri = ""


                    valueList = [None] * (len(outFldNameList))
                    aPoint = arcpy.Point()
                    aPoint.X = cameraX
                    aPoint.Y = cameraY

                    aPtGeometry = arcpy.PointGeometry(aPoint,inPathSRS).projectAs(outPathSRS)
                    aPoint = aPtGeometry.centroid
                    valueList[0] = aPoint
                    attributes = catalogData['attributes']  #create a dictionary object with containing the fields and field values for an item in the image service
                    attributes.update({'CamHeading':camHeading})
                    attributes.update({'CamPitch':camPitch})
                    attributes.update({'CamRoll':float(camRoll)})
                    attributes.update({'HFOV':HFOV})
                    attributes.update({'VFOV':VFOV})
                    attributes.update({'NearDist':nearDistance})
                    attributes.update({'FarDist':farDistance})
                    attributes.update({'AvgHtAG': (cameraZ-averageZ)})
                    attributes.update({'Image':r'A|{0}|{1}|{2}|{3}'.format(inPath,OID,iWidth,iHeight)})
                    attributes.update({'Point':"{0},{1}".format(cameraX,cameraY)})
                    attributes.update({'ImgRot':-(float(camRoll))})
                    #attributes.update({'ImgRot': 0})
                    attributes.update({'CamOri': camOri})
                    attributes.update({'SortOrder': 0})
                    if attributes.get('AcquisitionDate'):
                        attributes.update({'AcquisitionDate': datetime.datetime.fromtimestamp(attributes['AcquisitionDate']/1000)})
                    #read and set the values from the input table.
                    for x in range(0, len(outFldNameList)):
                        infldName = outFldNameList[x]

                        if ('OBJECTID' in infldName) or ('Shape' in infldName):
                            #handle things.
                            continue
                        else:
                            try:
                                aValue = attributes[infldName]              #fetch the value from the attributes dictionary
                                outindex = outFldNameList.index(infldName)  #fetch the index of the current field from the output field list
                                valueList[outindex] = aValue               #update the valueList at that index
                            except:
                                continue

                    #Set all the default values.
                    defKeys = defValues.keys()
                    for aKey in defKeys:
                        if aKey in outFldNameList:
                            keyindex = outFldNameList.index(aKey)       #fetch the index of the current field from the output field list
                            tdefVal = defValues[aKey]                   #store the parameter value
                            try:
                                if tdefVal is not None:
                                    defVal = float(tdefVal)
                                else:
                                    defVal = None
                            except:
                                defVal = tdefVal[0]                        #exception will occur only for OIType as it is string and for this field the value is only the first character
                            if valueList[keyindex] is None or valueList[keyindex]=="" :
                                valueList[keyindex] = defVal     #fill up the default values only if the current value at that index is None

                    #add records
                    outCursor.insertRow(valueList)
                    if count % batch == 0:
                        arcpy.AddMessage("Added {} rows out of {}".format(str(count), str(len(listObjectID))))
        del outCursor,obj
        return("Completed")
    except Exception as e:
        arcpy.AddMessage("Error in adding images from image service. {}".format(str(e)))
        if log:
            log.Message("Error in adding images from image service. {}".format(str(e)), log.const_critical_text)
        return("Error in adding images from image service. {}".format(str(e)))