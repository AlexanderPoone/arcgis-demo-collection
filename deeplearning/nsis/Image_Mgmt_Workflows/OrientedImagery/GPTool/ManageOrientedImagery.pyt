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
# Description: This is a utility program which is used to upload feature services to portal.
# Version: 2.3
# Date Created : 20181009
# Date updated : 20200305
# Requirements: ArcGIS Pro 2.2.4
# Author: Esri Imagery Workflows team
#------------------------------------------------------------------------------


import os
import json
import arcpy
import requests
import xml.etree.ElementTree as ET
import orientedimagerytools as oitools
import_folder = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(import_folder)
solutionlog = os.path.join(import_folder,"Scripts","SolutionsLog")
sys.path.append(solutionlog)
programcheck = os.path.join(import_folder,"Scripts")
sys.path.append(programcheck)
import logger
from ProgramCheckAndUpdate import ProgramCheckAndUpdate
import feature_service
from feature_service import FeatureServiceUtil
from arcgis.gis import GIS
requests.packages.urllib3.disable_warnings()

ORDependent_path = os.path.dirname(os.path.realpath(__file__))
ORDependent_path = os.path.join(os.path.dirname(ORDependent_path), "Dependents\\OptimizeRasters")
sys.path.append(ORDependent_path)
import OptimizeRasters

AzureRoot = '.OptimizeRasters/Microsoft'
GoogleRoot = '.OptimizeRasters/Google'
AwsRoot = '.aws'
propertiesAsList = []
propertiesAsjSon = ""

def initializeLog(toolName):
    log = logger.Logger()
    log_output_folder = os.path.join(import_folder, 'logs')
    log.SetLogFolder(log_output_folder)
    log.Project(toolName)
    log.LogNamePrefix(toolName)
    log.StartLog()
    return log

def initializeVersionCheck(log):
    log.CreateCategory('VersionCheck')
    versionCheck = ProgramCheckAndUpdate()
    log.Message('Checking for updates..', logger.Logger.const_general_text)
    verMessage = versionCheck.run(programcheck)
    if(verMessage is not None):
        log.Message(verMessage, logger.Logger.const_warning_text)
        arcpy.AddMessage(verMessage)
    log.CloseCategory()

def closeLog(log):
    log.Message("Done", log.const_general_text)
    log.WriteLog('#all')

def displaySelectByLayerWarning(aMsg):
    installInfo = arcpy.GetInstallInfo()
    instVer = installInfo.get('Version')

    if instVer.startswith('2.3'):
        arcpy.AddWarning('A bug in ArcGIS Pro version 2.3+ prevents custom toolboxes to make selections to feature layers. This tool has been affected by this bug and unable to fulfil its purpose.')

        if aMsg != '':
            arcpy.AddWarning('The operation could not be completed succefully due to the aforementioned bug. Use the following clause to select records records.')
            arcpy.AddMessage(aMsg)

def showCrashWarning(parameters):
    appVersion = arcpy.GetInstallInfo()['Version']
    if not parameters[0].value:
        if appVersion == '2.5' :
            parameters[0].setWarningMessage("A known bug in ArcGIS Pro 2.5 framework triggers a crash if the browse button is clicked. The workaround is to copy and paste the full path to the OIC file in 'Input Oriented Imagery Catalog' field.")
        else:
            parameters[0].clearMessage()
    else:
        parameters[0].clearMessage()

class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "Toolbox"
        self.alias = "ManageOrientedImagery"

        # List of tool classes associated with this toolbox
        self.tools = [CreateOrientedImageCatalog, AddImagesToOrientedImagery, CreateCoverageFeatures, CreateCoverageMap,
                      SelectBrokenPaths, RepairPaths, SelectLocalImages, CopyImagetoWeb, PublishOrientedImageCatalog,
                      CreateReferenceOrientedImageryCatalog, SetExposureStationID, Properties, AnalyseOrientedImageryCatalog,
                      CalculateHeading,AddOrientedImageryFields]


class CreateOrientedImageCatalog(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Create Oriented Imagery Catalog"
        self.description = ""
        self.canRunInBackground = False


    def getParameterInfo(self):
        outputGDB = arcpy.Parameter(
        displayName="Output Geodatabase",
        name="outputLocation",
        datatype= 'DEWorkspace',
        parameterType="Required",
        direction='Input')

        catalogName = arcpy.Parameter(
        displayName="Catalog Name",
        name="catalogName",
        datatype= 'GPString',
        parameterType="Required",
        direction='Output')

        catalogSRS = arcpy.Parameter(
        displayName="Catalog Coordinate System",
        name="catalogSRS",
        datatype="GPCoordinateSystem",
        parameterType="Required",
        direction="Input")

        defaultSRS = arcpy.SpatialReference(3857)
        catalogSRS.value = defaultSRS


        description = arcpy.Parameter(
        displayName="Description",
        name="aDescription",
        datatype="GPString",
        parameterType="Required",
        direction="Input")

        tags = arcpy.Parameter(
        displayName="Tags",
        name="aTag",
        datatype="GPString",
        parameterType="Required",
        direction="Input")

        copyright = arcpy.Parameter(
        displayName="Copyright",
        name="aCopyright",
        datatype="GPString",
        parameterType="Optional",
        direction="Input")


        params = [catalogName,outputGDB,catalogSRS,description,tags,copyright]

        return params


    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        params = self.mapParams(parameters)
        if params['catalogName'].altered:
            if ' ' in params['catalogName'].valueAsText:
                params['catalogName'].value = params['catalogName'].valueAsText.replace(' ','')
        if not params['tags'].altered:
            params['tags'].value = 'OrientedImagery'

    def updateMessages(self, parameters):
        params = self.mapParams(parameters)
        msgsToShow = ""
        if params['outputGDB'].valueAsText and not params['outputGDB'].valueAsText.endswith('.gdb'):
            params['outputGDB'].setErrorMessage("Output Geodatabase needs a be a file Geodatabase. Please select a valid File Geodatabase")
        else:
            params['outputGDB'].clearMessage()

        if params['catalogName'].altered:
            if params['outputGDB'].valueAsText and params['catalogName'].valueAsText :
                outNameChk = arcpy.ValidateTableName(params['catalogName'].valueAsText, params['outputGDB'].valueAsText)

                if outNameChk == '':
                    params['catalogName'].clearMessage()
                else:
                    if outNameChk != params['catalogName'].valueAsText :
                        params['catalogName'].setErrorMessage("Invalid Catalog Name. Suggested name: "+outNameChk)
                    else:
                        params['catalogName'].clearMessage()

    def mapParams(self, parameters):
        params = {
                     'outputGDB': parameters[1],
                     'catalogName': parameters[0],
                     'catalogSRS': parameters[2],
                     'description': parameters[3],
                     'tags': parameters[4],
                     'copyright': parameters[5]
                 }
        return params

    def execute(self,parameters,messages):
        log = initializeLog('CreateOrientedImageryCatalog')
        initializeVersionCheck(log)
        params = self.mapParams(parameters)
        outSrs = params['catalogSRS'].valueAsText
        outGDB = params['outputGDB'].valueAsText
        outOICBaseName = params['catalogName'].valueAsText
        try:
            oitools.createOIC(outSrs, outGDB, outOICBaseName, params, log)
        except Exception as e:
            arcpy.AddError('Error in create oriented imagery catalog.' + str(e))
            log.Message('Error in create oriented imagery catalog. ' + str(e), log.const_critical_text)
        closeLog(log)


class AddImagesToOrientedImagery(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Add Images to Oriented Imagery Catalog"
        self.description = ""
        self.canRunInBackground = False


    def getParameterInfo(self):

        global errorMessage
        errorMessage = None
        global warningMessage
        warningMessage = None

        inputOIC = arcpy.Parameter(
        displayName="Input Oriented Imagery Catalog",
        name="inputOIC",
        datatype=["DEFile", "GPGroupLayer"],
        parameterType="Required",
        direction="Input")

        inputType = arcpy.Parameter(
        displayName="Input Type",
        name="InputType",
        datatype= "GPString",
        parameterType="Optional",
        direction="Input")
        inputType.filter.type = "ValueList"
        inputType.enabled = True

        dem = arcpy.Parameter(
            displayName="DEM:",
            name="DEM",
            datatype='GPString',
            parameterType="Optional",
            direction="Input")
        dem.filter.type = "ValueList"
        dem.filter.list = ['https://elevation3d.arcgis.com/arcgis/rest/services/WorldElevation3D/Terrain3D/ImageServer', 'https://elevation.arcgis.com/arcgis/rest/services/WorldElevation/Terrain/ImageServer']
        dem.enabled = True

        renderingRule = arcpy.Parameter(
            displayName="Rendering Rule:",
            name="RenderingRule",
            datatype='GPString',
            parameterType="Optional",
            direction="Input")
        renderingRule.filter.type = "ValueList"
        renderingRule.enabled = False

        inputFile = arcpy.Parameter(
            displayName="Image List:",
            name="ImageList",
            datatype='DEFile',
            parameterType="Optional",
            direction="Input")
        inputFile.enabled = False
        inputFile.multiValue = True

        inputFolder = arcpy.Parameter(
            displayName="Folder",
            name="Folder",
            datatype='DEFolder',
            parameterType="Optional",
            direction="Input")
        inputFolder.enabled = False

        fileFilter = arcpy.Parameter(
            displayName="File Filter:",
            name="FolderFilter",
            datatype='GPString',
            parameterType="Optional",
            direction="Input")
        fileFilter.enabled = False

        customParameters = arcpy.Parameter(
        displayName='Parmeters:',
        name='CustomParameters',
        datatype='GPValueTable',
        parameterType='Optional',
        direction='Input')
        customParameters.columns = [['GPString', 'Parameter'], ['GPString', 'Value']]
        customParameters.enabled = False

        imageryType = arcpy.Parameter(
                       displayName="Imagery Type:",
                       name="ImageryType",
                       datatype='GPString',
                       parameterType="Required",
                       direction="Input")
        imageryType.enabled = True
        imageryType.filter.type = "ValueList"
        #imageryType.category = 'Default Parameters'

        oiType = arcpy.Parameter(
                displayName="Oriented Imagery Type:",
                name="OIType",
                datatype='GPString',
                parameterType="Optional",
                direction="Input")
        oiType.enabled = False
        oiType.filter.type = "ValueList"
        #oiType.category = 'Default Parameters'

        camHeading = arcpy.Parameter(
                displayName="Camera Heading ",
                name="CamHeading",
                datatype='GPString',
                parameterType="Optional",
                direction="Input")
        camHeading.enabled = False
        #camHeading.category = 'Default Parameters'

        camPitch = arcpy.Parameter(
                displayName="Camera Pitch",
                name="CamPitch",
                datatype='GPString',
                parameterType="Optional",
                direction="Input")
        camPitch.enabled = False
        #camPitch.category = 'Default Parameters'

        camRoll = arcpy.Parameter(
                displayName="Camera Roll",
                name="CamRoll",
                datatype='GPString',
                parameterType="Optional",
                direction="Input")
        camRoll.enabled = False
        #camRoll.category = 'Default Parameters'

        horizontalFieldOfView = arcpy.Parameter(
                displayName="Horizontal Field of View",
                name="HFOV",
                datatype='GPString',
                parameterType="Optional",
                direction="Input")
        horizontalFieldOfView.enabled = False
        #horizontalFieldOfView.category = 'Default Parameters'

        verticalFieldOfView = arcpy.Parameter(
                displayName="Vertical Field of View",
                name="VFOV",
                datatype='GPString',
                parameterType="Optional",
                direction="Input")
        verticalFieldOfView.enabled = False
        #verticalFieldOfView.category = 'Default Parameters'

        averageHeight = arcpy.Parameter(
                displayName="Average Height (m)",
                name="AvgHtAG",
                datatype='GPString',
                parameterType="Optional",
                direction="Input")
        averageHeight.enabled = False
        #averageHeight.category = 'Default Parameters'

        farDistance = arcpy.Parameter(
                displayName="Far Distance",
                name="FarDist",
                datatype='GPString',
                parameterType="Optional",
                direction="Input")
        farDistance.enabled = False
        #farDistance.category = 'Default Parameters'

        nearDistance = arcpy.Parameter(
                displayName="Near Distance",
            name="NearDist",
            datatype='GPString',
            parameterType="Optional",
            direction="Input")
        nearDistance.enabled = False
        #nearDistance.category = 'Default Parameters'

        maxDistance = arcpy.Parameter(
                displayName="Max Distance",
                name="MaxDistance",
                datatype='GPString',
                parameterType="Optional",
                direction="Input")
        maxDistance.enabled = False
        #maxDistance.category = 'Default Parameters'

        imgRot = arcpy.Parameter(
                displayName="Image Rotation",
                name="ImgRot",
                datatype='GPString',
                parameterType="Optional",
                direction="Input")
        imgRot.enabled = False
        #imgRot.category = 'Default Parameters'

        params = [inputOIC, inputType, inputFile, inputFolder, fileFilter, dem, renderingRule, customParameters,
                  imageryType, oiType, camHeading, camPitch, camRoll, horizontalFieldOfView,
                  verticalFieldOfView, averageHeight, nearDistance, farDistance, maxDistance, imgRot]

        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def mapParams(self, parameters):
        return {
                    "inputOIC": parameters[0],
                    "inputType": parameters[1],
                    "inputFile": parameters[2],
                    "inputFolder": parameters[3],
                    "fileFilter": parameters[4],
                    "dem": parameters[5],
                    "renderingRule": parameters[6],
                    "customParameters": parameters[7],
                    "imageryType": parameters[8],
                    "OIType": parameters[9],
                    "CamHeading": parameters[10],
                    "CamPitch": parameters[11],
                    "CamRoll": parameters[12],
                    "HFOV": parameters[13],
                    "VFOV": parameters[14],
                    "AvgHtAG": parameters[15],
                    "NearDist": parameters[16],
                    "FarDist": parameters[17],
                    "MaxDistance": parameters[18],
                    "ImgRot": parameters[19]
               }

    def hasDefaultValues(self, parameters):
        # check if oic file has default parameters set.
        params = self.mapParams(parameters)
        if params['inputOIC'].valueAsText and params['inputOIC'].valueAsText.lower().endswith('.oic'):
            oicFilePath = params['inputOIC'].valueAsText
        else:
            oicFilePath = oitools.getOICFilePath(params)
        if not oicFilePath:
            return False
        with open(oicFilePath) as f:
            oicDict = json.load(f)
        if oicDict['properties']['MaxDistance']:
            return True
        defaults = oicDict["properties"]["DefaultAttributes"]
        for key in defaults:
            if defaults[key]:
                return True
        return False

    def enableInput(self, oicInput, params):
        #Based on OICType, enable file input or folder input with file filter.
        params['inputFile'].enabled = False
        params['inputFolder'].enabled = False
        params['fileFilter'].enabled = False
        params['customParameters'].enabled = False
        if not params['inputFile'].altered:
            params['inputFile'].value = ''
        if not params['inputFolder'].altered:
            params['inputFolder'].value = ''
        if not params['fileFilter'].altered:
            params['fileFilter'].value = ''
        if params['customParameters'].value:
            params['customParameters'].enabled = True
        if oicInput:
            if oicInput['Type'].lower() == 'file':
                params['inputFile'].enabled = True
            elif oicInput['Type'].lower() == 'folder':
                params['inputFolder'].enabled = True
                if oicInput.get('Filters'):
                    params['fileFilter'].enabled = True
                    filters = oicInput['Filters'].split(',')
                    params['fileFilter'].filter.type = "ValueList"
                    params['fileFilter'].filter.list = filters
                    if not params['fileFilter'].altered:
                        params['fileFilter'].value = filters[0]

    def getOIType(self, OITypeShortForm):
        # Gets the OIType from the short form of OIType persisted in the oic file.
        OITypes = {
                      'U': 'Undefined',
                      'T': 'Terrestrial',
                      'O': 'Oblique',
                      'I': 'Inspection',
                      'B': 'Bubble',
                      'P': 'Panorama',
                      'V': 'Video'
                  }
        oiType = OITypes.get(OITypeShortForm) or OITypeShortForm
        return oiType

    def getDEMResponse(self, demURL):
        data = {'f':'json'}
        try:
            res = requests.get(demURL, data, verify=False)
            resJSON = res.json()
        except:
            return {'message':'Not a valid DEM. Currently we support only Image Services.'}
        if resJSON.get('error'):
            if 'token' in resJSON['error']['message'].lower():
                tokenDict = arcpy.GetSigninToken()
                if tokenDict and tokenDict.get('token'):
                    data['token'] = tokenDict['token']
                    try:
                        res = requests.get(demURL, data)
                        resJSON = res.json()
                    except:
                        return {'message':'Not a valid DEM. Currently we support only Image Services.'}
                    if resJSON.get('error'):
                        return {'message':'Error in using this DEM. {}'.format(resJSON['error'].get('message'))}
                    else:
                        return {'message':'', 'response':resJSON}
                else:
                    return {'message':'Please log in to continue using this DEM.'}
            else:
                return {'message':'Error in using this DEM.'}
        else:
            return {'response': resJSON, 'message': ''}

    def setDefaultValues(self, params, oiType, camHeading, camPitch, camRoll, hfov, vfov, avgHtAG, nearDist, farDist, maxDist, imgRot):
        params['CamHeading'].value = camHeading
        params['CamPitch'].value = camPitch
        params['CamRoll'].value = camRoll
        params['HFOV'].value = hfov
        params['VFOV'].value = vfov
        params['AvgHtAG'].value = avgHtAG
        params['NearDist'].value = nearDist
        params['FarDist'].value = farDist
        params['MaxDistance'].value = maxDist
        params['OIType'].value = self.getOIType(oiType)
        params['ImgRot'].value = imgRot

    def setDefaultValuesByType(self, params, imageryTypes, imageryType):
        if imageryTypes.get(imageryType):
            typeDict = imageryTypes[imageryType]
            self.setDefaultValues(params, typeDict['OIType'], typeDict['CamHeading'], typeDict['CamPitch'], typeDict['CamRoll'],
                                  typeDict['HFOV'], typeDict['VFOV'], typeDict['AvgHtAG'], typeDict['NearDist'],
                                  typeDict['FarDist'], typeDict['MaxDist'], typeDict.get('ImgRot'))

    def clearDefaultValues(self, params):
        self.setDefaultValues(params, '', '', '', '', '', '', '', '', '', '', '')

    def updateParameters(self, parameters):
        global errorMessage
        errorMessage = ''
        global warningMessage
        warningMessage = ''
        params = self.mapParams(parameters)
        imageryTypesDict = oitools.getImageryTypesFromCSV()
        imageryTypes = sorted(list(imageryTypesDict.keys()))
        oicImageryTypesDict = {}
        oicImageryTypes = []
        if params['inputOIC'].value:
            if params['inputOIC'].valueAsText.lower().endswith('.oic'):
                oicFilePath = params['inputOIC'].valueAsText
            else:
                oicFilePath = oitools.getOICFilePath(params)
            hasDefaultValues = self.hasDefaultValues(parameters)
            if hasDefaultValues:
                oicImageryTypesDict = oitools.getImageryTypeFromOIC(oicFilePath)
                oicImageryTypes = list(oicImageryTypesDict.keys())
                params['CamHeading'].enabled = True
                params['CamPitch'].enabled = True
                params['CamRoll'].enabled = True
                params['HFOV'].enabled = True
                params['VFOV'].enabled = True
                params['AvgHtAG'].enabled = True
                params['NearDist'].enabled = True
                params['FarDist'].enabled = True
                params['MaxDistance'].enabled = True
                params['ImgRot'].enabled = True

        if not params["inputType"].altered:
            typesList = oitools.returnTypes()
            params["inputType"].filter.list = typesList

        #if params['inputOIC'].value:
        if params["inputType"].value:
            #Added by Randall after removing categories.
            params['CamHeading'].enabled = True
            params['CamPitch'].enabled = True
            params['CamRoll'].enabled = True
            params['HFOV'].enabled = True
            params['VFOV'].enabled = True
            params['AvgHtAG'].enabled = True
            params['NearDist'].enabled = True
            params['FarDist'].enabled = True
            params['MaxDistance'].enabled = True
            params['ImgRot'].enabled = True


        if params["inputType"].altered and not params['inputType'].hasBeenValidated:
            allparas = oitools.returnParameters(params['inputType'].valueAsText)
            oicInput = allparas[0]
            valList = allparas[1]
            if params["customParameters"].value and oitools.getCustomParamKeys(params["customParameters"].value) == oitools.getCustomParamKeys(valList):
                pass
            else:
                params["customParameters"].value = valList
            self.enableInput(oicInput, params)
            inputTypeImageryTypesDict = oitools.getImageryTypesFromInputType(params['inputType'].valueAsText)
            inputTypeImageryTypes = sorted(list(inputTypeImageryTypesDict.keys()))
            imageryTypesDict.update(inputTypeImageryTypesDict)
            imageryTypesDict.update(oicImageryTypesDict)
            imageryTypes = oicImageryTypes + inputTypeImageryTypes + imageryTypes
            params['imageryType'].filter.list = []
            params['imageryType'].value = ''
            self.clearDefaultValues(params)
            if 'LoadedFromOIC' in imageryTypesDict:
                params['imageryType'].value = imageryTypes[0]
                self.setDefaultValuesByType(params, imageryTypesDict, imageryTypes[0])
            params['imageryType'].filter.list = imageryTypes
        if params['imageryType'].altered and not params['imageryType'].hasBeenValidated:
            if params['inputType'].value:
                imageryTypesDict.update(oitools.getImageryTypesFromInputType(params['inputType'].valueAsText))
            imageryTypesDict.update(oicImageryTypesDict)
            self.setDefaultValuesByType(params, imageryTypesDict, params['imageryType'].valueAsText)
        if params["inputOIC"].altered and not params['inputOIC'].hasBeenValidated:
            with open(oicFilePath) as f:
                oicDict = json.load(f)
            if params['inputType'].value:
                inputTypeImageryTypesDict = oitools.getImageryTypesFromInputType(params['inputType'].valueAsText)
                inputTypeImageryTypes = sorted(list(inputTypeImageryTypesDict.keys()))
                imageryTypesDict.update(inputTypeImageryTypesDict)
                imageryTypes = oicImageryTypes + inputTypeImageryTypes + imageryTypes
            else:
                imageryTypes = oicImageryTypes + imageryTypes
            imageryTypesDict.update(oicImageryTypesDict)
            params['imageryType'].filter.list = []
            params['imageryType'].value = ''
            self.clearDefaultValues(params)
            if 'LoadedFromOIC' in imageryTypesDict:
                self.setDefaultValuesByType(params, imageryTypesDict, imageryTypes[0])
                params['imageryType'].value = imageryTypes[0]
            params['imageryType'].filter.list = imageryTypes
            dem = oicDict.get('properties').get('DEMPrefix')
            if dem:
                demParts = dem.split('|')
                if demParts[0] == 'E':
                    params['dem'].value = demParts[1]
                    params['renderingRule'].enabled = False
                elif demParts[0] == 'I':
                    params['dem'].value = demParts[2]
                    if len(demParts) > 3:
                        demDict = self.getDEMResponse(demParts[2])
                        if demDict.get('response'):
                            rasterFunctionInfos = demDict.get('response')['rasterFunctionInfos']
                            if rasterFunctionInfos:
                                params['renderingRule'].enabled = True
                                rasterFunctionNames = []
                                for rasterFunction in rasterFunctionInfos:
                                    rasterFunctionNames.append(rasterFunction.get('name'))
                                if demParts[3] in rasterFunctionNames:
                                    params['renderingRule'].filter.list = rasterFunctionNames
                                    params['renderingRule'].value = demParts[3]
                warningMessage = 'DEM is already set for this catalog. Any change to DEM will update the DEM for existing images as well.'
                return
        if params['dem'].altered and not params['dem'].hasBeenValidated:
            dems = params['dem'].filter.list
            if params['dem'].valueAsText not in dems:
                dems.append(params['dem'].valueAsText)
                params['dem'].filter.list = dems
            demResponseDict = self.getDEMResponse(params['dem'].valueAsText)
            if not demResponseDict.get('response'):
                errorMessage = demResponseDict['message']
                return
            rasterFunctionInfos = demResponseDict.get('response')['rasterFunctionInfos']
            if rasterFunctionInfos:
                params['renderingRule'].enabled = True
                rasterFunctionNames = []
                for rasterFunction in rasterFunctionInfos:
                    rasterFunctionNames.append(rasterFunction.get('name'))
                params['renderingRule'].filter.list = rasterFunctionNames
                params['renderingRule'].value = rasterFunctionNames[0]
            else:
                params['renderingRule'].enabled = False

    def updateMessages(self, parameters):
        global errorMessage
        global warningMessage
        showCrashWarning(parameters)
        hasDefaultValues = self.hasDefaultValues(parameters)
        params = self.mapParams(parameters)
        if hasDefaultValues:
            parameters[8].setWarningMessage('Found default parameters set in the selected Oriented Imagery Catalog. This could be overwritten on editing the below Default Parameters.')
        else:
            parameters[8].clearMessage()
        if errorMessage:
            params['dem'].setErrorMessage(errorMessage)
        else:
            if warningMessage:
                params['dem'].setWarningMessage(warningMessage)
            else:
                params['dem'].clearMessage()

    def execute(self,parameters,messages):
        log = initializeLog('AddImagesToOrientedImagery')
        initializeVersionCheck(log)
        os.environ['GDAL_HTTP_UNSAFESSL']='YES'
        params = self.mapParams(parameters)
        isInputOICFile = False
        try:
            try:
                currProj = arcpy.mp.ArcGISProject("CURRENT")
            except:
                isInputOICFile = True
            if parameters[0].valueAsText.lower().endswith('.oic'):
                isInputOICFile = True
            defaultValues = oitools.getDefaultValues(parameters)
            oitools.addImagesToOIC(params, defaultValues, log, isInputOICFile)
        except Exception as e:
            arcpy.AddError('Error in adding images to oriented imagery catalog ' + str(e))
            log.Message('Error in adding images to oriented imagery catalog ' + str(e), log.const_critical_text)
        closeLog(log)

class CreateCoverageFeatures(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Create Coverage Features"
        self.description = ""
        self.canRunInBackground = False


    def getParameterInfo(self):
        inputOIC = arcpy.Parameter(
        displayName="Input Oriented Imagery Catalog",
        name="inputOIC",
        datatype=["DEFile", "GPGroupLayer"],
        parameterType="Required",
        direction="Input")

        coverageOptions = arcpy.Parameter(
                displayName="Coverage Feature Options:",
                name="coverageOptions",
                datatype='GPString',
                parameterType="Required",
                direction="Input")
        coverageOptions.enabled = True
        coverageOptions.filter.type = "ValueList"
        #coverageOptions.filter.list = ["Build Coverage", "Create Buffer", "Use Exposure Point Extent"]
        coverageOptions.filter.list = ["From each exposure point","From each exposure point and dissolve", "Buffer each exposure point", "From extent of all exposures"]

##        mergeFeatures = arcpy.Parameter(
##                displayName="Merge Coverage Features:",
##                    name="mergeFeatures",
##                    datatype='GPBoolean',
##                    parameterType="Optional",
##                    direction="Input")
##        mergeFeatures.enabled = False
##        mergeFeatures.value = False

        params = [inputOIC,coverageOptions] #,mergeFeatures]

        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        pass


    def updateMessages(self, parameters):
        showCrashWarning(parameters)

    def execute(self,parameters,messages):
        log = initializeLog('CreateCoverageFeatures')
        initializeVersionCheck(log)
        row = None
        isInputOICFile = False
        try:
            try:
                currProj = arcpy.mp.ArcGISProject("CURRENT")
            except:
                isInputOICFile = True
            if parameters[0].valueAsText.lower().endswith('.oic'):
                isInputOICFile = True
            if not isInputOICFile:
                grpLayer = parameters[0].value
                grpLayers = grpLayer.listLayers()

                defprops = {}

                for gLyr in grpLayers:
                    gLyrDec = arcpy.Describe(gLyr)
                    if gLyrDec.shapeType == 'Point':
                        inputFeatureClass = gLyr
                        gLyrsource = gLyrDec.catalogPath
                        gLyrsourceDir = os.path.dirname(os.path.dirname(gLyrsource))
                        oicFilePath = os.path.join(gLyrsourceDir,grpLayer.name+'.oic')
                        try :
                            with open(oicFilePath) as f:
                                oic_file = json.load(f)
                            defprops = oic_file['properties']['DefaultAttributes']

                        except:
                            defprops = {}

                    elif gLyrDec.shapeType == 'Polygon':
                        outputFeatureClass = gLyr
            else:
                oicFilePath = parameters[0].valueAsText
                with open(oicFilePath) as f:
                    oic_file = json.load(f)
                defprops = oic_file['properties']['DefaultAttributes']
                outputFeatureClass = oic_file['properties']['CoverageSource']
                inputFeatureClass = oic_file['properties']['PointsSource']

            #["Calculate Coverage", "Create Buffer", "Use Exposure Point Extent"]
            covCreateOption = parameters[1].valueASText
            covCreateOption = covCreateOption.lower()

            fieldList = arcpy.ListFields(outputFeatureClass,'Name')
            if len(fieldList) == 0:
                arcpy.AddField_management(outputFeatureClass, 'Name', "TEXT", 0, 0, 100, 'Name')

            if ((covCreateOption == "from each exposure point") or (covCreateOption == "from each exposure point and dissolve")):
                iFldNames = ('SHAPE@X','SHAPE@Y','Name','CamHeading','CamPitch','CamRoll','HFOV','VFOV','AvgHtAG','FarDist','NearDist','OIType') #','Image')
                desc = arcpy.Describe(inputFeatureClass)
                fieldNames = [field.name for field in arcpy.ListFields(inputFeatureClass)]
                fieldNames.extend(['SHAPE@X','SHAPE@Y'])

                if hasattr(desc, "layer"):
                    outPath = desc.layer.catalogPath
                    inSearchCursor = arcpy.da.SearchCursor(outPath, fieldNames)
                else:
                    outPath = desc.catalogPath
                    inSearchCursor = arcpy.da.SearchCursor(outPath, fieldNames)
                log.Message("Output feature class path:{}".format(arcpy.Describe(outputFeatureClass).catalogPath), log.const_general_text)
                geometryType = "POLYGON"
                fcSRS = desc.spatialReference


                outFldName = ('SHAPE@','Name')
                outfcCursor = arcpy.da.InsertCursor(outputFeatureClass,outFldName)

                arcpy.SelectLayerByAttribute_management(outputFeatureClass, "NEW_SELECTION",'')

                if int(arcpy.GetCount_management(outputFeatureClass)[0]) > 0:
                    arcpy.DeleteFeatures_management(outputFeatureClass)

                outSRS = srsString = arcpy.Describe(outputFeatureClass).spatialreference
                totalFarDist = 0
                farDistNo = 0

                with inSearchCursor:
                    for index, row in enumerate(inSearchCursor, start=1):
                        errorFound = False
                        inShapeX = row[fieldNames.index('SHAPE@X')]
                        inShapeY = row[fieldNames.index('SHAPE@Y')]
                        try:
                            name = row[fieldNames.index('Name')]
                            if name == None:
                                name = defprops['Name']

                            if 'CamHeading' in fieldNames:
                                camHeading = row[fieldNames.index('CamHeading')]
                            else:
                                camHeading = None
                            if camHeading == None:
                                try:
                                    camHeading = float(defprops['CamHeading'])
                                except:
                                    log.Message('Could not find a value for CamHeading', log.const_warning_text)
                                    arcpy.AddWarning('Could not find a value for CamHeading')
                                    errorFound = True


                            if 'CamPitch' in fieldNames:
                                camPitch = row[fieldNames.index('CamPitch')]
                            else:
                                camPitch = None
                            if camPitch == None:
                                try:
                                    camPitch = float(defprops['CamPitch'])
                                except:
                                    log.Message('Could not find a value for CamPitch', log.const_warning_text)
                                    arcpy.AddWarning('Could not find a value for CamPitch')
                                    errorFound = True

                            if 'CamRoll' in fieldNames:
                                camRoll = row[fieldNames.index('CamRoll')]
                            else:
                                camRoll = None
                            if camRoll == None:
                                try:
                                    camRoll = float(defprops['CamRoll'])
                                except:
                                    log.Message('Could not find a value for CamRoll', log.const_warning_text)
                                    arcpy.AddWarning('Could not find a value for CamRoll')
                                    errorFound = True

                            if 'HFOV' in fieldNames:
                                HFOV = row[fieldNames.index('HFOV')]
                            else:
                                HFOV = None
                            if HFOV == None:
                                try:
                                    HFOV = float(defprops['HFOV'])
                                except:
                                    log.Message('Could not find a value for HFOV', log.const_warning_text)
                                    arcpy.AddWarning('Could not find a value for HFOV')
                                    errorFound = True

                            if 'VFOV' in fieldNames:
                                VFOV = row[fieldNames.index('VFOV')]
                            else:
                                VFOV = None
                            if VFOV == None:
                                try:
                                    VFOV = float(defprops['VFOV'])
                                except:
                                    log.Message('Could not find a value for VFOV', log.const_warning_text)
                                    arcpy.AddWarning('Could not find a value for VFOV')
                                    errorFound = True

                            if 'AvgHtAG' in fieldNames:
                                avgHtAG = row[fieldNames.index('AvgHtAG')]
                            else:
                                avgHtAG = None
                            if avgHtAG == None:
                                try:
                                    avgHtAG = float(defprops['AvgHtAG'])
                                except:
                                    log.Message('Could not find a value for AvgHtAG', log.const_warning_text)
                                    arcpy.AddWarning('Could not find a value for AvgHtAG')
                                    errorFound = True

                            if 'FarDist' in fieldNames:
                                farDist = row[fieldNames.index('FarDist')]
                            else:
                                farDist = None

                            if farDist == None:
                                try:
                                    farDist = float(defprops['FarDist'])
                                    totalFarDist = farDist
                                except:
                                    log.Message('Could not find a value for FarDist', log.const_warning_text)
                                    arcpy.AddWarning('Could not find a value for FarDist')
                                    errorFound = True
                            else:
                                totalFarDist = totalFarDist + farDist
                                farDistNo = farDistNo + 1

                            if 'NearDist' in fieldNames:
                                nearDist = row[fieldNames.index('NearDist')]
                            else:
                                nearDist = None
                            if nearDist == None:
                                try:
                                    nearDist = float(defprops['NearDist'])
                                except:
                                    log.Message('Could not find a value for NearDist', log.const_warning_text)
                                    arcpy.AddWarning('Could not find a value for NearDist')
                                    errorFound = True

                            if 'OIType' in fieldNames:
                                OIType = row[fieldNames.index('OIType')]
                            else:
                                OIType = None
                            if OIType == None:
                                try:
                                    OIType = defprops['OIType']
                                except:
                                    OIType = 'U'

                            #imagePath = row[12]
                            if errorFound == False:
                                covPoly = oitools.returnCoveragePoints(inShapeX,inShapeY,camHeading,camPitch,camRoll,HFOV,VFOV,avgHtAG,farDist,nearDist,OIType,outSRS)
                                outValueList = []
                                outValueList.append(covPoly)
                                outValueList.append(name)

                                outfcCursor.insertRow(outValueList)
                                log.Message('Added row {}'.format(index), log.const_general_text)

                        except arcpy.ExecuteError:
                            arcpy.addErrorMessage(arcpy.GetMessages())

                del row
                del outfcCursor

                if farDistNo > 0:
                    avgFarDist = totalFarDist / farDistNo
                else:
                    avgFarDist = totalFarDist

                simplifyTol = max((avgFarDist/100),1)

                useSimplified = False
                if covCreateOption == "from each exposure point and dissolve":
                    useSimplified = True
                    databasePath = os.path.dirname(arcpy.Describe(outputFeatureClass).catalogPath)
                    mergeName = os.path.join(databasePath,arcpy.CreateUniqueName("Merge",databasePath))
                    #minBoundName = os.path.join(databasePath,arcpy.CreateUniqueName("MinBound",databasePath))

                    try:
##                        arcpy.AddMessage("Computing Minimum Boundary")
##                        arcpy.SelectLayerByAttribute_management(outputFeatureClass, 'New selection',"OBJECTID >= 0")
##
##                        arcpy.MinimumBoundingGeometry_management(outputFeatureClass, minBoundName, "ENVELOPE", "NONE", None, "NO_MBG_FIELDS")
##
##                        arcpy.AddMessage("Merging")
                        arcpy.SelectLayerByAttribute_management(outputFeatureClass, 'New selection',"OBJECTID >= 0")

                        arcpy.Dissolve_management(outputFeatureClass, mergeName, None, None, "MULTI_PART", "UNSPLIT_LINES")


                        if (arcpy.ProductInfo() == 'ArcView'):
                            useSimplified = False
                            pass
                        else:
                            useSimplified = True
                            simplifiedFeatures = os.path.join(databasePath,arcpy.CreateUniqueName("simplifiedFeat",databasePath))
                            arcpy.SimplifyPolygon_cartography(mergeName, simplifiedFeatures, "POINT_REMOVE", simplifyTol)

                        if int(arcpy.GetCount_management(outputFeatureClass)[0]) > 0:
                            arcpy.DeleteFeatures_management(outputFeatureClass)

                        outFldName = ('SHAPE@','Name')
                        outfcCursor = arcpy.da.InsertCursor(outputFeatureClass,outFldName)

                        if useSimplified:

                            mergeFldNames = ('SHAPE@')
                            mergeCursor = arcpy.da.SearchCursor(simplifiedFeatures, mergeFldNames)
                        else:
                            mergeFldNames = ('SHAPE@')
                            mergeCursor = arcpy.da.SearchCursor(mergeName, mergeFldNames)

                        for tRow in mergeCursor:
                            mShape = tRow[0]
                            mergeValueList = []
                            mergeValueList.append(mShape)
                            mergeValueList.append('MergedShape')
                            outfcCursor.insertRow(mergeValueList)

                        del outfcCursor
                        del mergeCursor
                        del tRow
                        arcpy.Delete_management(mergeName)
                        if useSimplified:
                            arcpy.Delete_management(simplifiedFeatures)

                    except arcpy.ExecuteError:
                        arcpy.AddError(arcpy.GetMessages())


            elif covCreateOption == "buffer each exposure point":
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

            elif covCreateOption == "from extent of all exposures":

                try:
                    inDesc = arcpy.Describe(inputFeatureClass)
                    inExtent = inDesc.extent
                    covPoly = inExtent.polygon
                    #arcpy.AddMessage(str(inExtent))
                    #arcpy.AddMessage(str(covPoly))
                    name = 'Extent'

                    if int(arcpy.GetCount_management(outputFeatureClass)[0]) > 0:
                        arcpy.DeleteFeatures_management(outputFeatureClass)

                    outFldName = ('SHAPE@','Name')
                    outfcCursor = arcpy.da.InsertCursor(outputFeatureClass,outFldName)

                    outValueList = []
                    outValueList.append(covPoly)
                    outValueList.append(name)

                    outfcCursor.insertRow(outValueList)
                    del outfcCursor

                    log.Message('Added Extent shape to Coverage Features', log.const_general_text)

                except arcpy.ExecuteError:
                    arcpy.AddError(arcpy.GetMessages())
                    log.Message(arcpy.GetMessages(), log.const_general_text)

            if (arcpy.ProductInfo() == 'ArcView'):
                pass
            else:
                arcpy.RecalculateFeatureClassExtent_management(outputFeatureClass)

            closeLog(log)

        except Exception as e:
            arcpy.AddError('Error in CreatingCoverageFeatures:{}'.format(str(e)))
            log.Message('Error in CreateCoverageFeatures:{}'.format(str(e)), log.const_critical_text)
            closeLog(log)

        #DisaplaySelectByLayerWarning(oidSelection)

class CreateCoverageMap(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Create Coverage Map"
        self.description = ""
        self.canRunInBackground = False


    def getParameterInfo(self):
        inputOIC = arcpy.Parameter(
        displayName="Input Oriented Imagery Catalog",
        name="inputOIC",
        datatype=["DEFile", "GPGroupLayer"],
        parameterType="Required",
        direction="Input")

        params = [inputOIC]
        return params


    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        pass

    def updateMessages(self, parameters):
        showCrashWarning(parameters)

    def execute(self,parameters,messages):
        try:
            log = initializeLog('CreateCoverageMap')
            initializeVersionCheck(log)
            isInputOICFile = False
            try:
                aprx = arcpy.mp.ArcGISProject("CURRENT")
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
                        log.Message('No records found in the Coverage Map Layer. The Coverage Map will be blank. To rectify run Create Coverage Features first and re-run this tool.', log.const_warning_text)
                    else:
                        webMercatorLayerList = inputMap.listLayers('WorldMercatorExtent')
                        if (len(webMercatorLayerList) == 1):
                            inputMap.removeLayer(webMercatorLayerList[0])

                        arcpy.CreateVectorTilePackage_management (inputMap, outFileName, "ONLINE", "","INDEXED")

                        arcpy.AddMessage('Vector Tile Package created for '+grpLayer.name)
                        log.Message('Vector Tile Package created for {}'.format(grpLayer.name), log.const_general_text)
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
                coverageLyr = arcpy.MakeFeatureLayer_management(coverageFCPath, os.path.splitext(os.path.basename(coverageFCPath))[0]).getOutput(0)
                layers = inputMap.listLayers()
                for l in layers:
                    inputMap.removeLayer(l)
                inputMap.addLayer(coverageLyr)
                coverageLyr = inputMap.listLayers()[0]
                oitools.updateCoverageLayerSymbology(coverageLyr)
                vtpkFileName = '{}.vtpk'.format(os.path.splitext(oicFilePath)[0])
                arcpy.CreateVectorTilePackage_management(inputMap, vtpkFileName, "ONLINE", "","INDEXED")
            closeLog(log)
        except Exception as e:
            arcpy.AddError('Error in creating coverage map. {}'.format(str(e)))
            log.Message('Error in creating coverage map. {}'.format(str(e)), log.const_critical_text)
            closeLog(log)


class SelectBrokenPaths(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Select Broken Paths"
        self.description = ""
        self.canRunInBackground = False

    def getParameterInfo(self):

        inputOIC = arcpy.Parameter(
        displayName="Input Oriented Imagery Catalog",
        name="inputOIC",
        datatype="GPGroupLayer",
        parameterType="Required",
        direction="Input")

        params = [inputOIC]

        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        pass

    def updateMessages(self, parameters):

        if not oitools.isActiveMap():
            parameters[0].setErrorMessage("This tool needs an active map to function correctly. Please make a map active and try again.")
        else:
            parameters[0].clearMessage()
        showCrashWarning(parameters)

    def execute(self,parameters,messages):
        try:
            log = initializeLog('SelectBrokenPaths')
            initializeVersionCheck(log)
            grpLayer = parameters[0].value
            grpLayers = grpLayer.listLayers()

            for gLyr in grpLayers:
                gLyrDec = arcpy.Describe(gLyr)
                if gLyrDec.shapeType == 'Point':
                    inputFeatureClass = gLyr
                    break

            fieldNames = []
            fieldNames.append('OBJECTID')
            fieldNames.append('Image')

            desc = arcpy.Describe(inputFeatureClass)
            selString = desc.FIDSet
            if selString =='':
                selType = 'NEW_SELECTION'
                selQuery = ''
            else:
                selType = 'SUBSET_SELECTION'
                selQuery= 'OBJECTID IN ('+selString.replace(';',',')+')'

            arcpy.AddMessage(selString+':::'+selType)
            log.Message(selString+':::'+selType, log.const_general_text)

            if desc.datatype == 'FeatureLayer':
                inSearchCursor = arcpy.da.SearchCursor(inputFeatureClass,fieldNames,selQuery)
            elif desc.datatype == 'FeatureClass':
                outPath = desc.catalogPath
                inSearchCursor = arcpy.da.SearchCursor(outPath,fieldNames,selQuery)
                inputFeatureClass = arcpy.MakeFeatureLayer_management (outPath, desc.name+'_temp')
            else:
                arcpy.AddMessage('No Feature Layer found.')
                log.Message('No Feature Layer found.', log.const_general_text)
                exit(1)

            oidSelection = []
            with inSearchCursor:
                for row in inSearchCursor:
                    sOID = row[0]
                    imgPath = row[1].strip()
                    #arcpy.AddMessage('Checking path for objectID:'+str(sOID))
                    log.Message('Checking path for objectID:{}'.format(sOID), log.const_general_text)

                    if imgPath.startswith('http'):
                        imgPath = oitools.returnValidURLFormat(imgPath)
                        r = requests.head(imgPath)
                        doesexist = r.status_code == requests.codes.ok
                        if doesexist == False:
                            oidSelection.append(sOID)
                    else:
                        if not os.path.exists(imgPath):
                            oidSelection.append(sOID)


            if len(oidSelection) != 0:
                arcpy.AddMessage("Selecting records.")
                log.Message("Selecting records.", log.const_general_text)

                if len(oidSelection) == 1:
                        theWhereClause = 'OBJECTID = '+str(oidSelection[0])
                elif len(oidSelection) > 1:
                    theWhereClause = ''
                    cntr = 1
                    for oids in oidSelection:
                        if cntr < len(oidSelection):
                            theWhereClause = theWhereClause + 'OBJECTID = '+str(oids) + ' OR '
                            cntr = cntr + 1
                        else:
                            theWhereClause = theWhereClause + 'OBJECTID = '+str(oids)
                            cntr + 1

                arcpy.AddMessage("Number of records selected :"+str(len(oidSelection)))
                log.Message("Number of records selected :"+str(len(oidSelection)), log.const_general_text)
                arcpy.SelectLayerByAttribute_management(inputFeatureClass,selType,theWhereClause)
                displaySelectByLayerWarning(theWhereClause)
            else:
                arcpy.AddMessage("All paths are valid. Nothing to select.")
                log.Message("All paths are valid. Nothing to select.", log.const_general_text)
            closeLog(log)
        except Exception as e:
            arcpy.AddError("Something went wrong in selecting broken paths. {}".format(str(e)))
            log.Message("Error while selecting broken paths. {}".format(str(e)), log.const_critical_text)
            closeLog(log)



class RepairPaths(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Repair Paths"
        self.description = ""
        self.canRunInBackground = False

    def getParameterInfo(self):

        inputOIC = arcpy.Parameter(
        displayName="Input Oriented Imagery Catalog",
        name="inputOIC",
        datatype=['DEFile', "GPGroupLayer"],
        parameterType="Required",
        direction="Input")

        pathsMappingTable = arcpy.Parameter(
        displayName='Repair Paths:',
        name='pathsMappingTable',
        datatype='GPValueTable',
        parameterType='Optional',
        direction='Input')
        pathsMappingTable.columns = [['GPString', 'OriginalPath'], ['GPString', 'ReplacePath']]
        pathsMappingTable.enabled = False

        params = [inputOIC, pathsMappingTable]

        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        if parameters[0].altered == True or parameters[0].hasBeenValidated:
            if not parameters[0].valueAsText.lower().endswith('.oic'):
                grpLayer = parameters[0].value

                grpLayers = grpLayer.listLayers()

                for gLyr in grpLayers:
                    gLyrDec = arcpy.Describe(gLyr)
                    if gLyrDec.shapeType == 'Point':
                        pointFeatureLayer = gLyr
                        break

                iFldNames = []
                iFldNames.append('Image')

                desc = arcpy.Describe(pointFeatureLayer)

                selString = desc.FIDSet
                if selString =='':
                    selType = 'NEW_SELECTION'
                    selQuery = ''
                else:
                    selType = 'SUBSET_SELECTION'
                    selQuery= 'OBJECTID IN ('+selString.replace(';',',')+')'

                if desc.datatype == 'FeatureLayer':
                    inSearchCursor = arcpy.da.SearchCursor(pointFeatureLayer,iFldNames,selQuery)
                elif desc.datatype == 'FeatureClass':
                    pointFeatureClassPath = desc.catalogPath
                    inSearchCursor = arcpy.da.SearchCursor(pointFeatureClassPath,iFldNames,selQuery)
                else:
                    arcpy.AddMessage('No Feature Layer found.')
                    exit(1)
            else:
                oicFilePath = parameters[0].valueAsText
                with open(oicFilePath) as oicFile:
                    oicDict = json.load(oicFile)
                featureClassPath = oicDict['properties']['PointsSource']
                inSearchCursor = arcpy.da.SearchCursor(featureClassPath, ['Image'], '')

            allPaths = []

            with inSearchCursor:
                for row in inSearchCursor:
                    pathName = row[0]
                    if pathName is not None:
                        aPath = os.path.dirname(pathName)
                        if [aPath, aPath] not in allPaths:
                            allPaths.append([aPath,aPath])

            if parameters[1].hasBeenValidated == True and parameters[0].hasBeenValidated == False:
                parameters[1].value = allPaths
                parameters[1].enabled = True

        else:
            parameters[1].enabled = False
            parameters[1].value = None
        return

    def updateMessages(self, parameters):
        showCrashWarning(parameters)
        if parameters[1].value != None:
            allPaths1 = parameters[1].value
            for pthValues in allPaths1:
                chkPth = pthValues[0]
                replpth = pthValues[1]
                if chkPth.endswith('/') or chkPth.endswith('\\') or replpth.endswith('/') or replpth.endswith('\\'):
                    parameters[1].setErrorMessage("Search paths or replace paths should not end in slash(/) or backslash (\). Please remove and then proceed.")
                else:
                    parameters[1].clearMessage()
        else:
            parameters[1].clearMessage()
        return

    def execute(self,parameters,messages):
        try:
            log = initializeLog('RepairPaths')
            initializeVersionCheck(log)
            isInputOICFile = False
            try:
                currProj = arcpy.mp.ArcGISProject("CURRENT")
            except:
                isInputOICFile = True
            if parameters[0].valueAsText.lower().endswith('.oic'):
                isInputOICFile = True
            allPaths = parameters[1].value
            if not isInputOICFile:
                grpLayer = parameters[0].value
                grpLayers = grpLayer.listLayers()

                for gLyr in grpLayers:
                    gLyrDec = arcpy.Describe(gLyr)
                    if gLyrDec.shapeType == 'Point':
                        inputFeatureClass = gLyr
                        break

                fieldNames = []
                fieldNames.append('Image')

                desc = arcpy.Describe(inputFeatureClass)

                selString = desc.FIDSet
                if selString =='':
                    selType = 'NEW_SELECTION'
                    selQuery = ''
                else:
                    selType = 'SUBSET_SELECTION'
                    selQuery= 'OBJECTID IN ('+selString.replace(';',',')+')'

                if desc.datatype == 'FeatureLayer':
                    inUpdateCursor = arcpy.da.UpdateCursor(inputFeatureClass,fieldNames,selQuery)
                elif desc.datatype == 'FeatureClass':
                    outPath = desc.catalogPath
                    inUpdateCursor = arcpy.da.UpdateCursor(outPath,fieldNames,selQuery)

                else:
                    arcpy.AddMessage('No Feature Layer found.')
                    log.Message('No Feature Layer found.', log.const_general_text)
                    exit(1)
            else:
                oicFilePath = parameters[0].valueAsText
                with open(oicFilePath) as oicFile:
                    oicDict = json.load(oicFile)
                featureClassPath = oicDict['properties']['PointsSource']
                inUpdateCursor = arcpy.da.UpdateCursor(featureClassPath, ['Image'], '')

            with inUpdateCursor:
                for row in inUpdateCursor:
                    srchPath = row[0]
                    if srchPath != None:
                        for pthValues in allPaths:
                            chkPth = pthValues[0]
                            replpth = pthValues[1]

                            if chkPth in srchPath :
                                #arcpy.AddMessage(srchPath+';'+chkPth+';'+replpth)
                                log.Message("ImagePath:{};OriginalPath:{};ReplacePath:{}".format(srchPath, chkPth, replpth), log.const_general_text)
                                updatePath = srchPath.replace(chkPth,replpth)
                                row[0] = updatePath
                                inUpdateCursor.updateRow(row)

            del row

            arcpy.AddMessage('Done')
            closeLog(log)
        except Exception as e:
            err = str(e)
            if 'cannot acquire a lock' in str(e).lower():
                err = 'Please make sure the attribute table is closed before runnning the tool.'
            arcpy.AddError("Error in repairing paths. {}".format(err))
            log.Message("Error in repairing paths. {}".format(err), log.const_critical_text)
            closeLog(log)

class SelectLocalImages(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Select Local Images"
        self.description = ""
        self.canRunInBackground = False


    def getParameterInfo(self):

        inputOIC = arcpy.Parameter(
        displayName="Input Oriented Imagery Catalog",
        name="inputOIC",
        datatype="GPGroupLayer", #datatype="GPFeatureLayer",
        parameterType="Required",
        direction="Input")

        params = [inputOIC]

        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        pass

    def updateMessages(self, parameters):

        if not oitools.isActiveMap():
            parameters[0].setErrorMessage("This tool needs an active map to function correctly. Please make a map active and try again.")
        else:
            parameters[0].clearMessage()
        showCrashWarning(parameters)
    def execute(self,parameters,messages):
        try:
            log = initializeLog('SelectLocalImages')
            initializeVersionCheck(log)
            grpLayer = parameters[0].value
            grpLayers = grpLayer.listLayers()

            for gLyr in grpLayers:
                gLyrDec = arcpy.Describe(gLyr)
                if gLyrDec.shapeType == 'Point':
                    inputFeatureClass = gLyr
                    break

            iFldNames = []
            iFldNames.append('OBJECTID')
            iFldNames.append('Image')

            desc = arcpy.Describe(inputFeatureClass)
            selString = desc.FIDSet
            if selString =='':
                selType = 'NEW_SELECTION'
                selQuery = ''
            else:
                selType = 'SUBSET_SELECTION'
                selQuery= 'OBJECTID IN ('+selString.replace(';',',')+')'

            if desc.datatype == 'FeatureLayer':
                inSearchCursor = arcpy.da.SearchCursor(inputFeatureClass,iFldNames,selQuery)
            elif desc.datatype == 'FeatureClass':
                outPtah = desc.catalogPath
                inSearchCursor = arcpy.da.SearchCursor(outPtah,iFldNames,selQuery)
                inputFeatureClass = arcpy.MakeFeatureLayer_management (outPtah, desc.name+'_temp')
            else:
                arcpy.AddMessage('No Feature Layer found.')
                log.Message('No Feature Layer found.', log.const_general_text)
                exit(1)

            oidSelection = []
            with inSearchCursor:
                for row in inSearchCursor:
                    sOID = row[0]
                    imgPath = row[1]
                    if imgPath.strip().startswith('http'):
                        pass
                    else:
                        oidSelection.append(sOID)

            if len(oidSelection) != 0:
                arcpy.AddMessage("Selecting records.")
                log.Message("Selecting records.", log.const_general_text)
                if len(oidSelection) == 1:
                        theWhereClause = 'OBJECTID = '+str(oidSelection[0])
                elif len(oidSelection) > 1:
                    theWhereClause = ''
                    cntr = 1
                    for oids in oidSelection:
                        if cntr < len(oidSelection):
                            theWhereClause = theWhereClause + 'OBJECTID = '+str(oids) + ' OR '
                            cntr = cntr + 1
                        else:
                            theWhereClause = theWhereClause + 'OBJECTID = '+str(oids)
                            cntr + 1
                arcpy.AddMessage("Number of records selected :"+str(len(oidSelection)))
                log.Message("Number of records selected :"+str(len(oidSelection)), log.const_general_text)
                arcpy.SelectLayerByAttribute_management(inputFeatureClass,selType,theWhereClause)
                displaySelectByLayerWarning(theWhereClause)
            else:
                arcpy.AddMessage("No Local images found. Nothing to select.")
                log.Message("No Local images found. Nothing to select.", log.const_general_text)
            closeLog(log)

        except Exception as e:
            arcpy.AddMessage('Error in selecting local images: {}'.format(str(e)))
            log.Message('Error in selecting local images: {}'.format(str(e)), log.const_critical_text)
            closeLog(log)


class AnalyseOrientedImageryCatalog(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Analyze Oriented Imagery Catalog"
        self.description = ""
        self.canRunInBackground = False


    def getParameterInfo(self):

        inputOIC = arcpy.Parameter(
        displayName="Input Oriented Imagery Catalog",
        name="inputOIC",
        datatype=["DEFile", "GPGroupLayer"],
        parameterType="Required",
        direction="Input")

        checkBrokenPaths = arcpy.Parameter(
            displayName="Check for broken paths",
            name="checkBrokenPaths",
            datatype='GPBoolean',
            parameterType="Optional",
            direction="Input")

        params = [inputOIC, checkBrokenPaths]

        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        pass

    def updateMessages(self, parameters):
        showCrashWarning(parameters)

    def isDefaultAttributeSet(self, oicJson, attribute):
        try:
            if oicJson['properties']['DefaultAttributes'].get(attribute):
                return True
            return False
        except Exception as e:
            arcpy.AddMessage('Error:'+str(e))
            return False

    def getNumberOfRowsWithNonEmptyValue(self, featureClass, field):
        try:
            inSearchCursor = arcpy.da.SearchCursor(featureClass, [field], "{} IS NOT NULL".format(field))
            rows = [row for row in inSearchCursor]
            return len(rows)
        except Exception as e:
            arcpy.AddError(str(e))

    def getVisibleFields(self, featureLayer):
        try:
            fields = arcpy.ListFields(featureLayer)
            desc = arcpy.Describe(featureLayer)
            fieldinfo = desc.fieldinfo
            visibleFields = []
            for i, field in enumerate(fields):
                if fieldinfo.getVisible(i) == 'VISIBLE':
                    visibleFields.append(field.name)
            return visibleFields
        except:
            return []


    def execute(self, parameters, messages):
        isInputOICFile = False
        try:
            log = initializeLog('AnalyzerTool')
            initializeVersionCheck(log)
            try:
                currProj = arcpy.mp.ArcGISProject("CURRENT")
            except:
                isInputOICFile = True
            if parameters[0].valueAsText.lower().endswith('.oic'):
                isInputOICFile = True
            if not isInputOICFile:
                grpLayer = parameters[0].value
                grpLayers = grpLayer.listLayers()
                featureLayer = ''
                for gLyr in grpLayers:
                    gLyrDec = arcpy.Describe(gLyr)
                    if gLyrDec.shapeType == 'Point':
                        featureLayer = gLyr
                        featureClass = gLyrDec.catalogPath
                        gLyrsourceDir = os.path.dirname(os.path.dirname(featureClass))
                        oicFilePath = os.path.join(gLyrsourceDir,grpLayer.name+'.oic')
                        vtpkFilePath = os.path.join(gLyrsourceDir,grpLayer.name+'.vtpk')
                    elif gLyrDec.shapeType == 'Polygon':
                        coverageFeatureClass = gLyrDec.catalogPath
                if not featureLayer:
                    arcpy.AddMessage('No Feature Layer found.')
                    log.Message('No Feature Layer found.', log.const_general_text)
                    exit(1)
            else:
                oicFilePath = parameters[0].valueAsText
                vtpkFilePath = os.path.splitext(oicFilePath)[0] + '.vtpk'
                with open(oicFilePath) as oicFile:
                    oicDict = json.load(oicFile)
                coverageFeatureClass = oicDict['properties']['CoverageSource']
                featureClass = oicDict['properties']['PointsSource']
            existingFieldNames = [field.name for field in arcpy.ListFields(featureClass)]
            if 'Image' not in existingFieldNames:
                arcpy.AddMessage('Required field \'Image\' is missing')
            allDefaultFields = ['CamHeading', 'CamPitch', 'CamRoll',
                              'HFOV', 'VFOV', 'AvgHtAG', 'FarDist', 'NearDist', 'OIType']
            defaultFieldsPresent = [field for field in existingFieldNames if field in allDefaultFields]
            defaultFieldsNotPresent = list(set(allDefaultFields) - set(defaultFieldsPresent))

            try:
                with open(oicFilePath) as f:
                    oic_file = json.load(f)
            except:
                arcpy.AddError('Issue in reading the OIC file: {}'.format(oicFilePath))

            inSearchCursor = arcpy.da.SearchCursor(featureClass, existingFieldNames)
            localImagesExist = False
            isPathBroken = False
            fieldsWithNoDefaultValue = set()
            if parameters[1].value:
                arcpy.AddMessage("Checking for broken paths...")
                for row in inSearchCursor:
                    imgPath = row[existingFieldNames.index('Image')]
                    if (not isPathBroken) and imgPath.startswith('http'):
                        imgPath = oitools.returnValidURLFormat(imgPath)
                        r = requests.head(imgPath)
                        isPathBroken = not (r.status_code == requests.codes.ok)
                if isPathBroken:
                    arcpy.AddWarning("Broken paths found!")
                    arcpy.AddWarning("Please run the Select Broken Paths GP Tool to identify the broken paths.")
                    log.Message("Please run the SelectBrokenPaths GP Tool to identify the broken paths.", log.const_warning_text)
                else:
                    arcpy.AddMessage("No broken paths found.")
                    log.Message("No broken paths found.", log.const_general_text)

            inSearchCursor.reset()
            arcpy.AddMessage("Checking for local images and default values...")
            for row in inSearchCursor:
                imgPath = row[existingFieldNames.index('Image')]
                if (not localImagesExist) and (not imgPath.strip().startswith('http')):
                    localImagesExist = True
                defaultAttributeValues = [row[existingFieldNames.index(defaultFieldPresent)] for defaultFieldPresent in defaultFieldsPresent]
                for i, val in enumerate(defaultAttributeValues):
                    if not defaultFieldsPresent[i] in fieldsWithNoDefaultValue:
                        if val is None:
                            defaultValFound = self.isDefaultAttributeSet(oic_file, defaultFieldsPresent[i])
                            if not defaultValFound:
                                fieldsWithNoDefaultValue.add(defaultFieldsPresent[i])
                for defaultFieldNotPresent in defaultFieldsNotPresent:
                    defaultValFound = self.isDefaultAttributeSet(oic_file, defaultFieldNotPresent)
                    if not defaultValFound:
                        fieldsWithNoDefaultValue.add(defaultFieldNotPresent)

            if localImagesExist:
                arcpy.AddWarning('Local images found!')
                arcpy.AddWarning('Please run the Select Local Images GP Tool to identify the local images.')
                arcpy.AddWarning('After identifying the local images run the Copy Images to Web to upload to cloud storage.')
                log.Message("Please run the SelectLocalImages GP Tool to identify the local images.", log.const_warning_text)
            else:
                arcpy.AddMessage("No Local images found.")
                log.Message("No Local images found.", log.const_general_text)

            fieldsToBeHidden = []
            if fieldsWithNoDefaultValue:
                arcpy.AddWarning('The following mandatory field(s) have no values in the feature class for one or more rows.')
                arcpy.AddWarning('These field(s) do not have a default value set in the OIC properties file either.\n{} '.format(
                                 '\n'.join(fieldsWithNoDefaultValue)))
                arcpy.AddWarning("Please make sure to fill values in the rows using 'Calculate Field' or the OIC Properties GP Tool.")
                log.Message('The following mandatory field(s) have no values in the feature class for one or more rows.\n'
                            'These field(s) do not have a default value set in the OIC properties file either.\n{} '.format(
                                '\n'.join(fieldsWithNoDefaultValue)), log.const_warning_text)
            else:
                arcpy.AddMessage("All mandatory fields have values.")
                log.Message("All mandatory fields have values.", log.const_general_text)
            arcpy.AddMessage("Checking if fields need to be hidden in the feature class...")
            if not isInputOICFile:
                visibleFields = self.getVisibleFields(featureLayer)
            else:
                visibleFields = existingFieldNames
            for field in visibleFields:
                defaultValFound = self.isDefaultAttributeSet(oic_file, field)
                if defaultValFound:
                    nRows = self.getNumberOfRowsWithNonEmptyValue(featureClass, field)
                    if nRows == 0:
                        fieldsToBeHidden.append(field)
            if fieldsToBeHidden:
                arcpy.AddWarning('The following field(s) are empty in the feature class, and have values defined in the OIC properties file.\n{}'.format(
                                 '\n'.join(fieldsToBeHidden)))
                arcpy.AddWarning('To Optimize the Oriented Imagery Catalog before publishing, it is recommended to hide these fields.')
                arcpy.AddWarning('This can be done by opening the attribute table, Opening the Fields View and turning the Visibilty off.')
                log.Message('The following field(s) are empty in the feature class, and have values defined in the OIC properties file.\n{}'.format(
                            '\n'.join(fieldsToBeHidden)), log.const_warning_text)
            else:
                arcpy.AddMessage("No need to hide any field.")
                log.Message("No need to hide any field.", log.const_general_text)
            arcpy.AddMessage('Checking for coverage features...')
            if coverageFeatureClass:
                coverageSearchCursor = arcpy.da.SearchCursor(coverageFeatureClass, ['OBJECTID', 'Shape', 'Shape_length', 'Shape_Area'])
                rows = [row for row in coverageSearchCursor]
                if not rows:
                    arcpy.AddWarning("Coverage features not found.\n Please run CreateCoverageFeatures GP Tool")
                    arcpy.AddWarning("This operation is optional. However it is a useful tool to know the field of view for each point.")
                    log.Message("Coverage features not found.\n Please run CreateCoverageFeatures GP Tool", log.const_warning_text)
                else:
                    arcpy.AddMessage("Coverage features found.")
                    log.Message("Coverage features found.", log.const_general_text)
                    arcpy.AddMessage("Checking for vector tile package...")
                    if not os.path.exists(vtpkFilePath):
                        arcpy.AddWarning("Coverage vector tile package not found.\n Please run CreateCoverageMap GP Tool")
                        log.Message("Coverage vector tile package not found.\n Please run CreateCoverageMap GP Tool", log.const_warning_text)
                    else:
                        arcpy.AddMessage("Coverage vector tile package found.")
                        log.Message("Coverage vector tile package found.", log.const_general_text)
            else:
                arcpy.AddWarning("Coverage features not found.\n Please run CreateCoverageFeatures GP Tool")
                log.Message("Coverage features not found.\n Please run CreateCoverageFeatures GP Tool", log.const_warning_text)
            closeLog(log)
        except Exception as e:
            arcpy.AddError('Error in analyzer tool: {}'.format(str(e)))
            log.Message('Error in analyzer tool: {}'.format(str(e)), log.const_critical_text)
            closeLog(log)


class CopyImagetoWeb(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Copy Images to Web"
        self.description = ""
        self.canRunInBackground = False


    def getParameterInfo(self):

        inputOIC = arcpy.Parameter(
        displayName="Input Oriented Imagery Catalog",
        name="inputOIC",
        datatype=["DEFile", "GPGroupLayer"],
        parameterType="Required",
        direction="Input")

        types = ['Amazon S3', 'Microsoft Azure', 'Google Cloud']    # 'local' must be the first element.
        storageType = arcpy.Parameter(
            displayName="Upload Data to :",
            name="CIW_Types",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        storageType.filter.type = "ValueList"
        storageType.filter.list = types    # 'local' must be the first element.
        storageType.value = types[0]

        inputProfile = arcpy.Parameter(
            displayName="Cloud Service Profile",
            name="inputProfile",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        inputProfile.filter.type = "ValueList"

        bucket = arcpy.Parameter(
            displayName="Bucket/Container",
            name="bucket",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        bucket.filter.type = "ValueList"

        path = arcpy.Parameter(
            displayName="Web Folder/Path",
            name="path",
            datatype='GPString',
            parameterType="Required",
            direction="Input")

        optimize = arcpy.Parameter(
            displayName="Optimize Imagery for the cloud",
            name="optimize",
            datatype='GPBoolean',
            parameterType="Optional",
            direction="Input")
        optimize.enabled = True
        optimize.value = False

        parameters = [inputOIC,storageType,inputProfile,bucket,path,optimize] #,CIW_optimize,CIW_Actions,CIW_outOIC]

        return parameters

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):

        if parameters[1].altered == True:
            pFolder = pfileName = None
            if parameters[1].valueAsText == 'Amazon S3':
                pFolder = AwsRoot
                pfileName = 'credentials'
                parameters[2].enabled = True
                parameters[3].enabled = True
            elif parameters[1].valueAsText == 'Microsoft Azure':
                pFolder = AzureRoot
                pfileName = 'azure_credentials'
                parameters[2].enabled = True
                parameters[3].enabled = True
            elif parameters[1].valueAsText == 'Google Cloud':
                pFolder = GoogleRoot
                pfileName = '*.json'
                parameters[2].enabled = True
                parameters[3].enabled = True
            if parameters[3].value == 'Local':
                parameters[3].value = ''
            if parameters[2].value == 'Profile':
                parameters[2].value = ''
            if (pFolder):
                p2Config = oitools.MOI_config_Init(pFolder, pfileName)
                if (p2Config):
                    p2List = p2Config.sections()
                    parameters[2].filter.list = p2List

        if parameters[2].altered == True:
            # fetch the list of bucket names available for the selected input profile
            availableBuckets = oitools.MOI_getAvailableBuckets(parameters[1], parameters[2])
            if availableBuckets:
                if type(availableBuckets) == dict:
                    availableBuckets = availableBuckets['response']['buckets']
                parameters[3].filter.list = availableBuckets        # 3 == bucket names
            else:
                if (parameters[2].value is not None and
                    not parameters[2].value.lower().startswith('iamrole:') and
                        not parameters[2].value.lower().startswith('aws_publicbucket')):
                    if (not parameters[2].value.lower().endswith('public-buckets.json')):
                        parameters[3].value = ''

    def updateMessages(self, parameters):
        showCrashWarning(parameters)
        if parameters[2].valueAsText != None:
            if 'Amazon' in parameters[1].valueAsText:
                allKeys =  sys.modules.keys()
                if 'boto3' in allKeys:
                    parameters[3].clearMessage()
                else:
                    parameters[3].setWarningMessage('Python module boto3 is not installed. Boto3 is required to upload files to Amazon S3 and list available folders.')
            else:
                parameters[3].clearMessage()


    def execute(self,parameters,messages):
        try:
            log = initializeLog('CopyImagetoWeb')
            initializeVersionCheck(log)
            isInputOICFile = False
            try:
                currProj = arcpy.mp.ArcGISProject("CURRENT")
            except:
                isInputOICFile = True
            if parameters[0].valueAsText.lower().endswith('.oic'):
                isInputOICFile = True
            iFldNames = ['OBJECTID','Image']
            if not isInputOICFile:
                grpLayer = parameters[0].value
                grpLayers = grpLayer.listLayers()

                for gLyr in grpLayers:
                    gLyrDec = arcpy.Describe(gLyr)
                    if gLyrDec.shapeType == 'Point':
                        inputFeatureClass = gLyr
                        break

                desc = arcpy.Describe(inputFeatureClass)
                selString = desc.FIDSet
                if selString =='':
                    selType = 'NEW_SELECTION'
                    selQuery = ''
                else:
                    selType = 'SUBSET_SELECTION'
                    selQuery= 'OBJECTID IN ('+selString.replace(';',',')+')'

                if desc.datatype == 'FeatureLayer':
                    inSearchCursor = arcpy.da.SearchCursor(inputFeatureClass,iFldNames,selQuery)
                    inUpdateCursor = arcpy.da.UpdateCursor(inputFeatureClass,iFldNames,selQuery)
                elif desc.datatype == 'FeatureClass':
                    outPath = desc.catalogPath
                    inSearchCursor = arcpy.da.SearchCursor(outPath,iFldNames,selQuery)
                    inUpdateCursor = arcpy.da.UpdateCursor(outPath,iFldNames,selQuery)
                    inputFeatureClass = arcpy.MakeFeatureLayer_management (outPath, desc.name+'_temp')
                else:
                    arcpy.AddMessage('No Feature Layer found.')
                    log.Message('No Feature Layer found.', log.const_general_text)
                    exit(1)
            else:
                oicFilePath = parameters[0].valueAsText
                with open(oicFilePath) as oicFile:
                    oicDict = json.load(oicFile)
                featureClassPath = oicDict['properties']['PointsSource']
                inSearchCursor = arcpy.da.SearchCursor(featureClassPath, iFldNames, '')
                inUpdateCursor = arcpy.da.UpdateCursor(featureClassPath, iFldNames,'')

            oidSelection = []
            uniqueFolderPaths = []

            imgList = []
            uniquePathList = []
            with inSearchCursor:
                for row in inSearchCursor:
                    sOID = row[0]
                    imgPath = row[1]
                    if imgPath.startswith('http'):
                        pass
                    else:
                        oidSelection.append(sOID)
                        aBaseDirName = os.path.dirname(imgPath)
                        if aBaseDirName not in uniquePathList:
                            uniquePathList.append(aBaseDirName)

                        imgList.append(imgPath)

            if len(imgList) > 0:
                args = {}
                inargs = {}

                inType = parameters[1].valueAsText
                inprofiles = parameters[2].valueAsText
                inBucket = parameters[3].valueAsText
                inPath = parameters[4].valueAsText
                optimizImg = parameters[5].value


                template_path = ORDependent_path
                _CTEMPLATE_FOLDER = 'OptimizeRasters\\Templates'

                if optimizImg:
                    configFN = os.path.join(os.path.join(os.path.dirname(template_path), _CTEMPLATE_FOLDER), 'Imagery_to_MRF_JPEG.xml')
                else:
                    configFN = os.path.join(os.path.join(os.path.dirname(template_path), _CTEMPLATE_FOLDER), 'CopyFilesOnly.xml')

                proxymrfConfig = os.path.join(os.path.join(os.path.dirname(template_path), _CTEMPLATE_FOLDER), 'CreateRasterProxy.xml')


                intempFolder = os.getenv('TEMP')#Get Sysystem Temp Folder.
                dtNow = datetime.datetime.now()
                prefix = 'OI_Proxy_'
                jobFolder = prefix + "_%04d%02d%02dT%02d%02d%02d%06d" % (dtNow.year, dtNow.month, dtNow.day,
                                dtNow.hour, dtNow.minute, dtNow.second, dtNow.microsecond)

                proxyFilePath = os.path.join(os.getenv('TEMP'),jobFolder)


                for inputDir in uniquePathList:
                    args['version'] = 'v2.0.1g/20171102'

                    args['config'] = configFN
                    inargs['mode']='rasterproxy'
                    inargs['config'] = proxymrfConfig

                    args['output'] = parameters[4].valueAsText
                    inargs['output'] = proxyFilePath

                    args['input'] = inputDir
                    inargs['input'] = parameters[4].valueAsText

                    args['cloudupload'] = 'true'
                    inargs['clouddownload'] = 'true'

                    args['outputprofile'] = parameters[2].valueAsText
                    inargs['inputprofile'] = parameters[2].valueAsText

                    outType = parameters[1].valueAsText
                    clouduploadtype_ = 'amazon'
                    if (outType == 'Microsoft Azure'):
                        clouduploadtype_ = 'azure'
                    elif (outType == 'Google Cloud'):
                        clouduploadtype_ = 'google'
                    args['clouduploadtype'] = clouduploadtype_
                    inargs['clouddownloadtype'] = clouduploadtype_

                    args['outputbucket'] = parameters[3].valueAsText
                    inargs['inputbucket'] = parameters[3].valueAsText

                    args['tempoutput'] = intempFolder  # used only if -cloudupload=true
                    args['deleteafterupload'] = 'false'


                    dtNow = datetime.datetime.now()
                    prefix = 'OR_OI'
                    jobName = prefix + "_%04d%02d%02dT%02d%02d%02d%06d" % (dtNow.year, dtNow.month, dtNow.day,
                                                                         dtNow.hour, dtNow.minute, dtNow.second, dtNow.microsecond)
                    fullJobName = os.path.join(template_path,jobName+'.orjob')
                    imgListToProcess = []
                    for chkimg in imgList:
                        chkFolder = os.path.dirname(chkimg)
                        if chkFolder == inputDir:
                            imgListToProcess.append(chkimg)

                    oitools.MOI_CreateORJob(fullJobName,args,imgListToProcess)

                    # let's run (OptimizeRasters)
                    arcpy.AddMessage("Uploading Files.")
                    log.Message("Uploading Files.", log.const_general_text)
                    or_args = {}
                    or_args['input'] = fullJobName
                    import OptimizeRasters
                    app = OptimizeRasters.Application(or_args)
                    if (not app.init()):
                        arcpy.AddError('Error. Unable to initialize (OptimizeRasters module)')
                        log.Message('Error. Unable to initialize (OptimizeRasters module)', log.const_critical_text)
                        exit(0)

                    app.postMessagesToArcGIS = True
                    app.run()

                    rpt = app.getReport()   # Get report/log status
                    isSuccess = False
                    if (rpt and
                            not rpt.hasFailures()):  # If log has no failures, consider the processing as successful.
                        isSuccess = True
                    else:
                        arcpy.AddMessage ('Results> {}'.format(str(isSuccess)))
                        log.Message('Results> {}'.format(str(isSuccess)), log.const_general_text)
                        exit(1)
                    #return isSuccess


                #Lets run OR and get the list of proxy files.
                arcpy.AddMessage('Creating list of uploaded files.')
                log.Message('Creating list of uploaded files.', log.const_general_text)
                app = OptimizeRasters.Application(inargs)
                if (not app.init()):
                    arcpy.AddError('Error. Unable to initialize (OptimizeRasters module)')
                    log.Message('Error. Unable to initialize (OptimizeRasters module)', log.const_critical_text)
                    return False
                app.postMessagesToArcGIS = True
                app.run()
                rpt = app.getReport()   # Get report/log status
                #arcpy.AddMessage(rpt)
                isSuccess = False
                if (rpt and
                        not rpt.hasFailures()):  # If log has no failures, consider the processing as successful.
                    isSuccess = True
                else:
                    arcpy.AddMessage ('Results> {}'.format(str(isSuccess)))
                    log.Message('Results> {}'.format(str(isSuccess)), log.const_general_text)
                    exit(1)

                #update the path.
                arcpy.AddMessage('Replacing paths of uploaded files.')
                log.Message('Replacing paths of uploaded files.', log.const_general_text)

                oidstr = str(oidSelection)
                selQuery= 'OBJECTID IN ('+oidstr.rstrip(']').lstrip('[')+')'
                if not isInputOICFile:
                    if desc.datatype == 'FeatureLayer':
                        inUpdateCursor = arcpy.da.UpdateCursor(inputFeatureClass,iFldNames,selQuery)
                    elif desc.datatype == 'FeatureClass':
                        outPath = desc.catalogPath
                        inUpdateCursor = arcpy.da.UpdateCursor(outPath,iFldNames,selQuery)
                else:
                    inUpdateCursor = arcpy.da.UpdateCursor(featureClassPath,iFldNames,selQuery)

                updatePaths = True
                with inUpdateCursor:
                    for urow in inUpdateCursor:
                        imgPath = urow[1]
                        imgBaseName = os.path.basename(imgPath)
                        fileFolder, imgextension = os.path.splitext(imgPath)
                        mrfproxyName = os.path.join(proxyFilePath,imgBaseName.replace(imgextension,'.mrf'))
                        if (os.path.exists(mrfproxyName)):
                            tree = ET.parse(mrfproxyName)
                            root = tree.getroot()
                            thesrc = root.find("CachedSource/Source")
                            src_replace = thesrc.text.replace('/vsicurl/','')
                            urow[1] = src_replace
                            inUpdateCursor.updateRow(urow)
                        else:
                            updatePaths = False

                if not updatePaths:
                    arcpy.AddWarning("Could not update input table with paths of uploaded images. Check bucket policies for listing files using gdal.")
                    log.Message("Could not update input table with paths of uploaded images. Check bucket policies for listing files using gdal.", log.const_warning_text)
            else:
                arcpy.AddMessage("No Local images found. Nothing to upload.")
                log.Message("No Local images found. Nothing to upload.", log.const_general_text)
            closeLog(log)
        except Exception as e:
            arcpy.AddError("Error in copying images to web: {}".format(str(e)))
            log.Message("Error in copying images to web: {}".format(str(e)), log.const_critical_text)
            closeLog(log)

class PublishOrientedImageCatalog(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Publish Oriented Imagery Catalog"
        self.description = ""
        self.canRunInBackground = False


    def getParameterInfo(self):
        global warningMessage
        warningMessage = None
        global errorMessage
        errorMessage = None
        inputOIC = arcpy.Parameter(
            displayName = "Oriented Imagery Catalog",
            name = "inputOIC",
            datatype=["DEFile", "GPGroupLayer"],
            parameterType = "Required",
            direction = "Input"
        )

        tags = arcpy.Parameter(
            displayName="Tags",
            name="tags",
            datatype="GPString",
            parameterType="Required",
            direction="Input"
        )

        description = arcpy.Parameter(
            displayName="Description",
            name="description",
            datatype="GPString",
            parameterType="Required",
            direction="Input"
        )

        portal_folder_name = arcpy.Parameter(
                displayName="Portal folder name:",
            name="portal_folder_name",
            datatype= 'GPString',
            parameterType="Optional",
            direction='Input')

        publish_values = ['Publish all', 'Publish all - overwrite', 'Publish Oriented Imagery Catalog item only',
                           'Publish Oriented Imagery Catalog item only - overwrite']
        publish_options = arcpy.Parameter(
            displayName="Publish options :",
            name="publish_options",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        publish_options.filter.type = "ValueList"
        publish_options.filter.list = publish_values
        publish_options.value = publish_values[0]

        attachData = arcpy.Parameter(
            displayName="Add images as attachments",
            name="attachData",
            datatype='GPBoolean',
            parameterType="Optional",
            direction="Input")
        attachData.enabled = False
        attachData.value = False

        parameters = [inputOIC, tags, description, portal_folder_name, publish_options, attachData]
        return parameters


    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def isValidGroupLayer(self, group_layer):
        try:
            is_valid_layer = False
            sub_layers = group_layer.listLayers()
            if len(sub_layers) == 2:
                feature_layers = [layer for layer in sub_layers if layer.isFeatureLayer]
                if len(feature_layers) == 2:
                    point_found = False
                    polygon_found = False
                    for feature_layer in feature_layers:
                        layer_dec = arcpy.Describe(feature_layer)
                        catalog_path = layer_dec.catalogPath
                        if layer_dec.shapeType == 'Point':
                            if catalog_path.endswith('_ExposurePoints') and not catalog_path.startswith('http'):
                                point_found = True
                        elif layer_dec.shapeType == 'Polygon':
                            if catalog_path.endswith('_CoverageMap') and not catalog_path.startswith('http'):
                                polygon_found = True
                    if point_found and polygon_found:
                        is_valid_layer = True
            return is_valid_layer
        except:
            return False


    def updateParameters(self, parameters):
        global warningMessage
        warningMessage = ""
        global errorMessage
        errorMessage = ""
        try:
            tkDict = arcpy.GetSigninToken()
            if tkDict != None:
                portalToken = tkDict['token']

            portal_desc = arcpy.GetPortalDescription()
            user_name = portal_desc['user']['username']
            portalurl = arcpy.GetActivePortalURL()
            feature_service_util = FeatureServiceUtil(user_name, portalurl)
            folders = feature_service_util.list_all_portal_folders()
            folder_names = [folder['title'] for folder in folders]
            parameters[3].filter.type = "ValueList"
            parameters[3].filter.list = folder_names
        except:
            parameters[3].filter.type = "ValueList"
            parameters[3].filter.list = []
        if parameters[0].altered and not parameters[0].hasBeenValidated:
            if parameters[0].valueAsText.lower().endswith('.oic'):
                oicFilePath = parameters[0].valueAsText
            else:
                grpLayer = parameters[0].value
                is_valid_layer = self.isValidGroupLayer(grpLayer)
                if not is_valid_layer:
                    errorMessage = "This group layer is invalid! Please select another group layer."
                    return
                grpLayers = grpLayer.listLayers()
                for gLyr in grpLayers:
                    gLyrDec = arcpy.Describe(gLyr)
                    if gLyrDec.shapeType == 'Point':
                        gLyrsource = gLyrDec.catalogPath
                        gLyrsourceDir = os.path.dirname(os.path.dirname(gLyrsource))
                        oicFilePath = os.path.join(gLyrsourceDir,grpLayer.name+'.oic')
            with open(oicFilePath) as f:
                oic_file = json.load(f)
            if oic_file:
                    parameters[1].value = oic_file['properties']['Tags']
                    parameters[2].value = oic_file['properties']['Description']
            optionsDict = self.getOptions(parameters[0].valueAsText, oicFilePath)
            publishOptions = optionsDict['publishOptions']
            warningMessage = optionsDict['warningMessage']
            folderId = optionsDict['folderId']
            parameters[4].filter.list = publishOptions
            if (not parameters[4].altered) or (parameters[4].valueAsText not in publishOptions):
                parameters[4].value = publishOptions[0]
            if folderId:
                parameters[3].value = [folder['title'] for folder in folders if folder['id'] == folderId][0]
        if parameters[4].value in ['Publish all', 'Publish all - overwrite']:
            parameters[5].enabled = True
            if not parameters[5].altered:
                parameters[5].value = False
        else:
            parameters[5].enabled = False
            if not parameters[5].altered:
                parameters[5].value = False
        if parameters[4].altered and not parameters[4].hasBeenValidated:
            if parameters[4].value in ['Publish all', 'Publish all - overwrite']:
                parameters[5].enabled = True
                if not parameters[5].altered:
                    parameters[5].value = False
            else:
                parameters[5].enabled = False
                if not parameters[5].altered:
                    parameters[5].value = False


    def getOptions(self, oicParam, oicFilePath):
        warningMessage = ""
        try:
            gis = GIS(arcpy.GetActivePortalURL(), token=arcpy.GetSigninToken()['token'])
        except:
            return {
                       'publishOptions': ['Publish all', 'Publish all - overwrite', 'Publish Oriented Imagery Catalog item only',
                       'Publish Oriented Imagery Catalog item only - overwrite'],
                       'warningMessage': '',
                       'folderId': None
                   }
        publishOptions = ['Publish all', 'Publish all - overwrite', 'Publish Oriented Imagery Catalog item only',
                                  'Publish Oriented Imagery Catalog item only - overwrite']
        folderId = None
        if oicParam.lower().endswith('.oic'):
            oicFileName = os.path.splitext(os.path.basename(oicParam))[0]
        else:
            oicFileName = oicParam
        isReferenceOIC = oitools.isReferenceOIC(oicFilePath, oicFileName)
        oic_items = gis.content.search(query='title:'+ oicFileName +' AND type:Oriented Imagery Catalog AND owner:'+arcpy.GetPortalDescription(
            ).get('user').get('username'))
        oic_items = [oic_item for oic_item in oic_items if oic_item.title == oicFileName]
        if len(oic_items) > 1:
            warningMessage = "More than one Oriented Imagery Catalog item with the name " + oicFileName + " has been found. Click Run to continue with the first one."
            publishOptions = [opt for opt in publishOptions if opt not in ['Publish all', 'Publish Oriented Imagery Catalog item only']]
        elif len(oic_items) == 1:
            if isReferenceOIC:
                publishOptions = ['Publish Oriented Imagery Catalog item only - overwrite']
            else:
                publishOptions = [opt for opt in publishOptions if opt not in ['Publish all', 'Publish Oriented Imagery Catalog item only']]
            folderId = oic_items[0].ownerFolder
        else:
            if isReferenceOIC:
                publishOptions = ['Publish Oriented Imagery Catalog item only']
            else:
                featureServiceName = oitools.getFeatureServiceNameFromOIC(oicFilePath, oicFileName)
                fs_items = gis.content.search(query='title:'+ featureServiceName + ' AND type:Feature Service AND owner:'+arcpy.GetPortalDescription(
                    ).get('user').get('username'))
                fs_items = [fs_item for fs_item in fs_items if fs_item.title == oicFileName +'_ExposurePoints']
                if len(fs_items) != 0:
                    publishOptions = [opt for opt in publishOptions if opt not in ['Publish all', 'Publish Oriented Imagery Catalog item only']]
                else:
                    publishOptions = [opt for opt in publishOptions if opt not in ['Publish all - overwrite', 'Publish Oriented Imagery Catalog item only - overwrite']]
        return {'publishOptions': publishOptions,
                'warningMessage': warningMessage,
                'folderId': folderId}

    def updateMessages(self, parameters):
        global warningMessage
        global errorMessage

        if not oitools.isUserSignedIn():
            parameters[0].setErrorMessage("Please sign in to continue.")
        else:
            if errorMessage:
                parameters[0].setErrorMessage(errorMessage)
            else:
                if warningMessage:
                    parameters[0].setWarningMessage(warningMessage)
                else:
                    parameters[0].clearMessage()
        showCrashWarning(parameters)

    def execute(self,parameters,messages):
        try:
            log = initializeLog("PublishOrientedImageryCatalog")
            initializeVersionCheck(log)
            try:
                tokenDict = arcpy.GetSigninToken()
                portalToken = tokenDict['token']
            except:
                arcpy.AddMessage("Please login to your portal to continue.")
            isInputOICFile = False
            try:
                currProj = arcpy.mp.ArcGISProject("CURRENT")
            except:
                isInputOICFile = True
            if parameters[0].valueAsText.lower().endswith('.oic'):
                isInputOICFile = True
            if not isInputOICFile:
                currProj = arcpy.mp.ArcGISProject("CURRENT")
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
                    log.Message("Please ensure that the Oriented imagery catalog file "+ os.path.basename(oicFilePath) + " is present in " + os.path.dirname(oicFilePath),
                                log.const_critical_text)
                    closeLog(log)
                    return
            else:
                if not parameters[0].valueAsText.lower().endswith('.oic'):
                    arcpy.AddError("Only OIC file is supported as input in this mode.")
                    closeLog(log)
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
                    coverageLyr = arcpy.MakeFeatureLayer_management(coverageFCPath, os.path.splitext(os.path.basename(coverageFCPath))[0]).getOutput(0)
                    templateFolder = os.path.dirname(os.path.realpath(__file__))
                    currProj = arcpy.mp.ArcGISProject(os.path.join(templateFolder,'ProjectTemplate.aprx'))
                    currProj.importDocument(os.path.join(templateFolder,'MapTemplate.mapx'), False)
                    mapList = currProj.listMaps('MapTemplate')
                    if len(mapList) >= 1:
                        currMap = mapList[0]
                        currMap.addLayer(coverageLyr)
                        oitools.updateCoverageLayerSymbology(coverageLyr)
                        currMap.addLayer(pointLyr)
                    else:
                        log.Message("Error adding map to project template. Exiting..")
                        arcpy.AddError("Error adding map to project template. Exiting..")
                        return
                    pointLayer = currMap.listLayers()[0]
                    oitools.updatePointLayerSymbology(pointLayer)

            serviceTags = parameters[1].valueAsText
            tagsList = serviceTags.split(',')
            tagsList.append('OIC')
            oicTags = ','.join(set(tagsList))
            serviceDescription = parameters[2].valueAsText
            portal_desc = arcpy.GetPortalDescription()
            user_name = portal_desc['user']['username']
            portalurl = arcpy.GetActivePortalURL()
            orgName = portal_desc['name']
            serviceCredits = 'Copyright 2018 '+orgName+'.'+'Uploaded by '+user_name
            feature_service_util = FeatureServiceUtil(user_name,
                                                              portalurl)
            folder_id = None
            if parameters[3].value:
                folders = feature_service_util.list_all_portal_folders()
                folder_ids = [folder['id'] for folder in folders if folder['title'] == parameters[3].value]
                folder_id = folder_ids[0] if folder_ids else None
                if not folder_id:
                    arcpy.AddError("Folder does not exist in portal.")
                    log.Message("Folder does not exist in portal.", log.const_critical_text)
                    closeLog(log)
                    return
            try:
                with open(oicFilePath) as f:
                    oic_file = json.load(f)
            except Exception as e:
                arcpy.AddError('Error in reading Oriented Imagery Catalog file.')
                log.Message('Error in reading Oriented Imagery Catalog file.{}'.format(str(e)), log.const_critical_text)
                closeLog(log)
                return
            if parameters[4].valueAsText == 'Publish all' or parameters[4].valueAsText == 'Publish all - overwrite':
                default_share_settings = {'everyone': False, 'org': True, 'groups': None}
                if not pointFCPath:
                    arcpy.AddError("Exposure points feature class missing!")
                    log.Message("Exposure points feature class missing!", log.const_critical_text)
                    closeLog(log)
                    return
                if not vtpkFilePath:
                    arcpy.AddError("Coverage map feature class missing!")
                    log.Message("Coverage map feature class missing!", log.const_critical_text)
                    closeLog(log)
                    return
                fc_summary = "Oriented Imagery Catalog: "+os.path.basename(pointFCPath)+" created using the Oriented Imagery Catalog tool for ArcGIS Pro."
                vtpk_summary = "Oriented Imagery Catalog: "+os.path.basename(vtpkFilePath)+" created using the Oriented Imagery Catalog tool for ArcGIS Pro."
                if oic_file['properties']['ServiceURL']:
                    featureServiceName = oitools.getServiceNameFromOICJson(oic_file, 'FeatureServer')
                else:
                    featureServiceName = os.path.basename(pointFCPath)
                if oic_file['properties']['OverviewURL']:
                    coverageServiceName = oitools.getServiceNameFromOICJson(oic_file, 'VectorTileServer')
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
                    log.Message('Something went wrong before uploading the exposure points. {}'.format(str(e)), log.const_critical_text)
                    closeLog(log)
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
                        log.Message('Could not access the group layer.',  log.const_critical_text)
                        closeLog(log)
                        return
                    pointCoverageLayers = group_layer.listLayers()
                    pointLayers = [l for l in pointCoverageLayers if arcpy.Describe(l).shapeType == 'Point']
                    if not pointLayers:
                        arcpy.AddError('Could not access the feature service layer.')
                        log.Message('Could not access the feature service layer.',  log.const_critical_text)
                        closeLog(log)
                        return
                    pointLayer = pointLayers[0]
                currProj.save()
                #if oic_file['properties']['ServiceURL'] and parameters[4].valueAsText == 'Publish all':
                    #arcpy.AddMessage("The points feature service is already published. Skipping..")
                    #point_service_url = oic_file['properties']['ServiceURL']
                #else:
                arcpy.AddMessage("Publishing Exposure Points.")
                log.Message("Publishing Exposure Points.", log.const_general_text)
                if oic_file['properties']['ServiceURL']:
                    featureServiceName =  oitools.getServiceNameFromOICJson(oic_file, 'FeatureServer')
                else:
                    featureServiceName = os.path.basename(pointFCPath)
                    featureServiceNameAvailable = oitools.isServiceNameAvailable(os.path.basename(pointFCPath), log)
                    if not featureServiceNameAvailable:
                        featureServiceName = '{}_{}'.format(featureServiceName, oitools.getCurrentTimeStampStr())
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
                    log.Message(publish_fc_response['message'], log.const_critical_text)
                    closeLog(log)
                    return
                point_service_url = publish_fc_response['serviceurl']
                arcpy.AddMessage("Published Exposure Points.")
                log.Message("Published Exposure Points.", log.const_general_text)
                #Add attachments if option is checked
                if parameters[5].enabled and parameters[5].value:
                    arcpy.AddMessage("Enabling attachments")
                    #Enabling attachments on the feature service
                    updateResponse = oitools.updateFeatureDefinition(publish_fc_response['itemId'], {'hasAttachments': True})
                    arcpy.AddMessage("Attaching images..")
                    log.Message("Attaching images..", log.const_general_text)
                    #Attaching images to the feature service
                    oitools.addAttachmentsWithRetry(pointFCPath, publish_fc_response['itemId'], log)
                    log.Message('Updating image paths', log.const_general_text)
                    #Updating image paths for the rows with attachments to FA
                    oitools.updateImagePaths(publish_fc_response['itemId'], log)


                vtpk_item = [item for item in items if item['type'] == "Vector Tile Package"][0]
                vtpk_item_share_settings = vtpk_item['shared_with']
                if os.path.isfile(vtpkFilePath):
                    arcpy.AddMessage("Uploading Coverage Map..")
                    log.Message("Uploading Coverage Map..", log.const_general_text)
                    if oic_file['properties']['OverviewURL']:
                        vectorTileServiceName =  oitools.getServiceNameFromOICJson(oic_file, 'VectorTileServer')
                    else:
                        vectorTileServiceName = vtpkFileName
                        vectorTileServiceNameAvailable = oitools.isServiceNameAvailable(vectorTileServiceName, log, 'Vector Tile Service')
                        if not vectorTileServiceNameAvailable:
                            vectorTileServiceName = '{}_{}'.format(vectorTileServiceName, oitools.getCurrentTimeStampStr())
                    add_portal_item_response = feature_service_util.add_portal_item(
                                                                                    {"snippet": vtpk_item['summary'],
                                                                                     "title": vectorTileServiceName,
                                                                                     "accessInformation": vtpk_item['credits'],
                                                                                     "tags": vtpk_item['tags'],
                                                                                     "description": vtpk_item['description']},
                                                                                     vtpkFilePath, folder_id=folder_id)
                    if not add_portal_item_response.get('success'):
                        arcpy.AddError(add_portal_item_response['message'])
                        log.Message(add_portal_item_response['message'], log.const_critical_text)
                        closeLog(log)
                        return
                    log.Message("Uploaded Coverage Map", log.const_general_text)
                    share_response = feature_service_util.share_portal_item(portalurl, user_name,
                                                          add_portal_item_response.get('item_id'),
                                                          share_with_everyone=vtpk_item_share_settings['everyone'],
                                                          share_with_org=vtpk_item_share_settings['org'],
                                                          groups=vtpk_item_share_settings['groups'])
                    log.Message("Shared Coverage Map", log.const_general_text)
                    vector_tile_item = [item for item in items if item['type'] == "Vector Tile Service"][0]
                    vector_tile_item_share_settings = vector_tile_item['shared_with']
                    arcpy.AddMessage("Publishing Coverage Map..")
                    log.Message("Publishing Coverage Map..", log.const_general_text)
                    publish_vtpk_response = feature_service_util.publish_vtpk_item(
                                                                                   add_portal_item_response['item_id'],
                                                                                   vectorTileServiceName, folder_id)
                    if not publish_vtpk_response.get('success'):
                        arcpy.AddError(publish_vtpk_response['message'])
                        log.Message(publish_vtpk_response['message'], log.const_critical_text)
                        closeLog(log)
                        return
                    share_response = feature_service_util.share_portal_item(
                        portalurl,
                        user_name,
                        publish_vtpk_response['item_id'],
                        share_with_everyone=vector_tile_item_share_settings['everyone'],
                        share_with_org=vector_tile_item_share_settings['org'],
                        groups=vector_tile_item_share_settings['groups'])
                    polygon_service_url = publish_vtpk_response['serviceurl']
                arcpy.AddMessage("Published the Coverage Map.")
                log.Message("Published the Coverage Map.", log.const_general_text)
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
                    log.Message("The Oriented Imagery Catalog "+ oicFileName + " already exists.", log.const_critical_text)
                    closeLog(log)
                    return
            if parameters[4].valueAsText == 'Publish Oriented Imagery Catalog item only - overwrite' or parameters[4].valueAsText == 'Publish all - overwrite':
                if oic_item:
                    arcpy.AddMessage('Updating Oriented Imagery Catalog')
                    log.Message('Updating Oriented Imagery Catalog', log.const_general_text)
                    update_oic_response = feature_service_util.update_portal_item(oic_item.get('id'),
                                                                                  {"tags": oicTags,
                                                                                  "description": serviceDescription
                                                                                  },
                                                                                  data=json.dumps(oic_file))
                    move_response = feature_service_util.move_items(folder_id, [oic_item.get('id')])
                    if not update_oic_response.get('success'):
                        arcpy.AddError('Could not update OIC file!')
                        log.Message('Could not update OIC file!', log.const_critical_text)
                    closeLog(log)
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
                log.Message(add_oic_response['message'], log.const_critical_text)
            share_response = feature_service_util.share_portal_item(portalurl, user_name,
                                                                    add_oic_response['item_id'],
                                                                    False, True)
            closeLog(log)
        except:
            e = sys.exc_info()[1]
            arcpy.AddError(e.args[0])
            log.Message(e.args[0], log.const_critical_text)
            closeLog(log)

class CreateReferenceOrientedImageryCatalog(object):

    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Create Reference Oriented Imagery Catalog"
        self.description = ""
        self.canRunInBackground = False

    def getParameterInfo(self):
        inputOIC = arcpy.Parameter(
            displayName = "Input Oriented Imagery Catalog",
            name = "inputOIC",
            datatype=["DEFile","GPString"],
            parameterType = "Required",
            direction = "Input"
        )
        inputOIC.value = os.path.join(os.path.dirname(os.path.realpath(__file__)),'default.oic')

        outputFolder = arcpy.Parameter(
            displayName="Output Folder",
            name="outputFolder",
            datatype="DEWorkspace",
            parameterType="Required",
            direction="Input"
        )
        outputOICFileName = arcpy.Parameter(
            displayName="Output Oriented Imagery Catalog File Name",
            name="outputOICFileName",
            datatype="GPString",
            parameterType="Required",
            direction="Input"
        )
        tags = arcpy.Parameter(
            displayName="Tags",
            name="tags",
            datatype="GPString",
            parameterType="Required",
            direction="Input"
        )
        description = arcpy.Parameter(
            displayName="Description",
            name="description",
            datatype="GPString",
            parameterType="Required",
            direction="Input"
        )
        featureServiceURL = arcpy.Parameter(
            displayName="Feature service URL",
            name="featureServiceURL",
            datatype="GPString",
            parameterType="Required",
            direction="Input"
        )
        imageField = arcpy.Parameter(
            displayName="Image Field",
            name="imageField",
            datatype= 'GPString',
            parameterType="Optional",
            direction='Input'
        )
        coverageMapServiceURL = arcpy.Parameter(
                displayName="Coverage Map Service URL",
                name="coverageMapServiceURL",
                datatype= 'GPString',
                parameterType="Optional",
                direction='Input')


        parameters = [inputOIC, outputFolder, outputOICFileName, tags, description, featureServiceURL, imageField, coverageMapServiceURL]
        return parameters

    def get_item_data_from_item_url(self, token, item_url):
        try:
            if not token:
                return None
            get_details_url = item_url + "/data"
            params = {
                'f': 'pjson',
                'token': token
            }
            response = requests.get(get_details_url, params=params, verify=False)
            return response.json()
        except Exception as e:
            return None

    def mapParams(self, parameters_list):
        return {
                "inputOIC": parameters_list[0],
                "outputFolder": parameters_list[1],
                "outputOICFileName": parameters_list[2],
                "tags": parameters_list[3],
                "description": parameters_list[4],
                "featureServiceURL": parameters_list[5],
                "imageField": parameters_list[6],
                "coverageMapServiceURL": parameters_list[7]
             }

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        portal_desc = arcpy.GetPortalDescription()
        portalurl = arcpy.GetActivePortalURL()
        if portal_desc.get('user'):
            tokenDict = arcpy.GetSigninToken()
            portalToken = tokenDict['token']
            user_name = portal_desc['user']['username']
            feature_service_util = FeatureServiceUtil(user_name, portalurl)
        else:
            feature_service_util = None
            portalToken = None
        params = self.mapParams(parameters)
        if params['inputOIC'].altered and not params['inputOIC'].hasBeenValidated:
            if params['inputOIC'].valueAsText:
                oicFilePath = params['inputOIC'].valueAsText
                if oicFilePath.lower().startswith("http"):
                    if 'id=' in oicFilePath.lower():
                        item_id = oicFilePath.lower().split("id=")[1]
                        oicFilePath = portalurl + '/sharing/rest/content/items/' + item_id
                    oic_file = self.get_item_data_from_item_url(portalToken, oicFilePath)
                    if oic_file:
                        type_ = oic_file.get('type')
                        if type_ != 'OIC':
                            return
                    else:
                        return
                else:
                    with open(oicFilePath) as f:
                        oic_file = json.load(f)
                if oic_file:
                    params['tags'].value = oic_file['properties']['Tags']
                    params['description'].value = oic_file['properties']['Description']
                    params['featureServiceURL'].value = oic_file['properties']['ServiceURL']
                    params['coverageMapServiceURL'].value = oic_file['properties']['OverviewURL']
                    if not oic_file['properties']['ServiceURL']:
                        params['imageField'].filter.list = []
                        params['imageField'].value = ""
        if params['featureServiceURL'].altered and not params['featureServiceURL'].hasBeenValidated:
            if not feature_service_util:
                params['imageField'].filter.list = []
                params['imageField'].value = ""
            else:
                fields = feature_service_util.get_feature_service_string_fields(params['featureServiceURL'].valueAsText).get('fields')
                if fields:
                    params['imageField'].filter.list = fields
                    image_fields = [field for field in fields if 'image' in field.lower()]
                    if image_fields:
                        params['imageField'].value = image_fields[0]
                else:
                    params['imageField'].filter.list = []
                    params['imageField'].value = ""

    def updateMessages(self, parameters):
        showCrashWarning(parameters)
        if not oitools.isUserSignedIn():
            if parameters[0].valueAsText.lower().startswith("http"):
                parameters[0].setErrorMessage("Please sign in to continue.")
        else:
            parameters[0].clearMessage()


    def execute(self,parameters,messages):
        try:
            log = initializeLog("CreateReferenceOrientedImageryCatalog")
            initializeVersionCheck(log)
            params = self.mapParams(parameters)
            inputOIC = params['inputOIC'].valueAsText
            outputOICFileName = params['outputOICFileName'].valueAsText
            if not '.oic' in outputOICFileName:
                outputOICFileName = ''.join([outputOICFileName, '.oic'])
            outputFolder = params['outputFolder'].valueAsText
            outputOICFilePath = os.path.join(outputFolder, outputOICFileName)
            log.Message("Input OIC: {}".format(inputOIC), log.const_general_text)
            if inputOIC.lower().startswith("http"):
                tokenDict = arcpy.GetSigninToken()
                portalurl = arcpy.GetActivePortalURL()
                portalToken = tokenDict['token']
                if 'id=' in inputOIC.lower():
                    item_id = inputOIC.lower().split("id=")[1]
                    inputOIC = portalurl + '/sharing/rest/content/items/' + item_id
                oic_file_json = self.get_item_data_from_item_url(portalToken, inputOIC)
                if oic_file_json:
                    type_ = oic_file_json.get('type')
                    if type_ != 'OIC':
                        arcpy.AddError("Please enter a valid Oriented Imagery Catalog item URL.")
                        log.Message("Please enter a valid Oriented Imagery Catalog item URL.", log.const_critical_text)
                else:
                    arcpy.AddError("Please enter a valid Oriented Imagery Catalog item URL.")
                    log.Message("Please enter a valid Oriented Imagery Catalog item URL.", log.const_critical_text)
            else:
                with open(inputOIC) as f:
                    oic_file_json = json.load(f)
            if oic_file_json:
                oic_file_json['properties']['Name'] = os.path.splitext(os.path.basename(outputOICFileName))[0]
                oic_file_json['properties']['Tags'] = params['tags'].valueAsText
                oic_file_json['properties']['Description'] = params['description'].valueAsText
                oic_file_json['properties']['ServiceURL'] = params['featureServiceURL'].valueAsText
                oic_file_json['properties']['OverviewURL'] = params['coverageMapServiceURL'].valueAsText
                oic_file_json['properties']['imageField'] = params['imageField'].valueAsText
                log.Message('Creating a Reference Oriented Imagery Catalog..', log.const_general_text)
                with open(outputOICFilePath, 'w') as f:
                    json.dump(oic_file_json, f)
            closeLog(log)
        except Exception as e:
            arcpy.AddError('Something went wrong while creating the Reference Oriented Imagery Catalog. {}'.format(str(e)))
            log.Message('Something went wrong while creating the Reference Oriented Imagery Catalog. {}'.format(str(e)),
                        log.const_critical_text)
            closeLog(log)


class SetExposureStationID(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Set Exposure Station ID"
        self.description = ""
        self.canRunInBackground = False


    def getParameterInfo(self):

        inputOIC = arcpy.Parameter(
        displayName="Input Oriented Imagery Catalog",
        name="inputOIC",
        datatype=["DEFile", "GPGroupLayer"],
        parameterType="Required",
        direction="Input")


        sortField = arcpy.Parameter(
            displayName="Sort by :",
            name="sortField",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        sortField.filter.type = "ValueList"

        maxTimeBetweenSimilarExposures = arcpy.Parameter(
            displayName="Max time between similar exposures (seconds) :",
            name="maxTimeBetweenSimilarExposures",
            datatype="GPLong",
            parameterType="Required",
            direction="Input")

        startID = arcpy.Parameter(
            displayName="Start Exposure Station ID :",
            name="startID",
            datatype="GPLong",
            parameterType="Required",
            direction="Input")
        sortField.filter.type = "ValueList"

        params = [inputOIC, sortField, maxTimeBetweenSimilarExposures, startID]

        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        if parameters[0].altered:
            if not parameters[0].valueAsText.lower().endswith('.oic'):
                grpLayer = parameters[0].value
                grpLayers = grpLayer.listLayers()

                for gLyr in grpLayers:
                    gLyrDec = arcpy.Describe(gLyr)
                    if gLyrDec.shapeType == 'Point':
                        inputFeatureClass = gLyr
                        allFields = arcpy.ListFields(inputFeatureClass,'*')
                        fieldNames = []
                        for field in allFields:
                            fieldNames.append(field.name)
                        parameters[1].filter.list = fieldNames
            else:
                oicFilePath = parameters[0].valueAsText
                with open(oicFilePath) as oicFile:
                    oicDict = json.load(oicFile)
                featureClassPath = oicDict['properties']['PointsSource']
                allFields = arcpy.ListFields(featureClassPath,'*')
                fieldNames = []
                for field in allFields:
                    fieldNames.append(field.name)
                parameters[1].filter.list = fieldNames

    def updateMessages(self, parameters):
        showCrashWarning(parameters)

    def execute(self,parameters,messages):
        try:
            log = initializeLog('GroupImages')
            initializeVersionCheck(log)
            isInputOICFile = False
            try:
                currProj = arcpy.mp.ArcGISProject("CURRENT")
            except:
                isInputOICFile = True
            if parameters[0].valueAsText.lower().endswith('.oic'):
                isInputOICFile = True
            if not isInputOICFile:
                grpLayer = parameters[0].value
                grpLayers = grpLayer.listLayers()

                for gLyr in grpLayers:
                    gLyrDec = arcpy.Describe(gLyr)
                    if gLyrDec.shapeType == 'Point':
                        inFeatureClass = gLyr
                        break
            else:
                oicFilePath = parameters[0].valueAsText
                with open(oicFilePath) as oicFile:
                    oicDict = json.load(oicFile)
                inFeatureClass = oicDict['properties']['PointsSource']

            if len(arcpy.ListFields(inFeatureClass,'AcquisitionDate')) == 0:
                arcpy.AddError("Could not find Field: AcquisitionDate")
                log.Message("Could not find Field: AcquisitionDate", log.const_critical_text)
                exit(1)

            if len(arcpy.ListFields(inFeatureClass,'ExposureStation')) == 0:
                arcpy.AddField_management(inFeatureClass, 'ExposureStation', "LONG")

            inFldNames = []
            inFldNames.append('AcquisitionDate')
            inFldNames.append('ExposureStation')
            inFldNames.append('SHAPE@XY')

            desc = arcpy.Describe(inFeatureClass)
            anSRS = desc.spatialReference
            try:
                selString = desc.FIDSet
            except:
                selString = ''
            if selString =='':
                selType = 'NEW_SELECTION'
                selQuery = ''
            else:
                selType = 'SUBSET_SELECTION'
                selQuery= 'OBJECTID IN ('+selString.replace(';',',')+')'

            orderby_clause = (None,'ORDER BY '+parameters[1].valueAsText)

            if desc.datatype == 'FeatureLayer':
                inSearchCursor = arcpy.da.SearchCursor(inFeatureClass,inFldNames,selQuery,sql_clause=orderby_clause)

                inupdateCursor = arcpy.da.UpdateCursor(inFeatureClass,inFldNames,selQuery,sql_clause=orderby_clause)
            elif desc.datatype == 'FeatureClass':
                outPath = desc.catalogPath
                inSearchCursor = arcpy.da.UpdateCursor(outPath,inFldNames,selQuery,sql_clause=orderby_clause)
                inupdateCursor = arcpy.da.UpdateCursor(outPath,inFldNames,selQuery,sql_clause=orderby_clause)
                inFeatureClass = arcpy.MakeFeatureLayer_management (outPath, desc.name+'_temp')
            else:
                arcpy.AddMessage('No Feature Layer found.')
                log.Message('No Feature Layer found.', log.const_general_text)
                exit(1)

            startRecID = 0
            startExposureID = parameters[3].value

            exposureID = startExposureID

            updateNext = False
            lastExposureIDUsed = None
            recSequence = -1

            updateList = []

            arcpy.AddMessage('Calculating Station IDs')
            log.Message('Calculating Station IDs', log.const_general_text)
            with inSearchCursor:
                for row in inSearchCursor:
                    recSequence = recSequence + 1

                    if recSequence == 0:
                        prevDate = row[0]
                    elif recSequence == 1:
                        currDate = row[0]
                        dateDiff = currDate - prevDate
                        if dateDiff.total_seconds() <= parameters[2].value:
                            updateList.insert(recSequence-1,exposureID)
                            updateList.insert(recSequence,exposureID)

                            #arcpy.AddMessage("Record 2 (True):"+'Exposure ID: '+'previous Date: '+str(prevDate)+'current Date: '+str(currDate)+'Date Diff: '+str(dateDiff.total_seconds())+'Exposure ID: '+str(exposureID)+' Last Exposure ID: '+str(lastExposureIDUsed))
                            prevDate = currDate
                            lastExposureIDUsed = exposureID
                        else:
                            updateList.insert(recSequence,-999)
                            #arcpy.AddMessage("Record 2 (False):"+'Exposure ID: '+'previous Date: '+str(prevDate)+'current Date: '+str(currDate)+'Date Diff: '+str(dateDiff.total_seconds())+'Exposure ID: '+str(exposureID)+' Last Exposure ID: '+str(lastExposureIDUsed))
                            prevDate = currDate
                    else:
                        currDate = row[0]
                        dateDiff = currDate - prevDate
                        if dateDiff.total_seconds() <= parameters[2].value:
                            updateList.insert(recSequence-1,exposureID)
                            updateList.insert(recSequence,exposureID)
    #                        arcpy.AddMessage("Record 2+ (True):"+'Exposure ID: '+'previous Date: '+str(prevDate)+'current Date: '+str(currDate)+'Date Diff: '+str(dateDiff.total_seconds())+'Exposure ID: '+str(exposureID)+' Last Exposure ID: '+str(lastExposureIDUsed))
                            prevDate = currDate
                            lastExposureIDUsed = exposureID

                        else:
                            updateList.insert(recSequence,-999)
    #                        arcpy.AddMessage("Record 2+ (False):"+'Exposure ID: '+'previous Date: '+str(prevDate)+'current Date: '+str(currDate)+'Date Diff: '+str(dateDiff.total_seconds())+'Exposure ID: '+str(exposureID)+' Last Exposure ID: '+str(lastExposureIDUsed))
                            prevDate = currDate
                            exposureID = exposureID + 1
                            if exposureID - lastExposureIDUsed > 1:
                                exposureID = lastExposureIDUsed + 1

            del row

            arcpy.AddMessage('Updating Station IDs')
            log.Message('Updating Station IDs', log.const_general_text)
            listseq = -1
            shapesDict = {}


            with inupdateCursor:
                for row in inupdateCursor:
                    listseq = listseq + 1
                    aVal = updateList[listseq]
                    if aVal == -999:
                        row[1] = None
                    else:

                        row[1] = aVal
                        x, y = row[2]
                        if aVal in shapesDict:
                            aXYList = shapesDict[aVal]
                            aXYList.append([x,y])
                            shapesDict[aVal] = aXYList
                        else:
                            aXYList = []
                            aXYList.append([x,y])
                            shapesDict[aVal] = aXYList

                    inupdateCursor.updateRow(row)

            del row

            arcpy.AddMessage("Averaging Shapes")
            log.Message("Averaging Shapes", log.const_general_text)
            for selID in range(startExposureID,lastExposureIDUsed):
                arcpy.SelectLayerByAttribute_management(inFeatureClass,"NEW_SELECTION",'ExposureStation = '+str(selID))
                try:
                    selString = desc.FIDSet
                except:
                    selString = ''
                if selString != '':
                    arcpy.AddMessage("Editing Exposure ID: "+str(selID))
                    log.Message("Editing Exposure ID: "+str(selID), log.const_general_text)
                    pointsList = shapesDict[selID]
                    allptx = 0
                    allpty = 0

                    for pt in pointsList:
                        ptx = pt[0]
                        pty = pt[1]

                        allptx = allptx + ptx
                        allpty = allpty + pty

                    avgPtX = allptx / len(pointsList)
                    avgPtY = allpty / len(pointsList)

                    updateCode = "def updatepoint(x,y,anSRS):\n	aPoint = arcpy.Point()\n	aPoint.X = x\n	aPoint.Y = y\n	aPtGeometry = arcpy.PointGeometry(aPoint,anSRS)\n	return aPtGeometry"
                    shapeFldName = 'Shape'
                    expression = "updatepoint("+str(avgPtX)+','+str(avgPtY)+','+str(anSRS.factoryCode)+')'
                    arcpy.CalculateField_management(inFeatureClass,shapeFldName,expression,"PYTHON3",updateCode)

            arcpy.AddMessage("Points grouped. You can now make selections based on the Field ExposureStation.")
            log.Message("Points grouped. You can now make selections based on the Field ExposureStation.",
                        log.const_general_text)
            closeLog(log)
        except Exception as e:
            arcpy.AddError("Error in GroupImages: {}".format(str(e)))
            log.Message("Error in GroupImages: {}".format(str(e)), log.const_critical_text)
            closeLog(log)
        #DisaplaySelectByLayerWarning()

def traverse(path, obj):
    """
    Traverse the object recursively and print every path / value pairs.
    """
    cnt = -1
    if isinstance(obj, dict):
        d = obj

        for k, v in d.items():
            if isinstance(v, dict):
                traverse(path + "." + k, v)
            elif isinstance(v, list):
                traverse(path + "." + k, v)
            else:
                #print(path + "." + k, "=>", v)
                propertiesAsList.append([str(path),str(k),str(v)])
    if isinstance(obj, list):
        li = obj
        for e in li:
            cnt += 1
            if isinstance(e, dict):
                traverse("{path}[{cnt}]".format(path=path, cnt=cnt), e)
            elif isinstance(e, list):
                traverse("{path}[{cnt}]".format(path=path, cnt=cnt), e)
            else:
                #print("{path}[{cnt}] => {e}".format(path=path, cnt=cnt, e=e))
                propertiesAsList.append([str(path),str(cnt),str(e)])

class Properties(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Properties"
        self.description = ""
        self.canRunInBackground = False

    def returURLContents(self, token, item_url):
        try:
            if not token:
                return None
            get_details_url = item_url + "/data"
            params = {
                'f': 'pjson',
                'token': token
            }
            response = requests.get(get_details_url, params=params, verify=False)
            return response.json()
        except Exception as e:
            return None

    def getParameterInfo(self):

        OICInput = arcpy.Parameter(
        displayName="Input Oriented Imagery Catalog",
        name="OICInput",
        datatype=["DEFile","GPGroupLayer"],
        parameterType="Required",
        direction="Input")

        properties = arcpy.Parameter(
        displayName='Properties:',
        name='Properties',
        datatype='GPValueTable',
        parameterType='Optional',
        direction='Input')
        properties.columns = [['GPString', 'Property'], ['GPString', 'Value']]
        properties.enabled = True

        params = [OICInput,properties]

        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        global propertiesAsList
        if parameters[0].valueAsText:
            oicFilePath = parameters[0].valueAsText

            if oicFilePath.startswith('\\') or oicFilePath[1] == ':':
                with open(oicFilePath) as f:
                    oic_file = json.load(f)
            else:
                grpLayer = parameters[0].value
                grpLayers = grpLayer.listLayers()
                for gLyr in grpLayers:
                    gLyrDec = arcpy.Describe(gLyr)
                    if gLyrDec.shapeType == 'Point':
                        coverageFCPath = gLyr.dataSource
                        gLyrsource = gLyrDec.catalogPath
                        gLyrsourceDir = os.path.dirname(os.path.dirname(gLyrsource))
                        oicFilePath = os.path.join(gLyrsourceDir,grpLayer.name+'.oic')

                        with open(oicFilePath) as f:
                            oic_file = json.load(f)
        else:
            parameters[1].value = None

        if parameters[0].altered and not parameters[0].hasBeenValidated:
                propertiesAsList = []
                traverse("root", oic_file)
                tableList = []

                for jVal in propertiesAsList:
                    prop = jVal[0].replace('root','')
                    prop = prop.strip('.')
                    prop = prop.replace('.',':')
                    prop = prop.replace('properties','')
                    #prop = prop.strip(':')

                    propertyVal = prop+':'+jVal[1]
                    propertyVal = propertyVal.strip(':')

                    if ('version' in propertyVal) or ('type' in propertyVal):
                        continue
                    else:
                        tableList.append([propertyVal,jVal[2]])
                parameters[1].value = tableList

    def updateMessages(self, parameters):

        if not oitools.isUserSignedIn():
            if not parameters[0].value is None:
                if parameters[0].valueAsText.lower().startswith("http"):
                    parameters[0].setErrorMessage("Please sign in to continue.")
        else:
            parameters[0].clearMessage()
        showCrashWarning(parameters)
    def execute(self,parameters,messages):
        try:
            log = initializeLog("Properties")
            initializeVersionCheck(log)
            inOIC = parameters[0].valueAsText
            oicFilePath = parameters[0].valueAsText
            if oicFilePath.startswith('\\') or oicFilePath[1] == ':':
                with open(oicFilePath) as f:
                    oic_file = json.load(f)
                f.close
            else:
                grpLayer = parameters[0].value
                grpLayers = grpLayer.listLayers()
                for gLyr in grpLayers:
                    gLyrDec = arcpy.Describe(gLyr)
                    if gLyrDec.shapeType == 'Point':
                        coverageFCPath = gLyr.dataSource
                        gLyrsource = gLyrDec.catalogPath
                        gLyrsourceDir = os.path.dirname(os.path.dirname(gLyrsource))
                        oicFilePath = os.path.join(gLyrsourceDir,grpLayer.name+'.oic')

                        with open(oicFilePath) as f:
                            oic_file = json.load(f)
                        f.close

            oicEditedValues = parameters[1].value
            log.Message('Parameters: {}'.format(str(oicEditedValues)), log.const_general_text)
            arcpy.AddMessage(str(oicEditedValues))
            arcpy.AddMessage(type(oicEditedValues))
            arcpy.AddMessage(type(oic_file))
            updateOICData = oitools.updateOICProperties(oic_file,oicEditedValues)
            with open(oicFilePath, 'w') as outfile:
                json.dump(updateOICData, outfile)
            closeLog(log)
        except Exception as e:
            arcpy.AddError("Error in Properties: {}".format(str(e)))
            log.Message("Error in Properties: {}".format(str(e)), log.const_critical_text)
            closeLog(log)


class CalculateHeading(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Calculate Heading"
        self.description = ""
        self.canRunInBackground = False

    def getParameterInfo(self):

        inputCatalog = arcpy.Parameter(
        displayName="Input Oriented Imagery Catalog",
        name="inputCatalog",
        datatype=["DEFile","GPGroupLayer"],
        parameterType="Required",
        direction="Input")

        minDist = arcpy.Parameter(
        displayName="Minium Distance (m)",
        name="minDist",
        datatype="GPLong",
        parameterType="Required",
        direction="Input")
        minDist.values = 3

        maxDistance = arcpy.Parameter(
        displayName="Maximum Distance (m)",
        name="maxDistance",
        datatype="GPLong",
        parameterType="Required",
        direction="Input")
        maxDistance.value = 100

        headingOffset = arcpy.Parameter(
        displayName="Heading Offset",
        name="headingOffset",
        datatype="GPLong",
        parameterType="Required",
        direction="Input")
        headingOffset.value = 0

        params = [inputCatalog,minDist,maxDistance,headingOffset]

        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        pass

    def updateMessages(self, parameters):
        showCrashWarning(parameters)

    def getReprojectedPoints(self, x1, y1, inputSRS, ouputSRS):
        point = arcpy.Point()
        point.X = x1
        point.Y = y1
        pointGeometry = arcpy.PointGeometry(point, inputSRS).projectAs(ouputSRS)
        return (pointGeometry.centroid.X, pointGeometry.centroid.Y)

    def execute(self,parameters,messages):

        log = initializeLog('CalculateHeading')
        isInputOICFile = False
        try:
            currProj = arcpy.mp.ArcGISProject("CURRENT")
        except:
            isInputOICFile = True
        if parameters[0].valueAsText.lower().endswith('.oic'):
            isInputOICFile = True
        try:
            if not isInputOICFile:
                grpLayer = parameters[0].value
                grpLayers = grpLayer.listLayers()

                for gLyr in grpLayers:
                    gLyrDec = arcpy.Describe(gLyr)
                    if gLyrDec.shapeType == 'Point':
                        inputFeatureClass = gLyr
                        gLyrsource = gLyrDec.catalogPath
                        gLyrsourceDir = os.path.dirname(os.path.dirname(gLyrsource))
                        oicFilePath = os.path.join(gLyrsourceDir,grpLayer.name+'.oic')
            else:
                oicFilePath = parameters[0].valueAsText
                with open(oicFilePath) as oicFile:
                    oicDict = json.load(oicFile)
                inputFeatureClass = oicDict['properties']['PointsSource']

            searchFieldNames = ['SHAPE@']

            fieldList = arcpy.ListFields(inputFeatureClass,'CamHeading')
            if len(fieldList) == 0:
                arcpy.AddMessage('Adding Field: CamHeading.')
                log.Message("Adding Field: CamHeading.", log.const_general_text)
                arcpy.AddField_management(inputFeatureClass, 'CamHeading', "FLOAT")

            updateFieldNames = ['CamHeading']

            desc = arcpy.Describe(inputFeatureClass)
            if hasattr(desc, "layer"):
                outPath = desc.layer.catalogPath
                inSearchCursor = arcpy.da.SearchCursor(outPath,searchFieldNames,sql_clause=(None,'ORDER BY Name'))
                outUpdateCursor = arcpy.da.UpdateCursor(outPath,updateFieldNames)
            else:
                outPath = desc.catalogPath
                inSearchCursor = arcpy.da.SearchCursor(outPath,searchFieldNames,sql_clause=(None,'ORDER BY Name'))
                outUpdateCursor = arcpy.da.UpdateCursor(outPath,updateFieldNames)
            fcSRS = desc.spatialReference
            fcSRSCode = fcSRS.factoryCode
            webMercSRS = arcpy.SpatialReference(3857)

            minDistance = int(parameters[1].valueAsText)
            maxDistance = int(parameters[2].valueAsText)
            headOffSet = int(parameters[3].valueAsText)

            count = int(arcpy.GetCount_management(inputFeatureClass)[0])

            inRows = [inRow for inRow in inSearchCursor]
            inRow = inRows[0]
            inShape = inRow[0]
            x1 = inShape.centroid.X
            y1 = inShape.centroid.Y
            if fcSRSCode != 3857:
                #reproject to web mercator.
                x1, y1 = self.getReprojectedPoints(x1, y1, fcSRS, webMercSRS)
            camHeadPrev = None
            try:
                for index, row in enumerate(outUpdateCursor):
                    try:
                        if index < count-1:
                            #arcpy.AddMessage("index:{}".format(index))
                            inRow = inRows[index+1]
                            inShape = inRow[0]
                            x2 = inShape.centroid.X
                            y2 = inShape.centroid.Y
                            if fcSRSCode != 3857:
                                #reproject to web mercator.
                                x2, y2 = self.getReprojectedPoints(x2, y2, fcSRS, webMercSRS)

                            distanceX = x2 - x1
                            distanceY = y2 - y1

                            distance = math.sqrt(distanceX**2 + distanceY**2)

                            camHead = -1
                            #arcpy.AddMessage("distance:{}".format(distance))
                            #arcpy.AddMessage("minDistance:{}".format(minDistance))
                            #arcpy.AddMessage("maxDistance:{}".format(maxDistance))
                            if (distance > minDistance) and (distance < maxDistance):

                                camHead = math.degrees((math.atan2(distanceX,distanceY))) + headOffSet
                                if camHead < 0:
                                    camHead = camHead + 360

                            if camHeadPrev and distance < minDistance :
                                camHead = camHeadPrev

                            x1 = x2
                            y1 = y2
                            #arcpy.AddMessage("CamHeading:{}".format(camHead))
                            row[0] = camHead
                            outUpdateCursor.updateRow(row)
                            camHeadPrev = camHead
                        else:
                            #Last Record.
                            row[0] = camHeadPrev
                            outUpdateCursor.updateRow(row)
                    except Exception as e:
                        arcpy.AddError("Error in computing camHeading for row number: {}(row number 0 indicates the first row)".format(index))
            except Exception as e:
                arcpy.AddError("{}. Please try closing the attribute table.".format(str(e)))
            closeLog(log)
        except Exception as e:
            arcpy.AddError("Error in calculating camHeading: {}".format(str(e)))
            log.Message("Error in calculating camHeading: {}".format(str(e)), log.const_critical_text)
            closeLog(log)
class AddOrientedImageryFields(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Add Oriented Imagery Fields"
        self.description = ""
        self.canRunInBackground = False

    def getParameterInfo(self):

        inputCatalog = arcpy.Parameter(
        displayName="Input Oriented Imagery Catalog",
        name="inputCatalog",
        datatype=["DEFile","GPGroupLayer"],
        parameterType="Required",
        direction="Input")

        fieldList = arcpy.Parameter(
        displayName="Fields to add:",
        name="fieldList",
        datatype="GPString",
        parameterType="Required",
        direction="Input")
        fieldList.filter.type = "ValueList"
        fieldList.enabled = True



        fieldValueList = arcpy.Parameter(
        displayName='Fields List:',
        name='fieldValueList',
        datatype='GPValueTable',
        parameterType='Optional',
        direction='Input')
        fieldValueList.columns = [['GPString', 'Field'], ['GPString', 'Value']]
        #fieldValueList.columns = [['GPBoolean', 'Field'], ['GPString', 'Value']]
        fieldValueList.enabled = True


        params = [inputCatalog,fieldList,fieldValueList]

        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):


        fieldListValues = []
        fieldListValues.append('CamHeading')
        fieldListValues.append('CamPitch')
        fieldListValues.append('CamRoll')
        fieldListValues.append('HFOV')
        fieldListValues.append('VFOV')
        fieldListValues.append('AvgHtAG')
        fieldListValues.append('FarDist')
        fieldListValues.append('NearDist')
        fieldListValues.append('OIType')
        fieldListValues.append('SortOrder')
        fieldListValues.append('CamOffset')
        fieldListValues.append('Accuracy')
        fieldListValues.append('ImgPyramids')
        fieldListValues.append('DepthImg')
        fieldListValues.append('CamOri')
        fieldListValues.append('ImgRot')

        if parameters[0].altered and not parameters[0].hasBeenValidated:

            if parameters[0].valueAsText.lower().endswith('.oic'):
                isInputOICFile = True
            else:
                isInputOICFile = False

            if not isInputOICFile:
                grpLayer = parameters[0].value
                grpLayers = grpLayer.listLayers()

                defprops = {}

                for gLyr in grpLayers:
                    gLyrDec = arcpy.Describe(gLyr)
                    if gLyrDec.shapeType == 'Point':
                        inputFeatureClass = gLyr
                        gLyrsource = gLyrDec.catalogPath
                        gLyrsourceDir = os.path.dirname(os.path.dirname(gLyrsource))
                        oicFilePath = os.path.join(gLyrsourceDir,grpLayer.name+'.oic')
                        try :
                            with open(oicFilePath) as f:
                                oic_file = json.load(f)
                            defprops = oic_file['properties']['DefaultAttributes']

                        except:
                            defprops = {}
            else:
                oicFilePath = parameters[0].valueAsText
                with open(oicFilePath) as f:
                    oic_file = json.load(f)
                defprops = oic_file['properties']['DefaultAttributes']

                inputFeatureClass = oic_file['properties']['PointsSource']

            fieldList = arcpy.ListFields(inputFeatureClass,'*')

            for fld in fieldList:
                if ((fld.name).lower() != 'objectid') and ((fld.name).lower() != 'shape'):
                    try:
                        fldidx = fieldListValues.index(fld.name)
                        fieldListValues.remove(fld.name)
                    except:
                        pass
            parameters[1].filter.list = fieldListValues
            parameters[1].value = None
            parameters[2].value = None

        if parameters[1].altered and not parameters[1].hasBeenValidated:
            afldNameToCheck = parameters[1].valueAsText
            if afldNameToCheck != None:

                tableList = parameters[2].value
                if tableList != None:
                    found = False
                    for val in tableList:
                        if val[0] == afldNameToCheck:
                            found = True
                            break
                    if not found:
                        tableList.append([afldNameToCheck,""])
                        parameters[2].value = tableList
                        #if parameters[2].hasBeenValidated:
                        #parameters[1].filter.list = []
                        #parameters[1].filter.list = fieldListValues
                else:
                    parameters[2].value = [[afldNameToCheck,""]]
                    #if parameters[2].hasBeenValidated:
                    #parameters[1].filter.list = []
                    #parameters[1].filter.list = fieldListValues


    def updateMessages(self, parameters):
        showCrashWarning(parameters)

    def execute(self,parameters,messages):

        if parameters[0].valueAsText.lower().endswith('.oic'):
            isInputOICFile = True
        else:
            isInputOICFile = False

        if not isInputOICFile:
            grpLayer = parameters[0].value
            grpLayers = grpLayer.listLayers()

            defprops = {}

            for gLyr in grpLayers:
                gLyrDec = arcpy.Describe(gLyr)
                if gLyrDec.shapeType == 'Point':
                    #arcpy.AddMessage("Point Featur Layer")

                    ifc = gLyr
                    selString = gLyrDec.FIDSet

                    if selString =='':
                        selType = 'NEW_SELECTION'
                        selQuery = ''
                    else:
                        selType = 'SUBSET_SELECTION'
                        selQuery= 'OBJECTID IN ('+selString.replace(';',',')+')'

                    gLyrsource = gLyrDec.catalogPath
                    gLyrsourceDir = os.path.dirname(os.path.dirname(gLyrsource))
                    oicFilePath = os.path.join(gLyrsourceDir,grpLayer.name+'.oic')

                    inputFeatureClass = gLyrDec.name+'1'
                    #arcpy.MakeFeatureLayer_management(ifc,inputFeatureClass,'"'+selQuery+'"')

                    arcpy.MakeTableView_management(ifc,inputFeatureClass,selQuery)


                    try :
                        with open(oicFilePath) as f:
                            oic_file = json.load(f)
                        defprops = oic_file['properties']['DefaultAttributes']
                        break

                    except:
                        defprops = {}
        else:
            oicFilePath = parameters[0].valueAsText
            with open(oicFilePath) as f:
                oic_file = json.load(f)
            defprops = oic_file['properties']['DefaultAttributes']

            inputFeatureClass = oic_file['properties']['PointsSource']

        fldValList = parameters[2].value

        for fldval in fldValList:
            fldname = fldval[0]
            fVal = fldval[1]
            addedFields = oitools.addMissingFields(inputFeatureClass,[fldname])

            chkFldList = arcpy.ListFields(inputFeatureClass,fldname)

            if len(chkFldList) == 1:

                fld = chkFldList[0]
                if fld.type == 'String':
                    arcpy.CalculateField_management(inputFeatureClass,fldname,'"'+ fVal +'"',"PYTHON3")
                else:
                    arcpy.CalculateField_management(inputFeatureClass,fldname,fVal,"PYTHON3")