import arcpy
import os
from os.path import basename, expanduser
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
import feature_service
from feature_service import FeatureServiceUtil
from concurrent.futures import ProcessPoolExecutor

from glob import glob
from random import randint

from natsort import natsorted

if (sys.version_info[0] < 3):
    import ConfigParser
else:
    import configparser as ConfigParser

multiprocessing.set_executable(os.path.join(sys.exec_prefix, 'pythonw.exe'))
gdalPath = os.path.join(os.path.dirname(os.path.dirname(__file__)),'Dependents/OptimizeRasters/GDAL/bin')
gdalPath = os.path.normpath(gdalPath)
# "PROJCS['WGS_1984_Web_Mercator_Auxiliary_Sphere',GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Mercator_Auxiliary_Sphere'],PARAMETER['False_Easting',0.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',0.0],PARAMETER['Standard_Parallel_1',0.0],PARAMETER['Auxiliary_Sphere_Type',0.0],UNIT['Meter',1.0]]", 

# ~\Documents\ArcGIS\Projects\MyProject35\MyProject35.gdb, 

# abc, 

# {'outputGDB': <geoprocessing parameter object object at 0x00000261E85FF4F0>, 'catalogName': <geoprocessing parameter object object at 0x00000261E85FB9F0>, 'catalogSRS': <geoprocessing parameter object object at 0x00000261E85FF530>, 'description': <geoprocessing parameter object object at 0x00000261E85FF570>, 'tags': <geoprocessing parameter object object at 0x00000261E85FF5B0>, 'copyright': <geoprocessing parameter object object at 0x00000261E85FF4B0>}, 

# <logger.Logger object at 0x00000261E86014E0>

# --------------------------------------------------------------------------------
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

def isServiceNameAvailable(serviceName, log=None, serviceType='Feature Service'):
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
        print("Could not check for the availability of the service {}. {}".format(serviceName, str(e)),
                    log.const_critical_text)
        return
    return responseJSON.get('available')

def getCurrentTimeStampStr():
    timeStr = datetime.now().isoformat(timespec='seconds').replace('-','').replace(':','')
    return timeStr

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

def updateFeatureDefinition(featureServiceItemId, updateDefinition):
    gis = GIS(arcpy.GetActivePortalURL(), token=arcpy.GetSigninToken()['token'])
    featureServiceItem = gis.content.get(featureServiceItemId)
    featureLayer = featureServiceItem.layers[0]
    return featureLayer.manager.update_definition(updateDefinition)

def addAttachmentsWithRetry(featureClassPath, featureServiceItemId, log=None):
    #Adding attachments to feature service. If adding attachment failes, retries upto 5 times.
    objectIds = []
    numberOfRetries = 5
    for n in range(numberOfRetries):
        attachments = getObjectIdAndImagePaths(featureClassPath, objectIds)
        objectIds = addAttachmentsToFeatureService(featureClassPath,
                                                  featureServiceItemId, attachments, None)
        if objectIds:
            if n < (numberOfRetries - 1):
                print("{} attachments failed to attach. Retrying..".format(len(objectIds)))
                arcpy.AddMessage("{} attachments failed to attach. Retrying..".format(len(objectIds)))
            elif n == (numberOfRetries - 1):
                print("{} attachments failed to attach even after retrying".format(len(objectIds)))
                arcpy.AddMessage("{} attachments failed to attach even after retrying".format(len(objectIds)))
        if not objectIds:
            break
    if objectIds:
        print("All complete..")
        arcpy.AddMessage("All complete..")

def updateImagePaths(featureServiceItemId, log=None):
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
        print("Error in updating image paths {}".format(str(e)))

def CreateCoverageFeatures(parameters):

    # log = initializeLog('CreateCoverageFeatures')
    # initializeVersionCheck(log)
    row = None
    isInputOICFile = False
    try:
        try:
            currProj = arcpy.mp.ArcGISProject(expanduser(r"~\Documents\ArcGIS\Projects\MyProject35\MyProject35.gdb"))
        except:
            isInputOICFile = True
        if parameters[0].valueAsText.lower().endswith('.oic'):
            isInputOICFile = True
        # if not isInputOICFile:
        #     grpLayer = parameters[0].value
        #     grpLayers = grpLayer.listLayers()

        #     defprops = {}

        #     for gLyr in grpLayers:
        #         gLyrDec = arcpy.Describe(gLyr)
        #         if gLyrDec.shapeType == 'Point':
        #             inputFeatureClass = gLyr
        #             gLyrsource = gLyrDec.catalogPath
        #             gLyrsourceDir = os.path.dirname(os.path.dirname(gLyrsource))
        #             oicFilePath = os.path.join(gLyrsourceDir,grpLayer.name+'.oic')
        #             try :
        #                 with open(oicFilePath) as f:
        #                     oic_file = json.load(f)
        #                 defprops = oic_file['properties']['DefaultAttributes']

        #             except:
        #                 defprops = {}

        #         elif gLyrDec.shapeType == 'Polygon':
        #             outputFeatureClass = gLyr
        # else:
        oicFilePath = parameters[0].valueAsText
        with open(oicFilePath) as f:
            oic_file = json.load(f)
        defprops = oic_file['properties']['DefaultAttributes']
        outputFeatureClass = oic_file['properties']['CoverageSource']
        inputFeatureClass = oic_file['properties']['PointsSource']

        #["Calculate Coverage", "Create Buffer", "Use Exposure Point Extent"]
        covCreateOption = parameters[1].valueAsText
        covCreateOption = covCreateOption.lower()

        fieldList = arcpy.ListFields(outputFeatureClass,'Name')
        if len(fieldList) == 0:
            arcpy.AddField_management(outputFeatureClass, 'Name', "TEXT", 0, 0, 100, 'Name')

        if True:
            databasePath = os.path.dirname(arcpy.Describe(outputFeatureClass).catalogPath)

            bufferName = os.path.join(databasePath,arcpy.CreateUniqueName("Buffer",databasePath))
            simplifyName = os.path.join(databasePath,arcpy.CreateUniqueName("Simplify",databasePath))
            statsName = os.path.join(databasePath,arcpy.CreateUniqueName("Stats",databasePath))

            farDistFldList = arcpy.ListFields(inputFeatureClass,'FarDist')
            getMean = False

            if len(farDistFldList) == 0:
                farDist = defprops['FarDist']+' Meters'
            else:
                farDist = 'FarDist'
                getMean = True

            try:
                arcpy.AddMessage('Buffering')
                arcpy.analysis.Buffer(inputFeatureClass,bufferName, farDist, "FULL", "ROUND", "ALL", None, "GEODESIC")

                if getMean:
                    arcpy.AddMessage('Getting Mean FarDist')
                    arcpy.analysis.Statistics(inputFeatureClass,statsName,"FarDist MEAN", None)

                    statCursor = arcpy.da.SearchCursor(statsName, ['MEAN_FarDist'])
                    for srow in statCursor:
                        farDistMean = srow[0]
                        #farDistMean = farDistMean

                    del srow
                    del statCursor

                else:
                    arcpy.AddMessage('Getting FarDist')
                    farDistMean = float( defprops['FarDist'])

                simplifyTol = max((farDistMean/100),1)

                #farDistMean = str(farDistMean)+' Meters'
                useSimplified = True
                if (arcpy.ProductInfo() == 'ArcView'):
                    useSimplified = False
                    pass
                else:
                    arcpy.AddMessage("Simplifying Polygons")
                    arcpy.SimplifyPolygon_cartography(bufferName, simplifyName, "POINT_REMOVE", simplifyTol)


                if int(arcpy.GetCount_management(outputFeatureClass)[0]) > 0:
                    arcpy.DeleteFeatures_management(outputFeatureClass)

                if useSimplified:
                    bufFldNames = ('SHAPE@')
                    bufCursor = arcpy.da.SearchCursor(simplifyName, bufFldNames)
                else:
                    bufFldNames = ('SHAPE@')
                    bufCursor = arcpy.da.SearchCursor(bufferName, bufFldNames)


                outFldName = ('SHAPE@','Name')
                outfcCursor = arcpy.da.InsertCursor(outputFeatureClass,outFldName)

                for bRow in bufCursor:
                    bShape = bRow[0]
                    bufValueList = []
                    bufValueList.append(bShape)
                    bufValueList.append('BufferedShape')
                    outfcCursor.insertRow(bufValueList)

                del bufCursor
                del bRow
                del outfcCursor

                arcpy.Delete_management(bufferName)
                if useSimplified:
                    arcpy.Delete_management(simplifyName)

                arcpy.Delete_management(statsName)

                arcpy.AddMessage('Done')
            except arcpy.ExecuteError:
                arcpy.AddError(arcpy.GetMessages())

        if (arcpy.ProductInfo() == 'ArcView'):
            pass
        else:
            arcpy.RecalculateFeatureClassExtent_management(outputFeatureClass)

        # closeLog(log)

    except Exception as e:
        arcpy.AddError('Error in CreatingCoverageFeatures:{}'.format(str(e)))
        # print('Error in CreateCoverageFeatures:{}'.format(str(e)))
        # closeLog(log)

def CreateCoverageMap(parameters):
    try:
        # log = initializeLog('CreateCoverageMap')
        # initializeVersionCheck(log)
        isInputOICFile = False
        try:
            aprx = arcpy.mp.ArcGISProject(expanduser(r"~\Documents\ArcGIS\Projects\MyProject35\MyProject35.gdb"))
        except:
            isInputOICFile = True
        if parameters[0].valueAsText.lower().endswith('.oic'):
            isInputOICFile = True
        if not isInputOICFile:
            activeMap = aprx.activeMap
            inputMapList = aprx.listMaps('MapTemplate')
            if len(inputMapList) >= 1:
                inputMap = inputMapList[0]
                loadedLayers = inputMap.listLayers("*")
                if len(loadedLayers) > 0:
                    for ll in loadedLayers:
                        if ll.name != 'WorldMercatorExtent':
                            inputMap.removeLayer(ll)
            else:
                mapTemplate = 'MapTemplate.mapx'
                templatePath = os.path.dirname(os.path.realpath(__file__))
                aprx.importDocument(os.path.join(templatePath,mapTemplate),False)

                inputMapList = aprx.listMaps('MapTemplate')
                if len(inputMapList) >= 1:
                    inputMap = inputMapList[0]
                    loadedLayers = inputMap.listLayers("*")
                    if len(loadedLayers) > 0:
                        for ll in loadedLayers:
                            if ll.name != 'WorldMercatorExtent':
                                inputMap.removeLayer(ll)
            #Check for the web Mercator extent layer.
            webMercatorLayerList = inputMap.listLayers('WorldMercatorExtent')

            if (len(webMercatorLayerList) == 0):

                webMercatorFeatureClass = os.path.join(aprx.defaultGeodatabase,'WorldMercatorExtent')
                #arcpy.AddMessage(WMEFC)
                if arcpy.Exists(webMercatorFeatureClass):
                    aExtentLayer = inputMap.addDataFromPath(webMercatorFeatureClass)
                    sym = aExtentLayer.symbology
                    sym.renderer.symbol.color = {'RGB' : [76, 230, 0, 100]}
                    sym.renderer.symbol.outlineColor = {'RGB' : [76, 230, 0, 100]}
                    aExtentLayer.symbology = sym
                else:
                    templatePath = os.path.dirname(os.path.realpath(__file__))
                    webMercatorTemplate = os.path.join(templatePath,'WorldMercatorExtent.lpkx')
                    inputMap.addDataFromPath(webMercatorTemplate)

            grpLayer = parameters[0].value
            grpLayers = grpLayer.listLayers()

            layerToAdd = None

            for gLyr in grpLayers:
                gLyrDec = arcpy.Describe(gLyr)
                gLyrsourceDir = None

                if gLyrDec.shapeType == 'Point':
                    pass
                elif gLyrDec.shapeType == 'Polygon':
                    aCount = arcpy.GetCount_management(gLyr)[0]
                    gLyrsource = gLyrDec.catalogPath
                    gLyrsourceDir = os.path.dirname(os.path.dirname(gLyrsource))
                    layerToAdd = gLyr
                    inputMap.addLayer(layerToAdd)
                    l1 = inputMap.listLayers()[0]
                    if l1.visible == False:
                        l1.visible = True

            if gLyrsourceDir != None:

                outFileName = os.path.join(gLyrsourceDir,grpLayer.name+'.vtpk')

                #arcpy.AddMessage(aCount)
                aCount = int(aCount)
                if aCount == 0:
                    arcpy.AddWarning( 'No records found in the Coverage Map Layer. The Coverage Map will be blank. To rectify run Create Coverage Features first and re-run this tool.')
                    print('No records found in the Coverage Map Layer. The Coverage Map will be blank. To rectify run Create Coverage Features first and re-run this tool.')
                else:
                    webMercatorLayerList = inputMap.listLayers('WorldMercatorExtent')
                    if (len(webMercatorLayerList) == 1):
                        inputMap.removeLayer(webMercatorLayerList[0])

                    arcpy.CreateVectorTilePackage_management (inputMap, outFileName, "ONLINE", "","INDEXED")

                    arcpy.AddMessage('Vector Tile Package created for '+grpLayer.name)
                    print('Vector Tile Package created for {}'.format(grpLayer.name))
        else:
            templatePath = os.path.dirname(os.path.realpath(__file__))
            currProj = arcpy.mp.ArcGISProject(os.path.join(templatePath,'ProjectTemplate.aprx'))
            currProj.importDocument(os.path.join(templatePath,'MapTemplate.mapx'), False)
            inputMapList = currProj.listMaps('MapTemplate')
            inputMap = inputMapList[0]
            oicFilePath = parameters[0].valueAsText
            with open(oicFilePath) as oic:
                inputOICJSON = json.load(oic)
                coverageFCPath = inputOICJSON['properties']['CoverageSource']
            print('Before')
            coverageLyr = arcpy.MakeFeatureLayer_management(coverageFCPath, os.path.splitext(os.path.basename(coverageFCPath))[0]).getOutput(0)
            print('After')
            layers = inputMap.listLayers()
            for l in layers:
                inputMap.removeLayer(l)
            inputMap.addLayer(coverageLyr)
            coverageLyr = inputMap.listLayers()[0]
            updateCoverageLayerSymbology(coverageLyr)
            vtpkFileName = '{}.vtpk'.format(os.path.splitext(oicFilePath)[0])
            # print('AAA')
            arcpy.CreateVectorTilePackage_management(inputMap, vtpkFileName, "ONLINE", "","INDEXED")
            # print('BBB')
            return coverageLyr
        # closeLog(log)
    except Exception as e:
        arcpy.AddError('Error in creating coverage map. {}'.format(str(e)))
        print('Error in creating coverage map. {}'.format(str(e)))
        # closeLog(log)

def PublishOrientedImageCatalog(parameters, coverageLyr):
    try:
        try:
            tokenDict = arcpy.GetSigninToken()
            portalToken = tokenDict['token']
        except:
            arcpy.AddMessage("Please login to your portal to continue.")
        isInputOICFile = False
        try:
            currProj = arcpy.mp.ArcGISProject(expanduser(r"~\Documents\ArcGIS\Projects\MyProject35\MyProject35.gdb"))
        except:
            isInputOICFile = True
        if parameters[0].valueAsText.lower().endswith('.oic'):
            isInputOICFile = True
        if not isInputOICFile:
            currProj = arcpy.mp.ArcGISProject(expanduser(r"~\Documents\ArcGIS\Projects\MyProject35\MyProject35.gdb"))
            currMap = currProj.activeMap
            pointFCPath = None
            vtpkFilePath = None
            if parameters[0].valueAsText.lower().endswith('.oic'):
                oicFilePath = parameters[0].valueAsText
                oicFileName = os.path.splitext(os.path.basename(oicFilePath))[0]
            else:
                grpLayer = parameters[0].value
                grpLayers = grpLayer.listLayers()
                for gLyr in grpLayers:
                    gLyrDec = arcpy.Describe(gLyr)
                    gLyrsource = gLyrDec.catalogPath
                    gLyrsourceDir = os.path.dirname(os.path.dirname(gLyrsource))
                    oicFilePath = os.path.join(gLyrsourceDir,grpLayer.name+'.oic')
                    oicFileName = grpLayer.name
                    if gLyrDec.shapeType == 'Point':
                        lyr = gLyr
                        pointFCPath = lyr.dataSource
                        pointFCShapeType = gLyrDec.shapeType
                    elif gLyrDec.shapeType == 'Polygon':
                        coverageFCPath = gLyr.dataSource
                        vtpkFilePath = os.path.join(gLyrsourceDir,grpLayer.name+'.vtpk')
                        vtpkFileName = os.path.basename(coverageFCPath)
            if not os.path.isfile(oicFilePath):
                arcpy.AddError("Please ensure that the Oriented imagery catalog file "+ os.path.basename(oicFilePath) + " is present in " + os.path.dirname(oicFilePath))
                print("Please ensure that the Oriented imagery catalog file "+ os.path.basename(oicFilePath) + " is present in " + os.path.dirname(oicFilePath),
                            log.const_critical_text)
                # closeLog(log)
                return
        else:
            if not parameters[0].valueAsText.lower().endswith('.oic'):
                arcpy.AddError("Only OIC file is supported as input in this mode.")
                # closeLog(log)
                return
            oicFilePath = parameters[0].valueAsText
            oicFileName = os.path.splitext(os.path.basename(oicFilePath))[0]
            with open(oicFilePath) as oic:
                inputOICJSON = json.load(oic)
                pointFCPath = inputOICJSON['properties']['PointsSource']
                coverageFCPath = inputOICJSON['properties']['CoverageSource']
                vtpkFilePath = os.path.splitext(oicFilePath)[0] + '.vtpk'
                vtpkFileName = os.path.basename(coverageFCPath)
            if pointFCPath:
                pointLyr = arcpy.MakeFeatureLayer_management(pointFCPath, os.path.splitext(os.path.basename(pointFCPath))[0]).getOutput(0)
                # coverageLyr = arcpy.MakeFeatureLayer_management(coverageFCPath, os.path.splitext(os.path.basename(coverageFCPath))[0]).getOutput(0)
                templateFolder = os.path.dirname(os.path.realpath(__file__))
                currProj = arcpy.mp.ArcGISProject(os.path.join(templateFolder,'ProjectTemplate.aprx'))
                currProj.importDocument(os.path.join(templateFolder,'MapTemplate.mapx'), False)
                mapList = currProj.listMaps('MapTemplate')
                if len(mapList) >= 1:
                    currMap = mapList[0]
                    currMap.addLayer(coverageLyr)
                    updateCoverageLayerSymbology(coverageLyr)
                    currMap.addLayer(pointLyr)
                else:
                    print("Error adding map to project template. Exiting..")
                    arcpy.AddError("Error adding map to project template. Exiting..")
                    return
                pointLayer = currMap.listLayers()[0]
                updatePointLayerSymbology(pointLayer)

        serviceTags = parameters[1].valueAsText
        tagsList = serviceTags.split(',')
        tagsList.append('OIC')
        oicTags = ','.join(set(tagsList))
        serviceDescription = parameters[2].valueAsText
        portal_desc = arcpy.GetPortalDescription()
        user_name = portal_desc['user']['username']
        portalurl = arcpy.GetActivePortalURL()
        orgName = portal_desc['name']
        serviceCredits = 'Copyright 2020 '+orgName+'.'+'Uploaded by '+user_name
        feature_service_util = FeatureServiceUtil(user_name,
                                                          portalurl)
        folder_id = None
        if parameters[3].value:
            folders = feature_service_util.list_all_portal_folders()
            folder_ids = [folder['id'] for folder in folders if folder['title'] == parameters[3].value]
            folder_id = folder_ids[0] if folder_ids else None
            if not folder_id:
                arcpy.AddError("Folder does not exist in portal.")
                print("Folder does not exist in portal.")
                # closeLog(log)
                return
        try:
            with open(oicFilePath) as f:
                oic_file = json.load(f)
        except Exception as e:
            arcpy.AddError('Error in reading Oriented Imagery Catalog file.')
            print('Error in reading Oriented Imagery Catalog file.{}'.format(str(e)))
            # closeLog(log)
            return
        if parameters[4].valueAsText == 'Publish all' or parameters[4].valueAsText == 'Publish all - overwrite':
            default_share_settings = {'everyone': False, 'org': True, 'groups': None}
            if not pointFCPath:
                arcpy.AddError("Exposure points feature class missing!")
                print("Exposure points feature class missing!")
                # closeLog(log)
                return
            if not vtpkFilePath:
                arcpy.AddError("Coverage map feature class missing!")
                print("Coverage map feature class missing!")
                # closeLog(log)
                return
            fc_summary = "Oriented Imagery Catalog: "+os.path.basename(pointFCPath)+" created using the Oriented Imagery Catalog tool for ArcGIS Pro."
            vtpk_summary = "Oriented Imagery Catalog: "+os.path.basename(vtpkFilePath)+" created using the Oriented Imagery Catalog tool for ArcGIS Pro."
            if oic_file['properties']['ServiceURL']:
                featureServiceName = getServiceNameFromOICJson(oic_file, 'FeatureServer')
            else:
                featureServiceName = os.path.basename(pointFCPath)
            if oic_file['properties']['OverviewURL']:
                coverageServiceName = getServiceNameFromOICJson(oic_file, 'VectorTileServer')
            else:
                coverageServiceName = vtpkFileName
            items = [{
                           "title": featureServiceName,
                           "type": "Feature Service",
                           "shared_with": default_share_settings,
                           "description": serviceDescription,
                           "tags": serviceTags,
                           "summary": fc_summary,
                           "credits": serviceCredits
                     },
                     {
                           "title": coverageServiceName,
                           "type": "Vector Tile Package",
                           "shared_with": default_share_settings,
                           "description": serviceDescription,
                           "tags": serviceTags,
                           "summary": vtpk_summary,
                           "credits": serviceCredits
                      },
                      {
                           "title": coverageServiceName,
                           "type": "Vector Tile Service",
                           "shared_with": default_share_settings,
                           "description": serviceDescription,
                           "tags": serviceTags,
                           "summary": vtpk_summary,
                           "credits": serviceCredits
                      }]
            if parameters[4].valueAsText == 'Publish all - overwrite':
                gis = GIS(portalurl, token=portalToken)
                item_ids = []
                for item in items:
                    item_json = feature_service_util.get_item(item.get('title'), item.get('type'), user_name)
                    if item_json:
                        if item.get('type') != 'Feature Service':
                            item_ids.append(item_json.get('id'))
                        item_obj = gis.content.get(item_json.get('id'))
                        item_share = item_obj.shared_with if item_obj else None
                        item['shared_with'] = item_share
                        item['credits'] = item_obj.accessInformation
                        item['summary'] = item_obj.snippet
                        if item['shared_with']['groups']:
                            item['shared_with']['groups'] = [group.id for group in item['shared_with']['groups']]
                delete_response = feature_service_util.delete_items(item_ids)
            try:
                with open(os.path.join(os.path.dirname(feature_service.__file__), 'service_definition.json')) as f:
                    service_definition = json.load(f)
                with open(os.path.join(os.path.dirname(feature_service.__file__), 'feature_definition.json')) as f:
                    feature_definiton = json.load(f)
            except Exception as e:
                arcpy.AddError('Something went wrong before uploading the exposure points!')
                print('Something went wrong before uploading the exposure points. {}'.format(str(e)))
                # closeLog(log)
                return
            extent = arcpy.Describe(pointFCPath).extent
            spatialReference = arcpy.Describe(pointFCPath).spatialReference
            feature_service_item = [item for item in items if item['type'] == "Feature Service"][0]
            feature_service_share_settings = feature_service_item['shared_with']

            if not isInputOICFile:
                layers = currMap.listLayers()
                group_layers = [l for l in layers if l.name == parameters[0].valueAsText and l.isGroupLayer]
                if group_layers:
                    group_layer = group_layers[0]
                else:
                    arcpy.AddError('Could not access the group layer.')
                    print('Could not access the group layer.',  log.const_critical_text)
                    # closeLog(log)
                    return
                pointCoverageLayers = group_layer.listLayers()
                pointLayers = [l for l in pointCoverageLayers if arcpy.Describe(l).shapeType == 'Point']
                if not pointLayers:
                    arcpy.AddError('Could not access the feature service layer.')
                    print('Could not access the feature service layer.',  log.const_critical_text)
                    # closeLog(log)
                    return
                pointLayer = pointLayers[0]
            currProj.save()
            #if oic_file['properties']['ServiceURL'] and parameters[4].valueAsText == 'Publish all':
                #arcpy.AddMessage("The points feature service is already published. Skipping..")
                #point_service_url = oic_file['properties']['ServiceURL']
            #else:
            arcpy.AddMessage("Publishing Exposure Points.")
            print("Publishing Exposure Points.")
            if oic_file['properties']['ServiceURL']:
                featureServiceName =  getServiceNameFromOICJson(oic_file, 'FeatureServer')
            else:
                featureServiceName = os.path.basename(pointFCPath)
                featureServiceNameAvailable = isServiceNameAvailable(os.path.basename(pointFCPath), None)
                if not featureServiceNameAvailable:
                    featureServiceName = '{}_{}'.format(featureServiceName, getCurrentTimeStampStr())
            publish_fc_response = feature_service_util.publish_feature_service(
                                                         pointFCPath,
                                                         feature_service_item['description'],
                                                         feature_service_item['tags'],
                                                         feature_service_item['summary'],
                                                         feature_service_item['credits'],
                                                         pointLayer,
                                                         feature_service_share_settings,
                                                         currMap,
                                                         parameters[3].value,
                                                         parameters[4].valueAsText,
                                                         featureServiceName)
            if not publish_fc_response['success']:
                arcpy.AddError(publish_fc_response['message'])
                print(publish_fc_response['message'])
                # closeLog(log)
                return
            point_service_url = publish_fc_response['serviceurl']
            arcpy.AddMessage("Published Exposure Points.")
            print("Published Exposure Points.")
            #Add attachments if option is checked
            if parameters[5].enabled and parameters[5].value:
                arcpy.AddMessage("Enabling attachments")
                #Enabling attachments on the feature service
                updateResponse = oitools.updateFeatureDefinition(publish_fc_response['itemId'], {'hasAttachments': True})
                arcpy.AddMessage("Attaching images..")
                print("Attaching images..")
                #Attaching images to the feature service
                oitools.addAttachmentsWithRetry(pointFCPath, publish_fc_response['itemId'], None)
                print('Updating image paths')
                #Updating image paths for the rows with attachments to FA
                oitools.updateImagePaths(publish_fc_response['itemId'], None)


            vtpk_item = [item for item in items if item['type'] == "Vector Tile Package"][0]
            vtpk_item_share_settings = vtpk_item['shared_with']
            print(vtpkFilePath)
            if os.path.isfile(vtpkFilePath):
                arcpy.AddMessage("Uploading Coverage Map..")
                print("Uploading Coverage Map..")
                if oic_file['properties']['OverviewURL']:
                    vectorTileServiceName =  getServiceNameFromOICJson(oic_file, 'VectorTileServer')
                else:
                    vectorTileServiceName = vtpkFileName
                    vectorTileServiceNameAvailable = isServiceNameAvailable(vectorTileServiceName, None, 'Vector Tile Service')
                    if not vectorTileServiceNameAvailable:
                        vectorTileServiceName = '{}_{}'.format(vectorTileServiceName, getCurrentTimeStampStr())
                add_portal_item_response = feature_service_util.add_portal_item(
                                                                                {"snippet": vtpk_item['summary'],
                                                                                 "title": vectorTileServiceName,
                                                                                 "accessInformation": vtpk_item['credits'],
                                                                                 "tags": vtpk_item['tags'],
                                                                                 "description": vtpk_item['description']},
                                                                                 vtpkFilePath, folder_id=folder_id)
                if not add_portal_item_response.get('success'):
                    arcpy.AddError(add_portal_item_response['message'])
                    print(add_portal_item_response['message'])
                    # closeLog(log)
                    return
                print("Uploaded Coverage Map")
                share_response = feature_service_util.share_portal_item(portalurl, user_name,
                                                      add_portal_item_response.get('item_id'),
                                                      share_with_everyone=vtpk_item_share_settings['everyone'],
                                                      share_with_org=vtpk_item_share_settings['org'],
                                                      groups=vtpk_item_share_settings['groups'])
                print("Shared Coverage Map")
                vector_tile_item = [item for item in items if item['type'] == "Vector Tile Service"][0]
                vector_tile_item_share_settings = vector_tile_item['shared_with']
                arcpy.AddMessage("Publishing Coverage Map..")
                print("Publishing Coverage Map..")
                publish_vtpk_response = feature_service_util.publish_vtpk_item(
                                                                               add_portal_item_response['item_id'],
                                                                               vectorTileServiceName, folder_id)
                if not publish_vtpk_response.get('success'):
                    arcpy.AddError(publish_vtpk_response['message'])
                    print(publish_vtpk_response['message'])
                    # closeLog(log)
                    return
                print(publish_vtpk_response)
                share_response = feature_service_util.share_portal_item(
                    portalurl,
                    user_name,
                    publish_vtpk_response['item_id'],
                    share_with_everyone=vector_tile_item_share_settings['everyone'],
                    share_with_org=vector_tile_item_share_settings['org'],
                    groups=vector_tile_item_share_settings['groups'])
                polygon_service_url = publish_vtpk_response['serviceurl']
            arcpy.AddMessage("Published the Coverage Map.")
            print("Published the Coverage Map.")
            if oic_file:
                oic_file['properties']['ServiceURL'] = point_service_url
                oic_file['properties']['OverviewURL'] = polygon_service_url
        oic_file['properties']['Tags'] = parameters[1].valueAsText
        oic_file['properties']['Description'] = parameters[2].valueAsText
        with open(oicFilePath, 'w') as f:
            json.dump(oic_file, f)
        oic_file['properties']['PointsSource'] = ""
        oic_file['properties']['CoverageSource'] = ""
        oic_summary = "Oriented Imagery Catalog: "+os.path.basename(oicFileName)+" created using the Oriented Imagery Catalog tool for ArcGIS Pro."
        oic_item = feature_service_util.get_item(oicFileName, "Oriented Imagery Catalog", user_name)
        if parameters[4].valueAsText == 'Publish Oriented Imagery Catalog item only' or parameters[4].valueAsText == 'Publish all':
            if oic_item:
                arcpy.AddError("The Oriented Imagery Catalog "+ oicFileName + " already exists.")
                print("The Oriented Imagery Catalog "+ oicFileName + " already exists.")
                # closeLog(log)
                return
        if parameters[4].valueAsText == 'Publish Oriented Imagery Catalog item only - overwrite' or parameters[4].valueAsText == 'Publish all - overwrite':
            if oic_item:
                arcpy.AddMessage('Updating Oriented Imagery Catalog')
                print('Updating Oriented Imagery Catalog')
                update_oic_response = feature_service_util.update_portal_item(oic_item.get('id'),
                                                                              {"tags": oicTags,
                                                                              "description": serviceDescription
                                                                              },
                                                                              data=json.dumps(oic_file))
                move_response = feature_service_util.move_items(folder_id, [oic_item.get('id')])
                if not update_oic_response.get('success'):
                    arcpy.AddError('Could not update OIC file!')
                    print('Could not update OIC file!')
                # closeLog(log)
                return
        oic_summary = "Oriented Imagery Catalog: "+oicFileName+" created using the Oriented Imagery Catalog tool for ArcGIS Pro."
        arcpy.AddMessage("Finalizing Oriented Imagery Catalog..")
        add_oic_response = feature_service_util.add_portal_item(
                                             {"snippet": oic_summary,
                                              "title": oicFileName,
                                              "accessInformation": serviceCredits,
                                              "tags": oicTags,
                                              "type": "Oriented Imagery Catalog",
                                              "description": serviceDescription},
                                              data=json.dumps(oic_file), folder_id=folder_id)
        if not add_oic_response.get('success'):
            arcpy.AddError(add_oic_response['message'])
            print(add_oic_response['message'])
        share_response = feature_service_util.share_portal_item(portalurl, user_name,
                                                                add_oic_response['item_id'],
                                                                False, True)
    except:
        e = sys.exc_info()[1]
        arcpy.AddError(e.args[0])
        print(e.args[0])

def returnParametersAsJson(parValues):
    parValuesj = {}
    if parValues:
        for keyValueList in parValues:
            aKey = keyValueList[0]
            aVal = keyValueList[1]
            parValuesj[aKey] = aVal
    return parValuesj

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

def addImagesToOIC(params, defValues, isInputOICFile):
    defValues = {'ImageryType': 'Terrestrial 360 Camera', 'OIType': 'Bubble', 'CamHeading': '0', 'CamPitch': '90', 'CamRoll': '0', 'HFOV': '360', 'VFOV': '180', 'AvgHtAG': '2.5', 'NearDist': '0', 'FarDist': '30', 'MaxDistance': '50', 'ImgRot': None}
    isInputOICFile = True


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
    else:                                                #TBD
        oicFileName = params['inputOIC'].valueAsText
        with open(oicFileName) as oic:
            inputOICJSON = json.load(oic)
            outPath = inputOICJSON['properties']['PointsSource']
    try:
        # lastObjectId = returnLastOID(outPath)
        count = int(arcpy.GetCount_management(featureClass)[0])
        if not count:
            lastObjectId = 0
        else:
            lastObjectId = arcpy.da.SearchCursor(featureClass, "OBJECTID", sql_clause = (None, "ORDER BY OBJECTID DESC")).next()[0]

        addedFields = addMissingFields(outPath,['All'])
    except Exception as e:
        arcpy.AddMessage(str(e))
        arcpy.AddMessage(type(e))
    if params['dem'].valueAsText:
        updateDEM(oicFileName, params['dem'].valueAsText, params['renderingRule'].enabled, params['renderingRule'].valueAsText)
    customType = params['inputType'].valueAsText
    print('Input type: ' + customType)
    customValues = params['customParameters'].value
    print('Extracting parameters..')
    customValuesAsJson = returnParametersAsJson(customValues)
    print('Extracting input parameters..')
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
    try:
        import oic_types
        typeApp = oic_types.OICType(customType)
        if (typeApp.init()):
            typeApp.run(outPath, customValuesAsJson, inputParams, defValues)
        else:
            arcpy.AddMessage('There was an error running the {} tool.',format(customType))
            print('There was an error running the {} tool.',format(customType))
        ###########################################################
        fieldNames = [fieldName for fieldName in addedFields]
        doNotDeleteFieldNames = []
        if fieldNames:
            searchCursor = arcpy.da.SearchCursor(outPath, fieldNames, "OBJECTID > {}".format(lastObjectId))
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
                arcpy.DeleteField_management(outPath, deleteFieldNames)
        ####################################################
    except Exception as errormsg:
        arcpy.AddMessage("Call OIC Types:"+str(errormsg))
        print("Call OIC Types:"+str(errormsg))

    arcpy.AddXY_management(featureClass)

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
#################################################################

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

#################################################################

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
    with open(expanduser('~/testtest.txt'), 'w') as tt:
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

def importExifDataFromImages(inputTable, imgList, outsrs, valueDefaults, log=None):
    nameFldChk = arcpy.ListFields(inputTable,'Name')
    if len(nameFldChk) == 1:
        #importFields = ['SHAPE@','Name','Point','Image','AcquisitionDate','CamHeading','CamPitch','CamRoll','HFOV','VFOV','AvgHtAG','FarDist','NearDist','OIType','Order_','CamOffset','Accuracy','ImgPyramids','DepthImg','CamOri']
        importFields = ['SHAPE@','Name','Image','AcquisitionDate','CamHeading','CamPitch','CamRoll','HFOV','VFOV','AvgHtAG','FarDist','NearDist','OIType','SortOrder','CamOffset','Accuracy','ImgPyramids','DepthImg','CamOri','ImgRot']
    else:
        #importFields = ['SHAPE@','Point','Image','AcquisitionDate','CamHeading','CamPitch','CamRoll','HFOV','VFOV','AvgHtAG','FarDist','NearDist','OIType','Order_','CamOffset','Accuracy','ImgPyramids','DepthImg','CamOri']
        importFields = ['SHAPE@','Image','AcquisitionDate','CamHeading','CamPitch','CamRoll','HFOV','VFOV','AvgHtAG','FarDist','NearDist','OIType','SortOrder','CamOffset','Accuracy','ImgPyramids','DepthImg','CamOri','ImgRot']

    fcCursor = arcpy.da.InsertCursor(inputTable,importFields)
    imgList = natsorted([img.replace(' ','%20') for img in imgList if img])
    print('imgList: ', imgList)
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
                        print(str(errMsg))
                    else:
                        arcpy.AddWarning("Incomplete EXIF data. Could not add image: "+os.path.basename(img))
                        print("Incomplete EXIF data. Could not add image: {}".format(os.path.basename(img)))
                else:
                    yCoord, xCoord = get_lat_lon(exif_data)
                    if yCoord == xCoord == None:
                        arcpy.AddWarning("Could not extract coordinate info to add image: "+os.path.basename(img))
                        print("Could not extract coordinate info to add image: {}".format(os.path.basename(img)))
                        continue
                    else:

                        if cntr == cntrCut:
                            arcpy.AddMessage('Extracted Data for '+str(imgCntr)+' of '+str(imgCount))
                            print("Extracted Data for {} of {}".format(str(imgCntr), str(imgCount)))
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
                        order = imgCntr #imgList.index(img)
                        # print('order: ',order)
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
                        print('Inserted row for: {}'.format(img))

    del fcCursor

# def main(imageListLocation):
#     os.chdir(r'C:\Image_Mgmt_Workflows\OrientedImagery\GPTool')
#     outSrs = "PROJCS['WGS_1984_Web_Mercator_Auxiliary_Sphere',GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Mercator_Auxiliary_Sphere'],PARAMETER['False_Easting',0.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',0.0],PARAMETER['Standard_Parallel_1',0.0],PARAMETER['Auxiliary_Sphere_Type',0.0],UNIT['Meter',1.0]]"
#     outGDB = r"~\Documents\ArcGIS\Projects\MyProject35\MyProject35.gdb"
#     outOICBaseName = 'tst' + str(randint(0,10000))

#     ##############################################################
#     outGDBFolderLocation = os.path.dirname(outGDB)
#     outGDBFolderName = os.path.dirname(outGDB)
#     oicPointFC = str(Path(outGDB) / '{}_ExposurePoints'.format(outOICBaseName))

#     oicCovFC = str(Path(outGDB) / '{}_CoverageMap'.format(outOICBaseName))

#     ptTemplate = os.path.join(os.path.dirname(os.path.realpath(__file__)),'ExposurePoints.lpkx')
#     polyTemplate = os.path.join(os.path.dirname(os.path.realpath(__file__)),'CoverageMap.lpkx')

#     arcpy.AddMessage('Creating point and polygon feature classes..')

#     arcpy.CreateFeatureclass_management(outGDB,outOICBaseName+'_ExposurePoints',"POINT",'#',"DISABLED","DISABLED",outSrs)
#     # addInitialFields(os.path.join(outGDB, '{}_ExposurePoints'.format(outOICBaseName)))
#     featureClass = os.path.join(outGDB, '{}_ExposurePoints'.format(outOICBaseName))
#     fieldDefinitions = []
#     fieldDefinitions.append({'fieldType': 'TEXT', 'fieldLength': '100', 'fieldName': 'Name'})
#     fieldDefinitions.append({'fieldType': 'TEXT', 'fieldLength': '1000', 'fieldName': 'Image'})
#     for fieldDef in fieldDefinitions:
#         fieldList = arcpy.ListFields(featureClass, fieldDef['fieldName'])
#         if not fieldList:
#             arcpy.AddField_management(featureClass, fieldDef['fieldName'], fieldDef['fieldType'],
#                                       fieldDef.get('fieldPrecision', '#'), fieldDef.get('fieldScale', '#'),
#                                       fieldDef.get('fieldLength', '#'), fieldDef['fieldName'])
#     ################################################################################
#     arcpy.CreateFeatureclass_management(outGDB,outOICBaseName+'_CoverageMap',"POLYGON",polyTemplate,"DISABLED","DISABLED",outSrs)

#     oicTemplateFile = os.path.join(os.path.dirname(os.path.realpath(__file__)),'OIC_Template.json')
#     grpJsonFile = os.path.join(outGDBFolderLocation,outOICBaseName+'.OIC')

#     with open(oicTemplateFile) as oicTFile:
#         oicDict = json.load(oicTFile)

#     oicDict["properties"]["Name"] =  outOICBaseName
#     oicDict["properties"]["PointsSource"] = oicPointFC
#     oicDict["properties"]["CoverageSource"] = oicCovFC
#     oicDict["properties"]["Description"] = ""
#     oicDict["properties"]["Tags"] = ""
#     oicDict["properties"]["Copyright"]["text"] = ""

#     with open(grpJsonFile, 'w') as outfile:
#         json.dump(oicDict, outfile)

#     currProj = arcpy.mp.ArcGISProject(expanduser(r"~\Documents\ArcGIS\Projects\MyProject35\MyProject35.aprx"))
#     # loadOIC(grpJsonFile, None)
#     # if not currentProject:
#     currentProject = arcpy.mp.ArcGISProject(expanduser(r"~\Documents\ArcGIS\Projects\MyProject35\MyProject35.aprx"))
#     oicpath = grpJsonFile
#     activeMap = currentProject.listMaps()[0] #.activeMap
#     groupLyrTemplate = os.path.join(os.path.dirname(os.path.realpath(__file__)),'OrientedImageryGroup.lyrx')

#     with open(oicpath) as oicTFile:
#         oicDict = json.load(oicTFile)

#     oicPointFC = oicDict["properties"]["PointsSource"]

#     if oicPointFC.startswith('\\'):
#         pass
#     elif ':' in oicPointFC:
#         pass
#     elif '.gdb' in oicPointFC.split('\\')[0]:
#         oicPointFC = os.path.join(os.path.dirname(oicpath),oicPointFC)

#     oicCovFC = oicDict["properties"]["CoverageSource"]
#     if oicCovFC.startswith('\\'):
#         pass
#     elif ':' in oicCovFC:
#         pass
#     elif '.gdb' in oicCovFC.split('\\')[0]:
#         oicCovFC = os.path.join(os.path.dirname(oicpath),oicCovFC)

#     oicCatName = oicDict["properties"]["Name"]

#     aGrpLayer = arcpy.mp.LayerFile(groupLyrTemplate)
#     activeMap.addLayer(aGrpLayer,'TOP')

#     oiGroupLayer = activeMap.listLayers('*')[0]

#     oicPointLyr = activeMap.addDataFromPath (oicPointFC)
#     oicPointLyr.name = "Exposure Points"
#     oicCovLyr = activeMap.addDataFromPath (oicCovFC)
#     oicCovLyr.name =  'Coverage Map'

#     ptsym = oicPointLyr.symbology
#     cirSymList = ptsym.renderer.symbol.listSymbolsFromGallery('Circle')
#     for cSym in cirSymList:
#         if '1' in cSym.name:
#             ptsym.renderer.symbol = cSym

#     ptsym.renderer.symbol.color = {'RGB' : [76, 230, 0, 100]}
#     ptsym.renderer.symbol.size = 10
#     oicPointLyr.symbology = ptsym
#     arcpy.AddMessage("Updated Symbology")

#     sym = oicCovLyr.symbology
#     sym.renderer.symbol.color = {'RGB' : [76, 230, 0, 50]}
#     sym.renderer.symbol.outlineColor = {'RGB' : [76, 230, 0, 50]}
#     oicCovLyr.symbology = sym
#     print("Updated Symbology")

#     print("Adding layers to the group.")
#     activeMap.addLayerToGroup(oiGroupLayer,oicPointLyr, 'AUTO_ARRANGE')
#     activeMap.addLayerToGroup(oiGroupLayer,oicCovLyr, 'AUTO_ARRANGE')

#     activeMap.removeLayer(oicPointLyr)
#     activeMap.removeLayer(oicCovLyr)

#     oiGroupLayer.name = oicCatName
#     ##################################################

#     params = {}

#     param = arcpy.Parameter()
#     param.value = grpJsonFile
#     params['inputOIC'] = param

#     param = arcpy.Parameter()
#     param.value = 'ImageList'
#     params['inputType'] = param

#     param = arcpy.Parameter()
#     param.value = imageListLocation
#     params['inputFile'] = param

#     param = arcpy.Parameter()
#     param.value = None
#     params['inputFolder'] = param

#     param = arcpy.Parameter()
#     param.value = None
#     params['fileFilter'] = param

#     param = arcpy.Parameter()
#     param.value = None
#     params['dem'] = param

#     param = arcpy.Parameter()
#     param.value = None
#     params['renderingRule'] = param

#     param = arcpy.Parameter()
#     param.value = None
#     params['customParameters'] = param

#     param = arcpy.Parameter()
#     param.value = 'Terrestrial 360 Camera'
#     params['imageryType'] = param

#     param = arcpy.Parameter()
#     param.value = 'Bubble'
#     params['OIType'] = param

#     param = arcpy.Parameter()
#     param.value = 0
#     params['CamHeading'] = param

#     param = arcpy.Parameter()
#     param.value = 90
#     params['CamPitch'] = param

#     param = arcpy.Parameter()
#     param.value = 0
#     params['CamRoll'] = param

#     param = arcpy.Parameter()
#     param.value = 360
#     params['HFOV'] = param

#     param = arcpy.Parameter()
#     param.value = 180
#     params['VFOV'] = param

#     param = arcpy.Parameter()
#     param.value = 2.5
#     params['AvgHtAG'] = param

#     param = arcpy.Parameter()
#     param.value = 0
#     params['NearDist'] = param

#     param = arcpy.Parameter()
#     param.value = 30
#     params['FarDist'] = param

#     param = arcpy.Parameter()
#     param.value = 50
#     params['MaxDistance'] = param

#     param = arcpy.Parameter()
#     param.value = None
#     params['ImgRot'] = param
#     addImagesToOIC(params, {'ImageryType': 'Terrestrial 360 Camera', 'OIType': 'Bubble', 'CamHeading': '0', 'CamPitch': '90', 'CamRoll': '0', 'HFOV': '360', 'VFOV': '180', 'AvgHtAG': '2.5', 'NearDist': '0', 'FarDist': '30', 'MaxDistance': '50', 'ImgRot': None}, True)      # Next up
    
#     parameters = [arcpy.Parameter(), arcpy.Parameter()]
#     parameters[0].value = grpJsonFile
#     parameters[1].value = "Buffer each exposure point"
#     CreateCoverageFeatures(parameters)

#     parameters = [arcpy.Parameter()]
#     parameters[0].value = grpJsonFile
#     coverageLyr = CreateCoverageMap(parameters)

#     # inputOIC = arcpy.Parameter(
#     #     displayName = "Oriented Imagery Catalog",
#     #     name = "inputOIC",
#     #     datatype=["DEFile", "GPGroupLayer"],
#     #     parameterType = "Required",
#     #     direction = "Input"
#     # )

#     # tags = arcpy.Parameter(
#     #     displayName="Tags",
#     #     name="tags",
#     #     datatype="GPString",
#     #     parameterType="Required",
#     #     direction="Input"
#     # )

#     # description = arcpy.Parameter(
#     #     displayName="Description",
#     #     name="description",
#     #     datatype="GPString",
#     #     parameterType="Required",
#     #     direction="Input"
#     # )

#     # portal_folder_name = arcpy.Parameter(
#     #         displayName="Portal folder name:",
#     #     name="portal_folder_name",
#     #     datatype= 'GPString',
#     #     parameterType="Optional",
#     #     direction='Input')

#     # publish_values = ['Publish all', 'Publish all - overwrite', 'Publish Oriented Imagery Catalog item only',
#     #                    'Publish Oriented Imagery Catalog item only - overwrite']
#     # publish_options = arcpy.Parameter(
#     #     displayName="Publish options :",
#     #     name="publish_options",
#     #     datatype="GPString",
#     #     parameterType="Required",
#     #     direction="Input")
#     # publish_options.filter.type = "ValueList"
#     # publish_options.filter.list = publish_values
#     # publish_options.value = publish_values[0]

#     # attachData = arcpy.Parameter(
#     #     displayName="Add images as attachments",
#     #     name="attachData",
#     #     datatype='GPBoolean',
#     #     parameterType="Optional",
#     #     direction="Input")
#     # attachData.enabled = False
#     # attachData.value = False

#     # parameters = [inputOIC, tags, description, portal_folder_name, publish_options, attachData]
#     parameters = [arcpy.Parameter(), arcpy.Parameter(), arcpy.Parameter(), arcpy.Parameter(), arcpy.Parameter(), arcpy.Parameter()]
#     parameters[0].value = grpJsonFile
#     parameters[1].value = 'oic,test'
#     parameters[2].value = 'Just a test'
#     parameters[3].value = None
#     parameters[4].value = 'Publish all'
#     parameters[5].value = None
#     PublishOrientedImageCatalog(parameters, coverageLyr)

def createTmpServerList(prefix, csv):
    with open(expanduser('~/tmp_serverlist.txt'), 'w') as f:
        try:
            with open(csv, 'r') as f2:
                for r2 in [r.split(',')[0] for r in f2.readlines()][1:]:
                    f.write(prefix + r2 + '\n')
        except:
            for r2 in glob(imgRoot+'/*/*/*/*/*/*.jpg'):
                f.write(prefix + basename(r2) + '\n')
            pass

if __name__ == '__main__':
    if len(sys.argv) >= 3:
        prefix = sys.argv[1]
        imgRoot = sys.argv[2]
    else:
        prefix = 'https://dord.mynetgear.com/'
        imgRoot = r'~\Desktop\tmp\Essex Crescent' #r'~\Desktop\WingHong' #'D:/MMS'

    if prefix[-1] not in ('/', '\\'):
        prefix += '/'
    
    csv = ', '.join([basename(x[:-8]) for x in glob(imgRoot + '/*/Imagery')]) + '.csv'
    createTmpServerList(prefix, imgRoot+'/'+csv)
    # main(expanduser('~/tmp_serverlist.txt'))






    imageListLocation = expanduser('~/tmp_serverlist.txt')

    os.chdir(r'C:\Image_Mgmt_Workflows\OrientedImagery\GPTool')
    outSrs = "PROJCS['WGS_1984_Web_Mercator_Auxiliary_Sphere',GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Mercator_Auxiliary_Sphere'],PARAMETER['False_Easting',0.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',0.0],PARAMETER['Standard_Parallel_1',0.0],PARAMETER['Auxiliary_Sphere_Type',0.0],UNIT['Meter',1.0]]"
    outGDB = expanduser(r"~\Documents\ArcGIS\Projects\MyProject35\MyProject35.gdb")
    outOICBaseName = basename(imgRoot).replace(' ', '_') + str(randint(0,10000))


    #########################################################################
    arcpy.env.workspace = outGDB
    for x in arcpy.ListFeatureClasses():
        arcpy.management.DeleteFeatures(x)
    #########################################################################


    outGDBFolderLocation = os.path.dirname(outGDB)
    outGDBFolderName = os.path.dirname(outGDB)
    oicPointFC = str(Path(outGDB) / '{}_ExposurePoints'.format(outOICBaseName))

    oicCovFC = str(Path(outGDB) / '{}_CoverageMap'.format(outOICBaseName))

    ptTemplate = os.path.join(os.path.dirname(os.path.realpath(__file__)),'ExposurePoints.lpkx')
    polyTemplate = os.path.join(os.path.dirname(os.path.realpath(__file__)),'CoverageMap.lpkx')

    arcpy.AddMessage('Creating point and polygon feature classes..')

    arcpy.CreateFeatureclass_management(outGDB,outOICBaseName+'_ExposurePoints',"POINT",'#',"DISABLED","DISABLED",outSrs)
    # addInitialFields(os.path.join(outGDB, '{}_ExposurePoints'.format(outOICBaseName)))
    featureClass = os.path.join(outGDB, '{}_ExposurePoints'.format(outOICBaseName))
    fieldDefinitions = []
    fieldDefinitions.append({'fieldType': 'TEXT', 'fieldLength': '100', 'fieldName': 'Name'})
    fieldDefinitions.append({'fieldType': 'TEXT', 'fieldLength': '1000', 'fieldName': 'Image'})
    for fieldDef in fieldDefinitions:
        fieldList = arcpy.ListFields(featureClass, fieldDef['fieldName'])
        if not fieldList:
            arcpy.AddField_management(featureClass, fieldDef['fieldName'], fieldDef['fieldType'],
                                      fieldDef.get('fieldPrecision', '#'), fieldDef.get('fieldScale', '#'),
                                      fieldDef.get('fieldLength', '#'), fieldDef['fieldName'])
    ################################################################################
    arcpy.CreateFeatureclass_management(outGDB,outOICBaseName+'_CoverageMap',"POLYGON",polyTemplate,"DISABLED","DISABLED",outSrs)

    oicTemplateFile = os.path.join(os.path.dirname(os.path.realpath(__file__)),'OIC_Template.json')
    grpJsonFile = os.path.join(outGDBFolderLocation,outOICBaseName+'.OIC')

    with open(oicTemplateFile) as oicTFile:
        oicDict = json.load(oicTFile)

    oicDict["properties"]["Name"] =  outOICBaseName
    oicDict["properties"]["PointsSource"] = oicPointFC
    oicDict["properties"]["CoverageSource"] = oicCovFC
    oicDict["properties"]["Description"] = ""
    oicDict["properties"]["Tags"] = ""
    oicDict["properties"]["Copyright"]["text"] = ""

    with open(grpJsonFile, 'w') as outfile:
        json.dump(oicDict, outfile)

    currProj = arcpy.mp.ArcGISProject(expanduser(r"~\Documents\ArcGIS\Projects\MyProject35\MyProject35.aprx"))
    # loadOIC(grpJsonFile, None)
    # if not currentProject:
    currentProject = arcpy.mp.ArcGISProject(expanduser(r"~\Documents\ArcGIS\Projects\MyProject35\MyProject35.aprx"))
    oicpath = grpJsonFile
    activeMap = currentProject.listMaps()[0] #.activeMap
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

    ptsym = oicPointLyr.symbology
    cirSymList = ptsym.renderer.symbol.listSymbolsFromGallery('Circle')
    for cSym in cirSymList:
        if '1' in cSym.name:
            ptsym.renderer.symbol = cSym

    ptsym.renderer.symbol.color = {'RGB' : [76, 230, 0, 100]}
    ptsym.renderer.symbol.size = 10
    oicPointLyr.symbology = ptsym
    arcpy.AddMessage("Updated Symbology")

    sym = oicCovLyr.symbology
    sym.renderer.symbol.color = {'RGB' : [76, 230, 0, 50]}
    sym.renderer.symbol.outlineColor = {'RGB' : [76, 230, 0, 50]}
    oicCovLyr.symbology = sym
    print("Updated Symbology")

    print("Adding layers to the group.")
    activeMap.addLayerToGroup(oiGroupLayer,oicPointLyr, 'AUTO_ARRANGE')
    activeMap.addLayerToGroup(oiGroupLayer,oicCovLyr, 'AUTO_ARRANGE')

    activeMap.removeLayer(oicPointLyr)
    activeMap.removeLayer(oicCovLyr)

    oiGroupLayer.name = oicCatName
    ##################################################

    params = {}

    param = arcpy.Parameter()
    param.value = grpJsonFile
    params['inputOIC'] = param

    param = arcpy.Parameter()
    param.value = 'ImageList'
    params['inputType'] = param

    param = arcpy.Parameter()
    param.value = imageListLocation
    params['inputFile'] = param

    param = arcpy.Parameter()
    param.value = None
    params['inputFolder'] = param

    param = arcpy.Parameter()
    param.value = None
    params['fileFilter'] = param

    param = arcpy.Parameter()
    param.value = None
    params['dem'] = param

    param = arcpy.Parameter()
    param.value = None
    params['renderingRule'] = param

    param = arcpy.Parameter()
    param.value = None
    params['customParameters'] = param

    param = arcpy.Parameter()
    param.value = 'Terrestrial 360 Camera'
    params['imageryType'] = param

    param = arcpy.Parameter()
    param.value = 'Bubble'
    params['OIType'] = param

    param = arcpy.Parameter()
    param.value = 0
    params['CamHeading'] = param

    param = arcpy.Parameter()
    param.value = 90
    params['CamPitch'] = param

    param = arcpy.Parameter()
    param.value = 0
    params['CamRoll'] = param

    param = arcpy.Parameter()
    param.value = 360
    params['HFOV'] = param

    param = arcpy.Parameter()
    param.value = 180
    params['VFOV'] = param

    param = arcpy.Parameter()
    param.value = 2.5
    params['AvgHtAG'] = param

    param = arcpy.Parameter()
    param.value = 0
    params['NearDist'] = param

    param = arcpy.Parameter()
    param.value = 30
    params['FarDist'] = param

    param = arcpy.Parameter()
    param.value = 50
    params['MaxDistance'] = param

    param = arcpy.Parameter()
    param.value = None
    params['ImgRot'] = param
    addImagesToOIC(params, {'ImageryType': 'Terrestrial 360 Camera', 'OIType': 'Bubble', 'CamHeading': '0', 'CamPitch': '90', 'CamRoll': '0', 'HFOV': '360', 'VFOV': '180', 'AvgHtAG': '2.5', 'NearDist': '0', 'FarDist': '30', 'MaxDistance': '50', 'ImgRot': None}, True)      # Next up
    
    parameters = [arcpy.Parameter(), arcpy.Parameter()]
    parameters[0].value = grpJsonFile
    parameters[1].value = "Buffer each exposure point"
    CreateCoverageFeatures(parameters)

    parameters = [arcpy.Parameter()]
    parameters[0].value = grpJsonFile
    coverageLyr = CreateCoverageMap(parameters)

    # inputOIC = arcpy.Parameter(
    #     displayName = "Oriented Imagery Catalog",
    #     name = "inputOIC",
    #     datatype=["DEFile", "GPGroupLayer"],
    #     parameterType = "Required",
    #     direction = "Input"
    # )

    # tags = arcpy.Parameter(
    #     displayName="Tags",
    #     name="tags",
    #     datatype="GPString",
    #     parameterType="Required",
    #     direction="Input"
    # )

    # description = arcpy.Parameter(
    #     displayName="Description",
    #     name="description",
    #     datatype="GPString",
    #     parameterType="Required",
    #     direction="Input"
    # )

    # portal_folder_name = arcpy.Parameter(
    #         displayName="Portal folder name:",
    #     name="portal_folder_name",
    #     datatype= 'GPString',
    #     parameterType="Optional",
    #     direction='Input')

    # publish_values = ['Publish all', 'Publish all - overwrite', 'Publish Oriented Imagery Catalog item only',
    #                    'Publish Oriented Imagery Catalog item only - overwrite']
    # publish_options = arcpy.Parameter(
    #     displayName="Publish options :",
    #     name="publish_options",
    #     datatype="GPString",
    #     parameterType="Required",
    #     direction="Input")
    # publish_options.filter.type = "ValueList"
    # publish_options.filter.list = publish_values
    # publish_options.value = publish_values[0]

    # attachData = arcpy.Parameter(
    #     displayName="Add images as attachments",
    #     name="attachData",
    #     datatype='GPBoolean',
    #     parameterType="Optional",
    #     direction="Input")
    # attachData.enabled = False
    # attachData.value = False

    # parameters = [inputOIC, tags, description, portal_folder_name, publish_options, attachData]
    parameters = [arcpy.Parameter(), arcpy.Parameter(), arcpy.Parameter(), arcpy.Parameter(), arcpy.Parameter(), arcpy.Parameter()]
    parameters[0].value = grpJsonFile
    parameters[1].value = 'oic,test'
    parameters[2].value = 'Just a test'
    parameters[3].value = None
    parameters[4].value = 'Publish all'
    parameters[5].value = None
    PublishOrientedImageCatalog(parameters, coverageLyr)