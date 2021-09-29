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
# Name: OICTypes.py
# Description: This script is used to load other OIC Types from the Types folder into memory. An OIC type is a pyton script that will load data into and OIC.
# Version: 2.3
# Date Created : 20181009
# Date updated : 20191126
# Requirements: ArcGIS Pro 2.2
# Author: Esri Imagery Workflows team
#------------------------------------------------------------------------------

import os
import sys
import importlib
import arcpy

class OICType:

    def __init__(self, nametype):
        self._name = nametype
        pass
    def init(self):
        oicTypePyFN = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))),'Types\\'+self._name+'.py')

        #print oicTypePyFN
        if os.path.isfile(oicTypePyFN) == True:
            return True
        else:
            return False

    def run(self, oicpath, custParas, inputParams, defaultValues, log=None):

        typesImportFolder = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))),'Types')

        sys.path.append(typesImportFolder)

        packageToImport = self._name
        try:

            oictype = __import__(packageToImport, globals(), locals(), [packageToImport], 0)

            arcpy.AddMessage("Calling " + packageToImport)
            aMsg = oictype.main(oicpath, custParas, inputParams, defaultValues, log)
            if 'error' in aMsg.lower():
                if log:
                    log.Message(aMsg, log.const_critical_text)
                arcpy.AddError(aMsg)
            else:
                if log:
                    log.Message(aMsg, log.const_general_text)
                arcpy.AddMessage(aMsg)

        except Exception as x:
            if log:
                log.Message("OIC Type Error: {}".format(str(x)), log.const_critical_text)
            arcpy.AddError ("OIC Type Error: "+str(x))
            return False




