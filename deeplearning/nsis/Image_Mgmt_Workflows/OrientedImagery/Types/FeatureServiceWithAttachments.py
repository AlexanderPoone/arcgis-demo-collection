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
# Name: imagelist.py
# Description: This is an custom OIC type.
# Version: 2.3
# Date Created : 20190915
# Requirements: ArcGIS Pro 2.4
# Author: Esri Imagery Workflows team
#------------------------------------------------------------------------------

import arcpy
import os
import sys
import re
import gdal
import multiprocessing
import concurrent.futures
from concurrent.futures import ProcessPoolExecutor
import orientedimagerytools as oitools
from arcgis.features import FeatureLayer
from arcgis.gis import GIS
multiprocessing.set_executable(os.path.join(sys.exec_prefix, 'pythonw.exe'))

def __init__(self, nametype):
    self._name = nametype



def main(oicPath, oicParas, inputParams, defValues, log=None):
    try:
        outPathSRS = arcpy.Describe(oicPath).spatialReference
        featureService = oicParas['FeatureServiceURL']
        gis = GIS(arcpy.GetActivePortalURL(), token=arcpy.GetSigninToken()['token'])

        if 'id=' in featureService.lower():
            itemId = getItemIdFromURL(featureService)
            featureServiceItem = gis.content.get(itemId)
            if not featureServiceItem:
                arcpy.AddError("Please verify the feature service item URL and the active portal.")
                log.Message("Please verify the feature service item URL and the active portal.", log.const_critical_text)
                return ("Error in adding attachments." )
            featureService = featureServiceItem.url
        featureLayer = FeatureLayer(featureService, gis=gis)
        featureLayerProperties = featureLayer.properties
        imageList = []
        if featureLayerProperties.get('layers'):
            for layer in featureLayerProperties['layers']:
                featureSubLayer = FeatureLayer('{}/{}'.format(featureService, layer['id']), gis=gis)
                imageList = getImageListFromFeatureLayerURL(featureSubLayer, outPathSRS)
        else:
            imageList = getImageListFromFeatureLayerURL(featureLayer, outPathSRS)
        addImageURLs(oicPath, imageList, outPathSRS, defValues, log)
        return("Successfully added attachments.")
    except Exception as e:
        if log:
            log.Message("Error in adding attachments. {}".format(str(e)), log.const_critical_text)
        return ("Error in adding attachments." + str(e))

def getItemIdFromURL(itemURL):
    itemURL = itemURL.lower()
    itemId = ''
    if 'id=' in itemURL:
        idURLPart = itemURL.split('id=')[1]
        idMatch = re.search(r'([0-9A-Za-z]+)', idURLPart)
        itemId = idMatch.group(1)
    else:
        return itemURL
    return itemId

def getExifData(imageDict):
    imageURL = imageDict['imageURL']
    return gdal.Info('/vsicurl/{}'.format(imageURL), allMetadata=True, format='json')

def getImageListFromFeatureLayerURL(featureLayer, outsrs):
    imageList = []
    featureSubLayerProperties = featureLayer.properties
    if featureSubLayerProperties.get('type') == 'Feature Layer' and featureSubLayerProperties.get('geometryType') == 'esriGeometryPoint' and featureSubLayerProperties.get('hasAttachments'):
        attachments = featureLayer.attachments.search()
        featureSet = featureLayer.query('1=1', out_fields='*')
        features = featureSet.features
        for attachment in attachments:
            attachmentURL = attachment['DOWNLOAD_URL']
            pointGeometry = [f.geometry for f in features if f.attributes['OBJECTID'] == attachment['PARENTOBJECTID']][0]
            imageList.append({"point": {'x': pointGeometry['x'], 'y': pointGeometry['y'], 'srs': featureSet.spatial_reference.get('wkid')}, "imageURL": attachmentURL})
    return imageList

def addImageURLs(inputTable, imgList, outsrs, valueDefaults, log):
    importFields = ['SHAPE@','Name','Image','AcquisitionDate','CamHeading','CamPitch','CamRoll','HFOV','VFOV','AvgHtAG','FarDist','NearDist','OIType','SortOrder','CamOffset','Accuracy','ImgPyramids','DepthImg','CamOri','ImgRot']
    fcCursor = arcpy.da.InsertCursor(inputTable, importFields)
    imgCount = len(imgList)
    cntrCut = round((imgCount * 10) / 100)
    imgCntr = 0
    #Multi processing
    with concurrent.futures.ProcessPoolExecutor() as executor:
        for imgDict, exif_data in zip(imgList, executor.map(getExifData, imgList)):
            inSRS = arcpy.SpatialReference(imgDict['point']['srs'])
            point = arcpy.Point(imgDict['point']['x'], imgDict['point']['y'])
            point = arcpy.PointGeometry(point, inSRS).projectAs(outsrs).centroid

            exif_data = exif_data['metadata']

            imageInfo = {}
            try:
                xmpData = exif_data['xml:XMP']

                if xmpData != None:
                    xmpString = oitools.readXMPString(xmpData,'drone-dji',"drone-dji:GimbalYawDegree")
                    if xmpString != '':
                        imageInfo['drone-dji:GimbalYawDegree'] = (xmpString.split('=')[1]).strip().replace('"', '')

                    xmpString = oitools.readXMPString(xmpData,'drone-dji',"drone-dji:GimbalPitchDegree")
                    if xmpString != '':
                        imageInfo['drone-dji:GimbalPitchDegree'] = ((xmpString.split('=')[1]).strip().replace('"', ''))

                    xmpString = oitools.readXMPString(xmpData,'drone-dji',"drone-dji:GimbalRollDegree")
                    if xmpString != '':
                        imageInfo['drone-dji:GimbalRollDegree'] = ((xmpString.split('=')[1]).strip().replace('"', ''))

            except:
                pass


            exif_data = exif_data['']
            exif_data.update(imageInfo)

            imageURL = imgDict['imageURL']
            imgCntr = imgCntr + 1
            name = imageURL.split('/FeatureServer')[0].split('/')[-1]
            if exif_data == {}:
                arcpy.AddWarning("Incomplete EXIF data. Could not add image: "+os.path.basename(imageURL))
                log.Message("Incomplete EXIF data. Could not add image: {}".format(os.path.basename(imageURL)), log.const_warning_text)
            else:
                    if '?' in imageURL:
                        tempimageURL = imageURL.split("?")[0]
                        imageURL = tempimageURL

                    row = []
                    row.append(point)
                    row.append(name)
                    row.append(imageURL)

                    dateTime = oitools._get_if_exist(exif_data, 'EXIF_DateTime')
                    if dateTime is not None:
                        dateTime = oitools.returnDate(dateTime)
                    else:
                        dateTime = oitools._get_if_exist(exif_data, 'EXIF_DateTimeOriginal')
                        if dateTime is not None:
                            dateTime = oitools.returnDate(dateTime)

                    row.append(dateTime)
                    # below method returns a dictionary of default parameters calculated from the image source
                    sourceDefaults = oitools.getDefaultValuesFromSource(exif_data)
                    OIType = valueDefaults['OIType'][0]
                    row.extend([sourceDefaults['CamHeading'], sourceDefaults['CamPitch'],
                                       sourceDefaults['CamRoll'], sourceDefaults['HFOV'],
                                       sourceDefaults['VFOV'], sourceDefaults['AvgHtAG'],
                                       sourceDefaults['FarDist'], sourceDefaults['NearDist'],
                                       OIType])
                    row.extend([0, None, None, None, None, ''])
                    imgRot = oitools._get_if_exist(exif_data, 'EXIF_Orientation')
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
                    row.append(imgRot)
                    fcCursor.insertRow(row)
                    if imgCntr % 10 == 0:
                        arcpy.AddMessage("Extracted Data for {} of {}".format(str(imgCntr), str(imgCount)))
                    elif imgCntr == imgCount:
                        arcpy.AddMessage("Extracted Data for {} of {}".format(str(imgCntr), str(imgCount)))
                    log.Message('Inserted row for: {}'.format(imageURL), log.const_general_text)

    del fcCursor

