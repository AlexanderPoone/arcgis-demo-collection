#------------------------------------------------------------------------------
# Copyright 2013 Esri
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
# Name: FrameCamera.py
# Description: A class to read the eo file and generate required Frame and Camera tables.
# Version: 2.3
# Date Created : 20171217
# Date updated : 20200305
# Requirements: ArcGIS 10.5.1
# Author: Esri Imagery Workflows team
#------------------------------------------------------------------------------

import os
import sys
import arcpy
import argparse
import datetime
import re
import arcpy.cartography as CA
import math
import numpy as np
from numpy.linalg import inv
class FrameCamera:

    def __init__(self, log):
        self.log = log

    def addFrameField1(self,inTable):
        try:
            arcpy.AddField_management(inTable,'ImageID','TEXT','#','#',60)
            arcpy.AddField_management(inTable,'Raster','TEXT','#','#',3000)
            arcpy.AddField_management(inTable,'PerspectiveX','DOUBLE')
            arcpy.AddField_management(inTable,'PerspectiveY','DOUBLE')
            arcpy.AddField_management(inTable,'PerspectiveZ','DOUBLE')
            arcpy.AddField_management(inTable,'Omega','DOUBLE')
            arcpy.AddField_management(inTable,'Phi','DOUBLE')
            arcpy.AddField_management(inTable,'Kappa','DOUBLE')
            arcpy.AddField_management(inTable,'CameraID','TEXT','#','#',40)
            arcpy.AddField_management(inTable,'SRS','TEXT','#','#',15)
            arcpy.AddField_management(inTable,'ProductName','TEXT','#','#',15)
            arcpy.AddField_management(inTable,'AcquisitionDate','Date')
            arcpy.AddField_management(inTable,'AverageZ','DOUBLE')
        except Exception as exp:
            self.log.Message(str(exp), self.log.const_critical_text)
            return False

    def addFrameField2(self,inTable):
        try:
            arcpy.AddField_management(inTable,'Latitude','DOUBLE')
            arcpy.AddField_management(inTable,'Longitude','DOUBLE')
            arcpy.AddField_management(inTable,'Event','DOUBLE')
            arcpy.AddField_management(inTable,'TimeInSeconds','Double')
        except Exception as exp:
            self.log.Message(str(exp), self.log.const_critical_text)
            return False

    def addFrameFieldSanborn(self,inTable):
        try:
            arcpy.AddField_management(inTable,'Flightline','TEXT','#','#',30)
            arcpy.AddField_management(inTable,'ShotID','TEXT','#','#',100)
        except Exception as exp:
            self.log.Message(str(exp), self.log.const_critical_text)
            return False


    def addCameraFields(self,inTable):
        try:
            arcpy.AddField_management(inTable,'FocalLength','DOUBLE')
            arcpy.AddField_management(inTable,'PrincipalX','DOUBLE')
            arcpy.AddField_management(inTable,'PrincipalY','DOUBLE')
            arcpy.AddField_management(inTable,'A0','DOUBLE')
            arcpy.AddField_management(inTable,'A1','DOUBLE')
            arcpy.AddField_management(inTable,'A2','DOUBLE')
            arcpy.AddField_management(inTable,'B0','DOUBLE')
            arcpy.AddField_management(inTable,'B1','DOUBLE')
            arcpy.AddField_management(inTable,'B2','DOUBLE')
            arcpy.AddField_management(inTable,'CameraID','TEXT','#','#',40)
            arcpy.AddField_management(inTable,'Camera_SerialID','TEXT','#','#',50)
            arcpy.AddField_management(inTable,'Camera_Type','TEXT','#','#',40)
        except Exception as exp:
            self.log.Message(str(exp), self.log.const_critical_text)
            return False

    def addCameraFields2(self,inTable):
        try:
            arcpy.AddField_management(inTable,'DistortionType','TEXT','#','#',40)
            arcpy.AddField_management(inTable,'Radial','TEXT','#','#',200)
            arcpy.AddField_management(inTable,'Tangential','TEXT','#','#',200)
        except Exception as exp:
            self.log.Message(str(exp), self.log.const_critical_text)
            return False

    def select_range(self,filename, start_range, end_range):
        try:
            f = open(filename, 'r')
            selected_lines = []
            start = 0
            for line in f:
                if (start_range in line):
                    start = 1

                if (end_range in line):
                    start = 0
                    selected_lines.append(line)
                    return selected_lines
                if (start == 1):
                    selected_lines.append(line)
            f.close()
            return selected_lines
        except Exception as exp:
            self.log.Message(str(exp), self.log.const_critical_text)

    def select_range_endfile(self,filename, start_range):
        try:
            f = open(filename, 'r')
            selected_lines = []
            start = 0
            for line in f:
                if (start_range in line):
                    start = 1

                if (start == 1):
                    selected_lines.append(line)
            f.close()
            return selected_lines
        except Exception as exp:
            self.log.Message(str(exp), self.log.const_critical_text)

    def select_range_endlist(self,list, start_range):
        try:
            selected_lines = []
            start = 0
            for line in list:
                if (line.split(";")[0].__contains__(start_range)):
                    start = 1

                if (start == 1):
                    selected_lines.append(line)
            return selected_lines
        except Exception as exp:
            self.log.Message(str(exp), self.log.const_critical_text)

    def select_range_file(self,filename, start_range, end_range):
        try:
            f = open(filename, 'r')
            selected_lines = []
            start = 0
            for line in f:
                if (start_range in line):
                    start = 1
                if (end_range in line):
                    start = 0
                    selected_lines.append(line)
                    return selected_lines
                if (start == 1):
                    selected_lines.append(line)
            f.close()
            return selected_lines
        except Exception as exp:
            self.log.Message(str(exp), self.log.const_critical_text)

    def getDefaultDatetimeUltramap(self, filename, timeDiff):
        try:
            date_str = ''
            time_str = ''
            with open(filename) as f:
                for line in f:
                    if('#Date:' in line):
                        date_str = line.split('#Date:')[1].strip()
                    elif('#Time:' in line):
                        time_str = line.split('#Time:')[1].strip()
                        break
            date_str = ''.join(date_str.split('-'))
            return self.dttm('{}{}'.format(date_str, time_str), timeDiff)    
        except Exception as e:
            self.log.Message(str(e), self.log.const_critical_text)

    def select_range_list1(self,list, start_range, end_range):
        try:
            selected_lines = []
            start = 0
            for line in list:
                if (start_range in line):
                    start = 1

                if (end_range in line):
                    selected_lines.append(line)
                    return selected_lines
                if (start == 1):
                    selected_lines.append(line)
            return selected_lines
        except Exception as exp:
            self.log.Message(str(exp), self.log.const_critical_text)

    def select_range_list2(self,list, start_range, end_range):
        try:
            selected_lines = []
            start = 0
            for line in list:
                if (line.__contains__("EPSG")):
                    continue
                elif (line.split(";")[0].__contains__(start_range)):
                    start = 1
                elif (line.split(";")[0].__contains__(end_range)):
                    return selected_lines
                if (start == 1):
                    selected_lines.append(line)
            return selected_lines
        except Exception as exp:
            self.log.Message(str(exp), self.log.const_critical_text)

    def dttm(self,_datetime,timeDiff):
        date_time_str = None
        if (_datetime.find("/")!=-1):
            #date format is assumed to be mm/dd/yyy
            date_time = datetime.datetime.strptime(_datetime,"%m/%d/%Y")+datetime.timedelta(hours=timeDiff)
            date_time_str = datetime.datetime.strftime(date_time,"%Y-%m-%d")
        elif (len(_datetime)==8):
            date_time = datetime.datetime.strptime(_datetime,"%Y%m%d")+datetime.timedelta(hours=timeDiff)
            date_time_str = datetime.datetime.strftime(date_time,"%Y-%m-%d")
        elif (len(_datetime)==10):
            date_time = datetime.datetime.strptime(_datetime,"%Y%m%d%H:%M")+datetime.timedelta(hours=timeDiff)
            date_time_str = datetime.datetime.strftime(date_time,"%Y-%m-%d %H")
        elif (len(_datetime)==13):
            date_time = datetime.datetime.strptime(_datetime,"%Y%m%d%H:%M")+datetime.timedelta(hours=timeDiff)
            date_time_str = datetime.datetime.strftime(date_time,"%Y-%m-%d %H:%M")
        elif (len(_datetime)==16):
            date_time = datetime.datetime.strptime(_datetime,"%Y%m%d%H:%M:%S")+datetime.timedelta(hours=timeDiff)
            date_time_str = datetime.datetime.strftime(date_time,"%Y-%m-%d %H:%M:%S")
        return date_time_str

    def frameUltraMap(self, rasterDir, totalLines, camId, imgId, prptX, prptY, prptZ, rotX, rotY, rotZ, srs, postfix, prefix, _time, cameraType,productType,camNameIDDir, nadirType):
        try:
            len_ = len(postfix.split(","))

            if len_==1 and postfix!='':
                if productType.lower()== 'both':
                    obliqueStrings = [postfix] * 4
            elif len_==1 and postfix=='':
                if productType.lower()=='nadir':
                    postfix = '.tif'
                elif productType.lower()=='oblique':
                    obliqueStrings = ['.tif'] * 4
                else:
                    postfix = '.tif'
                    obliqueStrings = ['.tif'] * 4

            if len_==4:
                obliqueStrings = postfix.split(',')

            if len_==5:
                obliqueStrings = postfix.split(',')[1:]
                postfix= postfix.split(',')[0]

            #ic = arcpy.da.InsertCursor(tableFullPath,["ImageID","Raster","PerspectiveX","PerspectiveY","PerspectiveZ","Omega","Phi","Kappa","CameraID","ProductName","SRS","AcquisitionDate"])
            fields = ["ImageID","Raster","PerspectiveX","PerspectiveY","PerspectiveZ","Omega","Phi","Kappa","CameraID","ProductName","SRS","AcquisitionDate"]
            frameRows = []
            if len(srs)==0:
                srs=None

            for i in range(0, totalLines):
                _imgId,_Raster = self.updateFields(imgId[i],prefix,cameraType,rasterDir)
                if productType.lower() == 'nadir' or productType.lower() == 'both':
                    if (camNameIDDir[camId[i]]=='Lvl02-PAN' and nadirType.lower()=='panchromatic'):
                        write = "{0}{1}".format(_imgId,postfix.split(".")[0]) + "," +  _Raster + "{0}".format(postfix) + "," + (prptX[i]) + "," + (prptY[i]) + "," + (prptZ[i]) + "," + (rotX[i]) + "," + (rotY[i]) + "," + (rotZ[i]) + "," + camId[i] + "," + "NadirOTF"
                        write = write.strip()
                        lst_write = write.split(",")
                        lst_write.append(srs)
                        lst_write.append(_time[i])
                        try:
                            frameRows.append(lst_write)
                        except Exception as exp:
                            self.log.Message(str(exp), self.log.const_critical_text)
                            self.log.Message("Error writing {}".format(write), self.log.const_critical_text)
                            pass

                    elif (camNameIDDir[camId[i]]=='Lvl02-Color' and nadirType=='ms'):
                        write = "{0}{1}".format(_imgId,postfix.split(".")[0]) + "," +  _Raster + "{0}".format(postfix) + "," + (prptX[i]) + "," + (prptY[i]) + "," + (prptZ[i]) + "," + (rotX[i]) + "," + (rotY[i]) + "," + (rotZ[i]) + "," + camId[i] + "," + "NadirOTF"
                        write = write.strip()
                        lst_write = write.split(",")
                        lst_write.append(srs)
                        lst_write.append(_time[i])
                        try:
                            frameRows.append(lst_write)
                        except Exception as exp:
                            self.log.Message(str(exp), self.log.const_critical_text)
                            self.log.Message("Error writing {}".format(write), self.log.const_critical_text)
                            pass
                if productType.lower() == 'oblique' or productType.lower() == 'both':
                    if (camNameIDDir[camId[i]]=='Lvl02-Oblique-Left'):
                        writeOblique2 = "{0}{1}".format(_imgId,obliqueStrings[0].split(".")[0]) + "," +  _Raster + "{0}".format(obliqueStrings[0]) + "," + prptX[i] + "," + prptY[i] + "," + prptZ[i] + "," + rotX[i] + "," + rotY[i] + "," + rotZ[i] + "," + camId[i] + "," + "ObliqueF"
                        writeOblique2 = writeOblique2.strip()
                        lst_writeOblique2 = writeOblique2.split(",")
                        lst_writeOblique2.append(srs)
                        lst_writeOblique2.append(_time[i])
                        try:
                            frameRows.append(lst_writeOblique2)
                            continue
                        except Exception as exp:
                            self.log.Message(str(exp), self.log.const_critical_text)
                            self.log.Message("Error writing {}".format(writeOblique2), self.log.const_critical_text)
                            pass

                    elif (camNameIDDir[camId[i]]=='Lvl02-Oblique-Right'):
                        writeOblique3 = "{0}{1}".format(_imgId,obliqueStrings[1].split(".")[0]) + "," +  _Raster +  "{0}".format(obliqueStrings[1]) + "," + prptX[i] + "," + prptY[i] + "," + prptZ[i] + "," + rotX[i] + "," + rotY[i] + "," + rotZ[i] + "," + camId[i] + "," + "ObliqueF"
                        writeOblique3 = writeOblique3.strip()
                        lst_writeOblique3 = writeOblique3.split(",")
                        lst_writeOblique3.append(srs)
                        lst_writeOblique3.append(_time[i])
                        try:
                            frameRows.append(lst_writeOblique3)
                            continue
                        except Exception as exp:
                            self.log.Message(str(exp), self.log.const_critical_text)
                            self.log.Message("Error writing {}".format(writeOblique3), self.log.const_critical_text)
                            pass

                    elif (camNameIDDir[camId[i]]=='Lvl02-Oblique-Forward'):
                        writeOblique4 = "{0}{1}".format(_imgId,obliqueStrings[2].split(".")[0]) + "," +  _Raster + "{0}".format(obliqueStrings[2]) + "," + prptX[i] + "," + prptY[i] + "," + prptZ[i] + "," + rotX[i] + "," + rotY[i] + "," + rotZ[i] + "," + camId[i] + "," + "ObliqueF"
                        writeOblique4 = writeOblique4.strip()
                        lst_writeOblique4 = writeOblique4.split(",")
                        lst_writeOblique4.append(srs)
                        lst_writeOblique4.append(_time[i])
                        try:
                            frameRows.append(lst_writeOblique4)
                            continue
                        except Exception as exp:
                            self.log.Message(str(exp), self.log.const_critical_text)
                            self.log.Message("Error writing {}".format(writeOblique4), self.log.const_critical_text)
                            pass

                    elif (camNameIDDir[camId[i]]=='Lvl02-Oblique-Backward'):
                        writeOblique5 = "{0}{1}".format(_imgId,obliqueStrings[3].split(".")[0]) + "," +  _Raster + "{0}".format(obliqueStrings[3]) + "," + prptX[i] + "," + prptY[i] + "," + prptZ[i] + "," + rotX[i] + "," + rotY[i] + "," + rotZ[i] + "," + camId[i] + ","+ "ObliqueF"
                        writeOblique5 = writeOblique5.strip()
                        lst_writeOblique5 = writeOblique5.split(",")
                        lst_writeOblique5.append(srs)
                        lst_writeOblique5.append(_time[i])
                        try:
                            frameRows.append(lst_writeOblique5)
                            continue
                        except Exception as exp:
                            self.log.Message(str(exp), self.log.const_critical_text)
                            self.log.Message("Error writing {}".format(writeOblique5), self.log.const_critical_text)
                            pass
            return fields, frameRows
        except Exception as exp:
            self.log.Message(str(exp), self.log.const_critical_text)
            return None, None

    def frameApplanix(self,eoFilename,rasterDir,totalLines,camId,imgId,prptX,prptY,prptZ,omega,phi,kappa,postfix,prefix,in_gdb,lat,lon,event,_time,tableFullPath,cameraType,_datetime):
        try:
                ic = arcpy.da.InsertCursor(tableFullPath,["ImageID","Raster","PerspectiveX","PerspectiveY","PerspectiveZ","Omega","Phi","Kappa","CameraID","Event","TimeInSeconds","Latitude","Longitude","ProductName","AcquisitionDate"])
##                ic = arcpy.da.InsertCursor(tableFullPath,["ImageID","Raster","PerspectiveX","PerspectiveY","PerspectiveZ","Omega","Phi","Kappa","CameraID","Event","TimeInSeconds","Latitude","Longitude"])
                for i in range(0, totalLines):
                    _imgId,_Raster = self.updateFields(imgId[i],prefix,cameraType,rasterDir)
                    write = "{0}{1}".format(_imgId,postfix.split(",")[0]) + "," +  _Raster + "{0}".format(postfix.split(",")[0]) + "," + prptX[i] + "," + prptY[i] + "," + prptZ[i] + "," + omega[i] + "," + phi[i] + "," + kappa[i] + "," +  camId[i] + ","+ event[i] + "," + _time[i] + "," + lat[i] + "," + lon[i] + "," + "NadirOTF"
                    write = write.strip()
                    lst_write = write.split(",")
                    lst_write.append(_datetime[i])
                    try:
                        ic.insertRow(lst_write)
                        continue
                    except Exception as exp:
                        self.log.Message(str(exp), self.log.const_critical_text)
                        self.log.Message("Error writing {}".format(write), self.log.const_critical_text)
                        pass
                del tableFullPath,write,lst_write,ic   #name_of_file
                return True
        except Exception as exp:
            self.log.Message(str(exp), self.log.const_critical_text)
            return False

    def frameAustralis(self,rasterDir,totalLines,camId,imgId,prptX,prptY,prptZ,omega,phi,kappa,postfix,prefix,_time,cameraType,eofilename, srs):
        fields = ["ImageID","Raster","PerspectiveX","PerspectiveY","PerspectiveZ","Omega","Phi","Kappa","CameraID","ProductName","AcquisitionDate", 'SRS']
        frameRows = []
        if rasterDir.startswith('http'):
            rasterDir = '/'.join([rasterDir,eofilename.split(".")[0]])
        else:
            rasterDir = os.path.join(rasterDir,eofilename.split(".")[0])  #Because the input parent raster directory has subfolders based on the eofilenames
        for i in range(0, totalLines):
            _imgId,_Raster = self.updateFields(imgId[i],prefix,cameraType,rasterDir)
            write = "{0}{1}".format(_imgId,postfix.split(".")[0]) + "," +  _Raster + "{0}".format(postfix) + "," + (prptX[i]) + "," + (prptY[i]) + "," + (prptZ[i]) + "," + (omega[i]) + "," + (phi[i]) + "," + (kappa[i]) + "," + camId[i] + "," + "ObliqueF"
            write = write.strip()
            lst_write = write.split(",")
            lst_write.append(_time[i])
            lst_write.append(srs)
            frameRows.append(lst_write)
        return fields, frameRows

    def frameBingo(self,rasterDir,totalLines,camId,imgId,prptX,prptY,prptZ,omega,phi,kappa,postfix,prefix,_time,tableFullPath,cameraType):
        ic = arcpy.da.InsertCursor(tableFullPath,["ImageID","Raster","PerspectiveX","PerspectiveY","PerspectiveZ","Omega","Phi","Kappa","CameraID","ProductName","AcquisitionDate"])
        for i in range(0, totalLines):
            _imgId,_Raster = self.updateFields(imgId[i],prefix,cameraType,rasterDir)
            write = "{0}{1}".format(_imgId,postfix.split(".")[0]) + "," +  _Raster + "{0}".format(postfix) + "," + (prptX[i]) + "," + (prptY[i]) + "," + (prptZ[i]) + "," + (omega[i]) + "," + (phi[i]) + "," + (kappa[i]) + "," + camId[i] + "," + "NadirOTF"
            write = write.strip()
            lst_write = write.split(",")
            lst_write.append(_time[i])
            try:
                ic.insertRow(lst_write)
            except Exception as exp:
                self.log.Message(str(exp), self.log.const_critical_text)
                self.log.Message("Error writing {}".format(write), self.log.const_critical_text)
                pass
        del ic
        return True

    def frameSanborn(self,rasterDir,totalLines,flightline,shotId,imgId,camId,prptX,prptY,prptZ,omega,phi,kappa,srs,postfix,prefix,datetime,cameraType):
        if len(srs)==0:
            srs=None
        fields = ["ImageID","Raster","PerspectiveX","PerspectiveY","PerspectiveZ","Omega","Phi","Kappa","CameraID","ProductName","FlightLine","ShotId","SRS","AcquisitionDate"]
        frameRows = []
        for i in range(0, totalLines):
            _imgId,_Raster = self.updateFields(imgId[i],prefix,cameraType,rasterDir)
            write = "{0}{1}".format(_imgId,postfix.split(".")[0]) + "," +  _Raster + "{0}".format(postfix) + "," + (prptX[i]) + "," + (prptY[i]) + "," + (prptZ[i]) + "," + (omega[i]) + "," + (phi[i]) + "," + (kappa[i]) + "," + camId[i] + "," + "ObliqueF" + "," + flightline[i] + "," + shotId[i]
            write = write.strip()
            lst_write = write.split(",")
            lst_write.append(srs)
            lst_write.append(datetime)
            frameRows.append(lst_write)
        return fields, frameRows

    def getRowCols(self,imagePath):
        try:
            raster = arcpy.Raster(imagePath)
            cols = raster.width
            rows = raster.height
            return rows,cols
        except Exception as exp:
            self.log.Message(str(exp), self.log.const_critical_text)
            return False

    def writeCamerasTable(self, tableFullPath, fields, rows):
        ic = arcpy.da.InsertCursor(tableFullPath, fields)
        for row in rows:
            try:
                ic.insertRow(row)
            except Exception as exp:
                self.log.Message(str(exp), self.log.const_critical_text)
                self.log.Message("Error writing {}".format(writeCamera), self.log.const_critical_text)         

    def cameraUltraMap(self, camLines, lstInput, lstIntrinsics, camSerid, camName, rotatedCams):
        """
           This sets the Exterior Orientation Parameters (A0,A1,A2,B0,B1,B2), FocalLength(microns) , PrincipalX(microns) , PrincipalY(microns) values
           where C = ((Columns/2)-0.5)*PixelSize(microns) and R = ((Rows/2)-0.5)*PixelSize(microns)
           ColorCamera/Oblique-Backward:
            A0= -R
            A1=  0
            A2= PixelSize (microns)
            B0= -C
            B1= PixelSize (microns)
            B2= 0
            Oblique-Left:
            A0= -C
            A1= PixelSize (microns)
            A2= 0
            B0= R
            B1= 0
            B2=-PixelSize (microns)
            Oblique-Right:
            A0= C
            A1= -PixelSize (microns)
            A2= 0
            B0= -R
            B1= 0
            B2= PixelSize (microns)
            Oblique-Forward:
            A0= R
            A1= 0
            A2= -PixelSize (microns)
            B0= C
            B1= -PixelSize (microns)
            B2= 0
        """
        try:
            pixelSizeMilli = []
            pixelSizeMicroFloat = []
            pixelSizeMicro = []
            width = []
            height = []
            C = []
            R = []
            camId = []
            principalDistMilli = []
            focalLengthtMicro = []
            ppaXmilli = []
            ppaXmicro = []
            ppaYmilli = []
            ppaYmicro = []
##            l = []
            lh = []
            lc = []
            swapFOV = []
            imgRot = []
            fields = ["FocalLength","PrincipalX","PrincipalY","A0","A1","A2","B0","B1","B2","CameraID","Camera_SerialID","Camera_Type","SensorWidth","SensorHeight", "SwapFOV", "ImgRot"]
            rows = []            
            for i in range(0, camLines):
                pixelSizeMilli.append(lstInput[i][4])
                if (rotatedCams != "" and rotatedCams != None):
                    if (lstInput[i][3].strip() in rotatedCams): #identify which cameras are rotated from the eo file
                        width.append(lstInput[i][6])   #swap width with height
                        height.append(lstInput[i][5])  #swap height with width
                        swapFOV.append(False)
                    else:
                        width.append(lstInput[i][5])
                        height.append(lstInput[i][6])
                        swapFOV.append(True)
                else:
                    width.append(lstInput[i][5])
                    height.append(lstInput[i][6])
                    swapFOV.append(True)
                rowsFloat=(float(float(height[i]) / float(pixelSizeMilli[i])))
                colsFloat=(float(float(width[i]) / float(pixelSizeMilli[i])))
                lh.append(rowsFloat)
                lc.append(colsFloat)
                var = float(pixelSizeMilli[i])* 1000
                round(var, 6)
                pixelSizeMicroFloat.append(var)
                pixelSizeMicro.append(str(var))
                varc = ((((colsFloat / 2) - 0.5) * pixelSizeMicroFloat[i]))
                C.append(str(varc))
                varr = ((((rowsFloat / 2) - 0.5) * pixelSizeMicroFloat[i]))
                R.append(str(varr))

            maxlimit = len(C)
            obl = lh[-4],lc[-4]     #the fourth last camera is left
            obr = lh[-3],lc[-3]     #the third last camera is right
            obf = lh[-2],lc[-2]     #the second last camera is forward
            obb = lh[-1],lc[-1]     #the last camera is backwar

            if (obl == obr):
                left_right_XY = str(obl).strip('()')
            if (obf == obb):
                fwd_bwd_XY = str(obf).strip('()')

            for j in range (0, maxlimit):
                camId.append(lstIntrinsics[j][0].strip())
                principalDistMilli.append(lstIntrinsics[j][1])
                ppaXmilli.append(lstIntrinsics[j][2])
                ppaYmilli.append(lstIntrinsics[j][3])

            for i in range(maxlimit):
                if ("pan" in camName[i].strip().lower() or 'color' in camName[i].strip().lower()):
                    imgRot.append(-90)
                elif ("left" in camName[i].strip().lower()):
                    imgRot.append(0)
                elif ("right" in camName[i].strip().lower()):
                    imgRot.append(180)
                elif ("forward" in camName[i].strip().lower()):
                    imgRot.append(90)
                elif ("backward" in camName[i].strip().lower()):
                    imgRot.append(-90)

            for i in range(0, maxlimit):
                try:
                    varPpDist = float(lstIntrinsics[i][1]) * 1000
                    round(varPpDist, 6)
                    varPpX = float(lstIntrinsics[i][2]) * 1000
                    round(varPpX, 6)
                    varPpY = float(lstIntrinsics[i][3]) * 1000
                    round(varPpY, 6)
                    focalLengthtMicro.append(str(varPpDist))
                    ppaXmicro.append(str(-1*varPpY))
                    ppaYmicro.append(str(varPpX))

                except Exception as exp:
                    self.log.Message(str(exp), self.log.const_critical_text)
                    pass

            if (left_right_XY != fwd_bwd_XY):
                for i in range(0, maxlimit):
                    if (camName[i].strip() == "Lvl02-PAN" or camName[i].strip() == "Lvl02-Color"):
                        writeCamera = (focalLengthtMicro[i]) + "," + (ppaXmicro[i]) + "," + (ppaYmicro[i]) + "," + ("-"+R[i]) + "," + "0" + "," + (pixelSizeMicro[i]) +","+ ("-"+C[i]) + "," + (pixelSizeMicro[i]) +"," + "0" + "," + camId[i] + "," + camSerid[i] + "," + camName[i]
                    elif (camName[i].strip() =="Lvl02-Oblique-Left"):
                        writeCamera = (focalLengthtMicro[i]) + "," + (ppaXmicro[i]) + "," + (ppaYmicro[i]) + "," + ("-"+C[i]) + "," + (pixelSizeMicro[i]) + "," + "0" +","+ (R[i]) + "," + "0" +"," + ("-"+pixelSizeMicro[i]) + "," + camId[i] + "," + camSerid[i] + "," + camName[i]
                    elif (camName[i].strip() =="Lvl02-Oblique-Right"):
                        writeCamera = (focalLengthtMicro[i]) + "," + (ppaXmicro[i]) + "," + (ppaYmicro[i]) + "," + (C[i]) + "," + ("-"+pixelSizeMicro[i]) + "," + "0" +","+ ("-"+R[i]) + "," + "0" +"," + (pixelSizeMicro[i]) + "," + camId[i] + "," + camSerid[i] + "," + camName[i]
                    elif (camName[i].strip() =="Lvl02-Oblique-Forward"):
                        writeCamera = (focalLengthtMicro[i]) + "," + (ppaXmicro[i]) + "," + (ppaYmicro[i]) + "," + (R[i]) + "," + "0" + "," + ("-"+pixelSizeMicro[i]) +","+ C[i] + "," + ("-"+pixelSizeMicro[i]) +"," + "0" + "," + camId[i] + "," + camSerid[i] + "," + camName[i]
                    elif (camName[i].strip() =="Lvl02-Oblique-Backward"):
                        writeCamera = (focalLengthtMicro[i]) + "," + (ppaXmicro[i]) + "," + (ppaYmicro[i]) + "," + ("-"+R[i]) + "," + "0" + "," + (pixelSizeMicro[i]) +","+ ("-"+C[i]) + "," + (pixelSizeMicro[i]) +"," + "0" + "," + camId[i] + "," + camSerid[i] + "," + camName[i]

                    writeCamera = writeCamera.strip()
                    lst_writeCamera = writeCamera.split(",")
                    #converting sensor width and height to microns
                    lst_writeCamera.append(float(width[i]) * 1000)
                    lst_writeCamera.append(float(height[i]) * 1000)
                    lst_writeCamera.append(swapFOV[i])
                    lst_writeCamera.append(imgRot[i])
                    try:
                        #ic.insertRow(lst_writeCamera)
                        rows.append(lst_writeCamera)
                    except Exception as exp:
                        self.log.Message(str(exp), self.log.const_critical_text)
                        self.log.Message("Error writing {}".format(writeCamera), self.log.const_critical_text)
                        pass

            else:
                for i in range(0, maxlimit):
                    writeCamera = (focalLengthtMicro[i]) + "," + (ppaXmicro[i]) + "," + (ppaYmicro[i]) + "," + ("-"+R[i]) + "," + "0" + "," + (pixelSizeMicro[i]) +","+ ("-"+C[i]) + "," + (pixelSizeMicro[i]) +"," + "0" + "," + camId[i] + "," + camSerid[i] + "," + camName[i]
                    writeCamera = writeCamera.strip()
                    lst_writeCamera = writeCamera.split(",")
                    #converting sensor width and height to microns
                    lst_writeCamera.append(float(width[i]) * 1000)
                    lst_writeCamera.append(float(height[i]) * 1000)  
                    lst_writeCamera.append(swapFOV[i])
                    lst_writeCamera.append(imgRot[i])
                    try:
                        rows.append(lst_writeCamera)
                    except Exception as exp:
                        self.log.Message(str(exp), self.log.const_critical_text)
                        self.log.Message("Error writing {}".format(writeCamera), self.log.const_critical_text)
                        pass

            del writeCamera,lst_writeCamera
            return fields, rows
        except Exception as exp:
            self.log.Message(str(exp), self.log.const_critical_text)
            return fields, rows

    def cameraAustralis(self,inputEO):
        """
           This sets the Exterior Orientation Parameters (A0,A1,A2,B0,B1,B2), FocalLength(microns) , PrincipalX(microns) , PrincipalY(microns) values
           where C = ((Columns/2)-0.5)*PixelSize(microns) and R = ((Rows/2)-0.5)*PixelSize(microns).
           For all the 9/17 cameras it is as below:
            A0= -C
            A1= PixelSize (microns)
            A2= 0
            B0= R
            B1= 0
            B2=-PixelSize (microns)
        """
        try:
            cameraDir = os.path.join(os.path.dirname(inputEO),"Camera_Models")
            if os.path.exists(cameraDir) is False:
                cameraDir = os.path.join(os.path.dirname(inputEO),"Camera")
                if os.path.exists(cameraDir) is False:
                    self.log.Message("No directory named Camera/Camera_Models found to build a camera table.Exiting the program",self.log.const_critical_text)
                    exit()
            fields = ["FocalLength","PrincipalX","PrincipalY","A0","A1","A2","B0","B1","B2","CameraID","Camera_SerialID", "DistortionType",'Radial','Tangential', 'SensorWidth', 'SensorHeight']
            camera_rows = []
            radialDistortion=[]
            tangentialDistortion=[]
            distortionType = "DistortionModel"
            for _file in os.listdir(cameraDir):
                readFile = open(os.path.join(cameraDir,_file),"r")
                for line in readFile:
                    line = line.strip()
                    if (line.startswith("Camera:")):
                        cameraSerialID = line.split(":")[1]
                        cameraID = cameraSerialID.split("+")[1]
                    elif (line.startswith("Resolution")):
                        cols =float(line.split(" x ")[0].split("=")[1].strip()) #7360
                        rows =float(line.split(" x ")[1].split("pixels")[0].strip()) #4912
                    elif (line.startswith("Pixel")):
                        PWidth = float(line.split(",")[0].split("=")[1].strip()[0:-2]) * 1000 #PixelWidth in microns
                        PHeight = float(line.split(",")[1].split("=")[1].strip()[0:-2]) * 1000 #PixelHeight in microns
                    elif (line.startswith("Principal distance")):
                        focalLength = float(line.split("=")[1].strip()) * 1000  #focallength in microns
                    elif (line.startswith("Principal point offset in x-image coordinate")):
                        ppX=float(line.split("=")[1].strip())*1000  #Principal X in microns
                    elif (line.startswith("Principal point offset in y-image coordinate")):
                        ppY=float(line.split("=")[1].strip())*1000    #Principal Y in microns
                    elif (line.startswith("1rd-order term of radial distortion correction")):
                        K0=float(line.split("=")[1].strip())
                        radialDistortion.append(K0)
                    elif (line.startswith("3rd-order term of radial distortion correction")):
                        K1=float(line.split("=")[1].strip())
                        radialDistortion.append(K1)
                    elif (line.startswith("5th-order term of radial distortion correction")):
                        K2=float(line.split("=")[1].strip())
                        radialDistortion.append(K2)
                    elif (line.startswith("7th-order term of radial distortion correction")):
                        K3=float(line.split("=")[1].strip())
                        radialDistortion.append(K3)
                    elif (line.startswith("Coefficient of decentering distortion")):        #this line will get executed twice as there are 2 lines with beginning with the same string.
                        P1=float(line.split("=")[1].strip())
                        tangentialDistortion.append(P1)
        
                readFile.close()
                #Calculate C and R
        
                C = ((cols/2.0)-0.5)*PWidth
                R = ((rows/2.0)-0.5)*PHeight
                A0 = str(-C)
                A1 = str(PWidth)
                A2 = str(0)
                B0 = str(R)
                B1 = str(0)
                B2 = str(-PHeight)
                radialDistortionString = "".join((str(val)+" ") for val in radialDistortion)
                tangentialDistortionString = "".join((str(val)+" ") for val in tangentialDistortion)
                radialDistortion=[]
                tangentialDistortion=[]
        
                writeCamera = (str(focalLength) + "," + str(ppX) + "," + str(ppY)+ "," + A0 + "," + A1 + "," + A2 +","+ B0 + "," + B1 +"," + B2 + "," +cameraID + "," + cameraSerialID + "," + distortionType + "," + radialDistortionString + "," + tangentialDistortionString)
                lst_writeCamera = writeCamera.split(",")
                lst_writeCamera.append(cols*PWidth)
                lst_writeCamera.append(rows*PHeight)
                try:
                    camera_rows.append(lst_writeCamera)
                except Exception as exp:
                    self.log.Message(str(exp),self.log.const_critical_text)
                    pass
    
            return fields, camera_rows
        except Exception as e:
            self.log.Message(str(e),self.log.const_critical_text)
            arcpy.AddError(str(e))

    def cameraSanborn(self,inputEO):
        """
           This sets the Exterior Orientation Parameters (A0,A1,A2,B0,B1,B2), FocalLength(microns) , PrincipalX(microns) , PrincipalY(microns) values
           where C = ((Columns/2)-0.5)*PixelSize(microns) and R = ((Rows/2)-0.5)*PixelSize(microns).
           For all the cameras it is as below:
            A0= -C
            A1= PixelSize (microns)
            A2= 0
            B0= R
            B1= 0
            B2=-PixelSize (microns)
        """
        fields = ["FocalLength","PrincipalX","PrincipalY","A0","A1","A2","B0","B1","B2","CameraID","DistortionType",'Radial','Tangential', 'SensorWidth', 'SensorHeight']
        cam_rows = []
        readFile = open(os.path.join(inputEO),"r")
        lstWrite=[]
        try:
            openFile = open(inputEO, 'r')
            read = openFile.readlines()
            for line in read[1:]:
                lstLine = line.strip().split(",")
                camId = lstLine[0]
                pixelSize = float(lstLine[1])*1000
                cols = float(lstLine[2])
                rows = float(lstLine[3])
                focalLength = str(float(lstLine[4]) * 1000)
                ppX = str(float(lstLine[5])*1000)
                ppY = str(float(lstLine[6])*1000)
                distortionType = "DistortionModel"
                K0='0'
                K1 = lstLine[7]
                K2 = lstLine[8]
                K3 = lstLine[9]
                P1 = lstLine[10]
                P2 = lstLine[11]

                radial = K0+" "+K1+" "+K2+" "+K3
                tangential = P1+" "+P2

                C = ((cols/2.0)-0.5)*pixelSize
                R = ((rows/2.0)-0.5)*pixelSize
                A0 = -C
                A1 = pixelSize
                A2 = 0
                B0 = R
                B1 = 0
                B2 = -pixelSize

                lstWrite.append(focalLength)
                lstWrite.append(ppX)
                lstWrite.append(ppY)
                lstWrite.append(A0)
                lstWrite.append(A1)
                lstWrite.append(A2)
                lstWrite.append(B0)
                lstWrite.append(B1)
                lstWrite.append(B2)
                lstWrite.append(camId)
                lstWrite.append(distortionType)
                lstWrite.append(radial)
                lstWrite.append(tangential)
                lstWrite.append(cols * pixelSize)
                lstWrite.append(rows * pixelSize)
                try:
                    #ic.insertRow(lstWrite)
                    cam_rows.append(lstWrite)
                    lstWrite=[]
                except Exception as exp:
                    self.log.Message(str(exp),self.log.const_critical_text)
                    pass
        except Exception as exp:
            self.log.Message(str(exp),self.log.const_critical_text)
        return fields, cam_rows


    def generateTable(self,in_gdb,tableName):
        if(arcpy.Exists(in_gdb) is False):
            arcpy.CreateFileGDB_management(os.path.dirname(in_gdb),os.path.basename(in_gdb))
        tableFullPath = os.path.join(in_gdb,tableName)
        if (arcpy.Exists(tableFullPath)) is True:
            self.log.Message("Table already exists.Ovewriting the existing table", self.log.const_general_text)
        arcpy.env.overwriteOutput = True
        arcpy.CreateTable_management(in_gdb,tableName) #Creating the table
        arcpy.env.overwriteOutput = False

    def updateFields(self,imageID,pre,metaFormat,rasterDir):
        try:
            if (pre == "#"):
                pre = ""
            imageID = imageID.strip()
            try:
                newval = pre +imageID
                if (rasterDir != "#"):
                    if rasterDir.startswith('http'):
                        if rasterDir.endswith('/'):
                            raster = "{}{}".format(rasterDir, newval)
                        else:
                            raster = "{}/{}".format(rasterDir, newval)
                    else:
                        raster = os.path.join(rasterDir,newval)
                else:
                    raster = newval
                imageID = newval.split(".")[0]
            except Exception as exp:
                self.log.Message("Failed to update value for {}", self.log.const_critical_text)
            return imageID,raster
        except Exception as exp:
            self.log.Message(str(exp), self.log.const_critical_text)
            return False


    def parseValueswithGaps(self,line):

        line =line.replace('\t','').replace('\n','')
        elems= line.split(' ')
        elems= list(filter(None,elems))
        return elems


    def parseValues(self, frameLines, convFactor, cameraType, order, timediff):
        totalLines = 0
        imgId = []
        prptX = []
        prptY = []
        prptZ = []
        rotX = []
        rotY = []
        rotZ = []
        omega = []
        phi = []
        kappa=[]
        camId = []
        _time=[]
        lat = []
        lon = []
        event = []
        shotId = []
        flightline = []
        _datetime=[]
        if (cameraType.lower() == 'ultramap'):
            for oLine in frameLines:
                totalLines = totalLines + 1
                try:
                    oLine= oLine.replace(" ","")
                    lstLine = oLine.strip().split(";")
                except Exception as exp:
                    self.log.Message(str(exp), self.log.const_critical_text)
                try:
                    Rx = math.radians(float(lstLine[5].strip()))
                    Ry = math.radians(float(lstLine[6].strip()))
                    Rz = math.radians(float(lstLine[7].strip()))
                    m11 = math.cos(Ry)*math.cos(Rz)+math.sin(Rx)*math.sin(Ry)*math.sin(Rz)
                    m21 = math.sin(Rx)*math.sin(Ry)*math.cos(Rz) - math.cos(Ry)*math.sin(Rz)
                    m32 = -math.sin(Rx)
                    m31 = math.cos(Rx)*math.sin(Ry)
                    m33 = math.cos(Rx)*math.cos(Ry)

                    Omega = math.degrees(math.atan2(-m32,m33) )
                    Phi =math.degrees(math.asin(m31) )
                    Kappa = math.degrees(math.atan2(-m21,m11) ) - 90

                    camId.append(lstLine[0])
                    imgId.append(lstLine[1])
                    prptX.append(lstLine[2])
                    prptY.append(lstLine[3])
                    prptZ.append(lstLine[4])
##                    rotX.append(str(convFactor*float(lstLine[5])))
##                    rotY.append(str(convFactor*float(lstLine[6])))
##                    rotZ.append(str(float(str((convFactor*float(lstLine[7]))-90))))
                    rotX.append(str(convFactor*float(Omega)))
                    rotY.append(str(convFactor*float(Phi)))
                    rotZ.append(str(float(str((convFactor*float(Kappa))))))
                    try:
                        date_time_str = self.dttm(lstLine[8].strip().replace(" ","").replace("\t",""), timediff)
                        _time.append(date_time_str)
                    except:
##                        self.log.Message("Unable to find Acquisition date and time", self.log.const_critical_text)
                        _time.append(None)
                except Exception as exp:
                    self.log.Message(str(exp), self.log.const_critical_text)
                    self.log.Message("Failed to read the lines from the eo file", self.log.const_critical_text)
                    pass
            return totalLines,camId,imgId,prptX,prptY,prptZ,rotX,rotY,rotZ,_time

        elif (cameraType.lower() == 'bingo'):
            for line in frameLines:
                try:
                    totalLines = totalLines + 1
                    elems = self.parseValueswithGaps(line.strip())
                    imgId.append(elems[0])     #imgId.append(lstLine.split(";")[1])
                    prptX.append(elems[1])
                    prptY.append(elems[2])
                    prptZ.append(elems[3])
                    if order == 'POK':
                        phi.append(str(convFactor*float(elems[4])))
                        omega.append(str(convFactor*float(elems[5])))
                    else:
                        omega.append(str(convFactor*float(elems[4])))
                        phi.append(str(convFactor*float(elems[5])))
                    kappa.append(str(convFactor*float(elems[6])))
                    camId.append("0")
                    try:
                        date_time_str = self.dttm(elems[7].strip().replace(" ","").replace("\t",""), timediff)
                        _time.append(date_time_str)
                    except:
##                        self.log.Message("Unable to find Acquisition date and time", self.log.const_critical_text)
                        _time.append(None)

                except Exception as exp:
                    self.log.Message(str(exp), self.log.const_critical_text)
                    self.log.Message("Failed to read the lines from the eo file", self.log.const_critical_text)
                    pass
            return totalLines,camId,imgId,prptX,prptY,prptZ,omega,phi,kappa,_time

        elif (cameraType.lower() == 'applanix'):
            for line in frameLines:
                try:
                    totalLines = totalLines + 1
                    elems = self.parseValueswithGaps(line)
                    imgId.append(elems[0].strip())
                    event.append(elems[1])
                    _time.append(elems[2])
                    prptX.append(elems[3])
                    prptY.append(elems[4])
                    prptZ.append(elems[5])
                    omega.append(str(convFactor*float(elems[6])))
                    phi.append(str(convFactor*float(elems[7])))
                    kappa.append(str(convFactor*float(elems[8])))
                    lat.append(elems[9])
                    lon.append(elems[10])
                    camId.append("0")

                    try:
                        try:
                            date_time_str = self.dttm(elems[11]+elems[12], timediff)
                        except:
                            date_time_str = self.dttm(elems[11], timediff)
                        _datetime.append(date_time_str)
                    except:
##                        self.log.Message("Unable to find Acquisition date and time", self.log.const_critical_text)
                        _datetime.append(None)

                except Exception as exp:
                    self.log.Message(str(exp), self.log.const_critical_text)
                    self.log.Message("Failed to read the lines from the eo file", self.log.const_critical_text)
                    pass
            return totalLines,camId,imgId,event,_time,prptX,prptY,prptZ,omega,phi,kappa,lat,lon,_datetime

        elif (cameraType.lower() == 'australis'):
            for line in frameLines:
                try:
                    totalLines = totalLines + 1
                    elems = self.parseValueswithGaps(line.strip())
                    imgId.append(elems[0])
                    prptX.append(elems[1])
                    prptY.append(elems[2])
                    prptZ.append(elems[3])
                    omega.append(str(convFactor*float(elems[4])))
                    phi.append(str(convFactor*float(elems[5])))
                    kappa.append(str(convFactor*float(elems[6])))
                    camId.append((elems[0][elems[0].rfind("-")+1:]).capitalize())  #eg of image id 008929-0408171752017-CAM1 . The entire image id string in the eo file contains CameraID as well. Hence extracting the cameraID from the image id
                    try:
                        date_time_str = self.dttm(elems[7].strip().replace(" ","").replace("\t",""), timediff)
                        _time.append(date_time_str)
                    except:
##                        self.log.Message("Unable to find Acquisition date and time", self.log.const_critical_text)
                        _time.append(None)

                except Exception as exp:
                    self.log.Message(str(exp), self.log.const_critical_text)
                    self.log.Message("Failed to read the lines from the eo file", self.log.const_critical_text)
                    pass
            return totalLines,camId,imgId,prptX,prptY,prptZ,omega,phi,kappa,_time

        elif (cameraType.lower() == 'sanborn'):
            for oLine in frameLines[1:]:    #the first line is the header information
                totalLines = totalLines + 1
                try:
                    oLine= oLine.replace(" ","")
                    lstLine = oLine.strip().split(",")
                except Exception as exp:
                    self.log.Message(str(exp), self.log.const_critical_text)
                try:
                    imgId.append(lstLine[0].split(".")[0])
                    flightline.append(lstLine[1])
                    shotId.append(lstLine[2])
                    camId.append(lstLine[3])
                    prptX.append(lstLine[4])
                    prptY.append(lstLine[5])
                    prptZ.append(lstLine[6])

                    Omega = float(lstLine[7].strip())
                    Phi = float(lstLine[8].strip())
                    Kappa = float(lstLine[9].strip())

                    rotX.append(str(convFactor*float(Omega)))
                    rotY.append(str(convFactor*float(Phi)))
                    rotZ.append(str(float(str((convFactor*float(Kappa))))))
                except Exception as exp:
                    self.log.Message(str(exp), self.log.const_critical_text)
                    self.log.Message("Failed to read the lines from the eo file", self.log.const_critical_text)
                    pass
            return totalLines,imgId,flightline,shotId,camId,prptX,prptY,prptZ,rotX,rotY,rotZ


    def extractParFiles(self,parFolder):
        listPar = []
        if os.path.isdir(parFolder):
            for root,dir,files in os.walk(parFolder):
                for file in files:
                    if file.endswith(".par"):
                        listPar.append(os.path.join(root,file))
            return listPar
        else:
            self.log.Message('Invalid folder input, please try again',0)
            exit(1)


    # for each par file, extract information and write into the frame table
    def extractDataFromPar(self,listPar,tablePath,tifFlag):
        ic = arcpy.da.InsertCursor(tablePath,["Raster","PerspectiveX","PerspectiveY","PerspectiveZ",\
            "Omega","Phi","Kappa","FocalLength","PrincipalX","PrincipalY","A0","A1","A2","B0","B1","B2","AverageZ","ProductName"])

        for fileName in listPar:
            #initializing values
            flag=0
            typeNo=0
            persZ=0
            omega=0
            photoScale=0
            focalLength=0
            ppaX=0
            ppaY=0
            avgZ=0
            ende=0
            lineToWrite=''
            lstToWrite=[]

            with open(fileName,'r') as parFile:
                fileLines= parFile.readlines()

            for line in fileLines:
                try:
                     # $TYPE occurs twice in every par file but we need to check only the first
                    if (line.startswith('$TYPE') and typeNo==0):
                        typeNo=1
                        if (line.strip().split(' ')[1]!='OPK'):
                            self.log.Message('Error in type for file. Needs to be OPK: {0}\n'.format(fileName),2)
                            flag=1
                            break
                        continue

                    elif line.startswith('$FSCALE00'):
                        photoScale= float(line.strip().split(' ')[1])
                        continue

                    elif line.startswith('$FILE00'):
                        if tifFlag==1:
                            raster= (fileName.replace('.par','.tif'))
                        else:
                            raster= line.strip().split(' ')[1]
                        continue

                    elif line.startswith("$PARAFFINE00"):
                        afflineParam = line.strip().split(' ')[1:]

                        A1 = round(float(afflineParam[0]) * 1000, 1)
                        A2 = round(float(afflineParam[1]) * 1000, 1)
                        A0 = round(float(afflineParam[2]) * 1000, 1)
                        B1 = round(float(afflineParam[3]) * 1000, 1)
                        B2 = round(float(afflineParam[4]) * 1000, 1)
                        B0 = round(float(afflineParam[5]) * 1000, 1)
                        continue

                    elif line.startswith('$FOCAL'):
                        focalLength= (float(line.strip().split(' ')[1]) * 1000)
                        continue

                    elif line.startswith('$FOC00'):
                        focalLength= (float(line.strip().split(' ')[1]) * 1000)
                        continue

                    elif line.startswith('$PPA'):
                        ppa= line.strip().split(' ')[1:]
                        ppaX= (float(ppa[0]))
                        ppaY= (float(ppa[1]))
                        continue

                    elif line.startswith('$XYZ00'):
                        perspective= line.strip().split(' ')[1:]

                        persX = round(float(perspective[0]), 3)
                        persY = round(float(perspective[1]), 3)
                        persZ = round(float(perspective[2]), 3)
                        continue

                    elif line.startswith('$OPK00'):
                        opk= line.strip().split(' ')[1:]

                        omega = round(float(opk[0]), 5)
                        phi = round(float(opk[1]), 5)
                        kappa = round(float(opk[2]), 3)
                        continue

                    elif line.startswith('.END'):
                        if ppaX != 0 and A1 != 0:
                            ppaX = (ppaX+(A0/A1))*A1     #ppa is from upper left. A0 is offset to center and A1 represents pixel size. In ArcGIS PPA is from center of frame in micorn
                        else:
                            ppaX = 0

                        if ppaY != 0 and B2 != 0:
                            ppaY = (ppaY+(B0/B2))*B2
                        else:
                            ppaY = 0

                        if persZ and photoScale and focalLength:
                            try:
                                avgZ= persZ- (photoScale*focalLength/1000000)
                            except:
                                self.log.Message('Error in calculating average Z value',2)
                                break

                        # After file is read now writing to the table for current file
                        lstToWrite.append(raster)
                        lstToWrite.append(persX)
                        lstToWrite.append(persY)
                        lstToWrite.append(persZ)
                        lstToWrite.append(omega)
                        lstToWrite.append(phi)
                        lstToWrite.append(kappa)
                        lstToWrite.append(focalLength)
                        lstToWrite.append(ppaX)
                        lstToWrite.append(ppaY)
                        lstToWrite.append(A0)
                        lstToWrite.append(A1)
                        lstToWrite.append(A2)
                        lstToWrite.append(B0)
                        lstToWrite.append(B1)
                        lstToWrite.append(B2)
                        lstToWrite.append(avgZ)
                        lstToWrite.append("NadirOTF")

                        try:
                            ic.insertRow(lstToWrite)
                            break
                        except Exception as exp:
                            self.log.Message(str(exp),2)
                            pass

                except Exception as exp:
                    self.log.Message(exp,2)
                    self.log.Message('Error in file: {0}\n'.format(fileName),2)
                    break

        self.log.Message('Table has been written\n',0)
        del ic
        return True

    def getFrameParams(self, rasterDir, totalLines, camId, imgId, prptX, prptY, prptZ, rotX, rotY, rotZ, srs, postfix, prefix, _time, cameraType,productType,camNameIDDir,default_time):
        postfixes = postfix.split(",")
        postfixes = [p for p in postfixes if p]
        if productType.lower()=='nadir':
            if not postfixes:
                postfix = '.tif'
            else:
                postfix = postfixes[0]
        elif productType.lower()=='oblique':
            if len(postfixes) < 4:
                obliqueStrings = postfixes + ['.tif'] * (4-len(postfixes))
            elif len(postfixes) > 4:
                obliqueStrings = postfixes[:4]
            else:
                obliqueStrings = postfixes
        frame_list = []
        if len(srs)==0:
            srs=None

        for i in range(totalLines):
            _imgId,_Raster = self.updateFields(imgId[i],prefix,cameraType,rasterDir)
            
            if productType.lower() == 'oblique' and camNameIDDir:
                if (camNameIDDir[camId[i]]=='Lvl02-Oblique-Left'):
                    postfix = obliqueStrings[0]
                elif (camNameIDDir[camId[i]]=='Lvl02-Oblique-Right'):
                    postfix = obliqueStrings[1]
                elif (camNameIDDir[camId[i]]=='Lvl02-Oblique-Forward'):
                    postfix = obliqueStrings[2]
                elif (camNameIDDir[camId[i]]=='Lvl02-Oblique-Backward'):
                    postfix = obliqueStrings[3]
                else:
                    postfix = None

            if postfix:
                frame_dict = {
                                 "ImageID": "{}{}".format(_imgId, postfix.split(".")[0]),
                                 "Raster": "{}{}".format(_Raster, postfix),
                                 "PerspectiveX": prptX[i],
                                 "PerspectiveY": prptY[i],
                                 "PerspectiveZ": prptZ[i],
                                 "Omega": rotX[i],
                                 "Phi": rotY[i],
                                 "Kappa": rotZ[i],
                                 "CameraID": camId[i],
                                 "SRS": srs
                             }
                if _time:
                    frame_dict["AcquisitionDate"] = _time[i] or default_time
                else:
                    frame_dict['AcquisitionDate'] = default_time
                frame_list.append(frame_dict)
        return frame_list
    
    def getDictList(self, fields, rows):
        dictList = []
        for row in rows:
            d = {}
            for i, item in enumerate(row):
                d[fields[i]] = item
            dictList.append(d)
        return dictList

    def getTableDefaults(self, sourceValues, userDefaults):
        # Retuns the default parameters to be filled in the table. Computed from the defualt parameter values entered by the user and the corresponding values from the source.
        tableDefaults = {}
        for userDefault in userDefaults:
            if userDefault['isDefault']:
                tableDefaults[userDefault['name']] = None
            else:
                if userDefault['value']:
                    tableDefaults[userDefault['name']] = userDefault['value']
                else:
                    tableDefaults[userDefault['name']] = sourceValues[userDefault['name']]
        return tableDefaults

    def feetToMeters(self, feet):
        return 0.3048*feet

    def writeToFC(self, inputValues, fcPath, userDefaults, averageZ):
        desc = arcpy.Describe(fcPath)
        outSRS = desc.spatialReference
        importFields = ['SHAPE@','Name','Image','AcquisitionDate','CamHeading','CamPitch','CamRoll','HFOV','VFOV','AvgHtAG','FarDist','NearDist','OIType','SortOrder','CamOri', 'ImgRot']
        fcCursor = arcpy.da.InsertCursor(fcPath,importFields)
        fc_rows = []
        for valueDict in inputValues:
            if valueDict['Raster'].startswith('http'):
                ossep = '/'
            else:
                ossep = os.sep
            urlSplitList = valueDict['Raster'].split(ossep)
            if len(urlSplitList) >= 2:
                shortName = ossep.join(urlSplitList[-2:])
                name = os.path.splitext(shortName)[0]
            else:
                name = None
            point = arcpy.Point()
            point.X = valueDict['PerspectiveX']
            point.Y = valueDict['PerspectiveY']
            inSRS = valueDict['SRS']
            inSRSObj = arcpy.SpatialReference(int(inSRS))
            pointGeometry = arcpy.PointGeometry(point, inSRSObj).projectAs(outSRS)
            pointCentroid = pointGeometry.centroid
            omega = math.radians(float(valueDict['Omega']))
            phi = math.radians(float(valueDict['Phi']))
            kappa = math.radians(float(valueDict['Kappa']))
            sensor_width = float(valueDict['SensorWidth'])
            sensor_height = float(valueDict['SensorHeight'])
            focal_length = float(valueDict['FocalLength'])
            radial_string = valueDict.get('Radial')
            imgRot = float(valueDict.get('ImgRot') or 0)
            k1 = '0'
            k2 = '0'
            k3 = '0'
            if radial_string:
                _, k1, k2, k3 = radial_string.strip().split(' ')

            camHeading = (math.atan2(-1 * (math.sin(phi)), (-1 * (-math.sin(omega)*math.cos(phi)))) * 180) / math.pi
            if camHeading < 0:
                camHeading = camHeading + 360
            camPitch = (math.acos(math.cos(omega)*math.cos(phi)) * 180 / math.pi)
            camRoll = (math.atan2((-1 * ((math.sin(omega)*math.sin(kappa)) - (math.cos(omega)*math.sin(phi)* math.cos(kappa)))), (math.sin(omega)*math.cos(kappa)) + (math.cos(omega)* math.sin(phi)* math.sin(kappa))) * 180) / math.pi

            HFOV = math.degrees(2 * math.atan(sensor_width/(2*focal_length)))
            VFOV = math.degrees(2 * math.atan(sensor_height/(2*focal_length)))
            if valueDict.get('SwapFOV'):
                HFOV, VFOV = VFOV, HFOV
            vwkid = ''
            if inSRSObj.linearUnitName.lower() != 'meter':#assuming unit is feet
                averageHeightAG = (self.feetToMeters(float(valueDict['PerspectiveZ'])) - float(averageZ))
                vwkid = 'ft'
            else:
                averageHeightAG = (float(valueDict['PerspectiveZ']) - float(averageZ))
            OIType = 'O'
            affineMatrix = np.array([[valueDict['A1'], valueDict['A2'], valueDict['A0']],
                                    [valueDict['B1'], valueDict['B2'], valueDict['B0']],
                                    [0, 0, 1]], dtype='float')
            inverseAffineMatrix = inv(affineMatrix)

            camOri = '|'.join(['2', str(inSRS), vwkid, valueDict['PerspectiveX'], valueDict['PerspectiveY'],
                              valueDict['PerspectiveZ'], str(math.degrees(omega)), str(math.degrees(phi)), str(math.degrees(kappa)),
                              str(inverseAffineMatrix[0][2]), str(inverseAffineMatrix[0][0]), str(inverseAffineMatrix[0][1]),
                              str(inverseAffineMatrix[1][2]), str(inverseAffineMatrix[1][0]), str(inverseAffineMatrix[1][1]), str(valueDict['FocalLength']),
                              valueDict['PrincipalX'], valueDict['PrincipalY'], k1, k2, k3])
            #if (camPitch == None or camPitch == ''):
                #nearDistance = None
            #else:
                #if camPitch > 0 and camPitch < 90 and averageHeightAG != '' and averageHeightAG is not None:
                    #nearDistance = averageHeightAG * math.tan((camPitch - (VFOV/2)) * math.pi / 180)
                #elif camPitch == 0 and averageHeightAG != '' and averageHeightAG is not None:
                    #nearDistance = -1 * averageHeightAG * math.sin(VFOV * math.pi / 360)
                #else:
                    #nearDistance = 200
    
            #if (camPitch == None or camPitch == ''):
                #farDistance = None
            #else:
                #if camPitch > 0 and camPitch < 90  and averageHeightAG != '' and averageHeightAG is not None:
                    #farDistance = averageHeightAG * math.tan((camPitch + (VFOV/2))* math.pi / 180)
                    #if farDistance < 0:
                        #farDistance = abs(farDistance)
                #elif camPitch == 0  and averageHeightAG != '' and averageHeightAG is not None:
                    #farDistance = averageHeightAG * math.sin(VFOV * math.pi / 360)
                    #if farDistance < 0:
                        #farDistance = abs(farDistance)
                #else:
                    #farDistance = 700
            if averageHeightAG and camPitch and camRoll:
                if abs(math.tan(math.pi * camRoll/180)) > 1:
                    nearDistance = abs(averageHeightAG * math.tan((camPitch - (HFOV/2)) * math.pi/180))
                    farDistance = abs(averageHeightAG * math.tan(((HFOV/2) + camPitch) * math.pi / 180))
                else:
                    nearDistance = abs(averageHeightAG * math.tan((camPitch - (VFOV/2)) * math.pi / 180))
                    farDistance = abs(averageHeightAG * math.tan(((VFOV/2) + camPitch) * math.pi / 180))

            else:
                nearDistance = 200
                farDistance = 700

            sourceValues = {
                               "CamPitch": camPitch,
                               "CamRoll": camRoll,
                               "CamHeading": camHeading,
                               "FarDist": farDistance,
                               "NearDist": nearDistance,
                               "AvgHtAG": averageHeightAG,
                               "HFOV": HFOV,
                               "VFOV": VFOV
                           }
            OIType = userDefaults['OIType'][0]
            fc_row = [pointCentroid, 
                      name,
                      valueDict['Raster'],
                      valueDict['AcquisitionDate']]
            fc_row.extend([sourceValues['CamHeading'], sourceValues['CamPitch'],
                            sourceValues['CamRoll'], sourceValues['HFOV'],
                            sourceValues['VFOV'], sourceValues['AvgHtAG'],
                            sourceValues['FarDist'], sourceValues['NearDist'],
                            OIType, 0, camOri, imgRot])
            fc_rows.append(fc_row)
            fcCursor.insertRow(fc_row)
        return fc_rows

    def writeToFCUltramap(self, eoFilename, preFix, postFix, rasterDir, rotatedCams, cameraType, productType, oicPath, defValues, averageZ, nadirType='panchromatic'):
        units = 'degrees'
        order = 'OPK'
        convFactor = 1.0
        intrinsicsLines = 0
        camLines = 0
        lstInput = []
        lstIntrinsics = []
        srs = []
        camName = []
        camSerid = []        
        camNameIDDir = {}
        timediff = 0

        camInitialLines__ = self.select_range_file(eoFilename, "[Cameras]", "[Intrinsics]")
        if (str(camInitialLines__[len(camInitialLines__)-2])) == "\n":
            camInitialLines = camInitialLines__[:-2]
        else:
            camInitialLines = camInitialLines__[:-1]

        camFinalLines = self.select_range_list1(camInitialLines, "0;", "{};".format(camInitialLines[-1].split(";")[0]))
        for oLine in camFinalLines:
            camLines = camLines + 1
            try:
                lstLine = oLine.strip().split(";")
            except Exception as exp:
                log.Message(str(exp),2)
            lstInput.append(lstLine)

        for i in range(0, camLines):
            camName.append(lstInput[i][3])
            camSerid.append(lstInput[i][1])            
            camNameIDDir[lstInput[i][0].strip()]=lstInput[i][3].strip()  # this is use in the frame table to map the camera id and camera names, so as to fill the right attributes

        intrinsicsInitialLines = self.select_range_file(eoFilename, "[Intrinsics]", "[Eccentricities]")
        intrinsicsFinalLines = self.select_range_list2(intrinsicsInitialLines, "0", "[Eccentricities]")

        for oLine in intrinsicsFinalLines:
            intrinsicsLines = intrinsicsLines + 1
            try:
                oLine= oLine.replace(" ","")
                lst = oLine.strip().split(";")
            except Exception as exp:
                log.Message(str(exp),2)
            lstIntrinsics.append(lst)

        eventInitial = self.select_range_endfile(eoFilename, "[Events]")
        srsLines = self.select_range_list1(eventInitial, "#", "#")

        for oLine in srsLines:
            try:
                lstLine0 = oLine.strip().split("=")
            except Exception as exp:
                log.Message(str(exp),2)
            srs.append(lstLine0)
        eventLines = self.select_range_endlist(eventInitial[4:], "0")
        totalLines,camId,imgId,prptX,prptY,prptZ,rotX,rotY,rotZ,_time = self.parseValues(eventLines, convFactor, cameraType, order, timediff)       
        defaultDatetime = self.getDefaultDatetimeUltramap(eoFilename, timediff)
        _time = [t or defaultDatetime for t in _time]
        frameFields, frameRows = self.frameUltraMap(rasterDir, totalLines,
                                                   camId,
                                                   imgId,
                                                   prptX,
                                                   prptY,
                                                   prptZ,
                                                   rotX,
                                                   rotY,
                                                   rotZ,
                                                   srs[0][1],
                                                   postFix,
                                                   preFix,
                                                   _time,
                                                   cameraType,
                                                   productType,
                                                   camNameIDDir,
                                                   nadirType)
        frames = self.getDictList(frameFields, frameRows)
        #frames1 = self.getFrameParams(rasterDir,totalLines,camId,imgId,prptX,prptY,prptZ,rotX,rotY,rotZ,srs[0][1],postFix,preFix,_time,cameraType,productType,camNameIDDir,defaultDatetime)
        cameraFields, cameraRows = self.cameraUltraMap(camLines, lstInput, lstIntrinsics, camSerid,
                           camName, rotatedCams)
        cameras = self.getDictList(cameraFields, cameraRows)
        merged = self.merge_lists_by_key(frames, cameras, 'CameraID')
        self.writeToFC(merged, oicPath, defValues, averageZ)

    def merge_lists_by_key(self, frames, cameras, key):
        for frame in frames:
            camera = [cam for cam in cameras if cam.get(key) == frame.get(key)]
            if camera:
                frame.update(camera[0])
        return frames

    def writeToFCAustralis(self, eoFolder, prefix, postfix, rasterDir, cameraType, oicPath, defValues, averageZ, srs):
        order = 'OPK'
        convFactor = 1.0
        allFrames = []
        timediff = 0
        for root, dirs, files in os.walk(eoFolder):
            for _file in files:
                if _file.lower().endswith('.eo'):
                    eoFilepath=os.path.join(root,_file)
                    openFile = open(eoFilepath,"r")
                    data= openFile.readlines()
                    start_image= data[0].split(' \n')[0]
                    end_image= data[-1].split(' \n')[0]
                    frameLines = self.select_range(eoFilepath, "{0}".format(start_image), "{0}".format(end_image))
                    totalLines,camId,imgId,prptX,prptY,prptZ,omega,phi,kappa,_time = self.parseValues(frameLines,convFactor,cameraType,order, timediff)
                    if rasterDir.startswith('http'):
                        rasterDirWithFolder = '/'.join([rasterDir,_file.split(".")[0]])
                    else:
                        rasterDirWithFolder = os.path.join(rasterDir,_file.split(".")[0])
                    frameFields, frameRows = self.frameAustralis(rasterDir,
                                                                totalLines,
                                                                camId,
                                                                imgId,
                                                                prptX,
                                                                prptY,
                                                                prptZ,
                                                                omega,
                                                                phi,
                                                                kappa,
                                                                postfix,
                                                                prefix,
                                                                _time,
                                                                cameraType,
                                                                _file,
                                                                srs)
                    frames = self.getDictList(frameFields, frameRows)
                    allFrames.extend(frames)
        cameraFields, cameraRows = self.cameraAustralis(eoFolder)
        cameras = self.getDictList(cameraFields, cameraRows)
        merged = self.merge_lists_by_key(allFrames, cameras, 'CameraID')
        self.writeToFC(merged, oicPath, defValues, averageZ)

    def writeToFCSanborn(self, eoFolder, prefix, postfix, rasterDir, cameraType, oicPath, defValues, averageZ):
        srs=[]
        timediff = 0
        for _file in os.listdir(eoFolder):  #in this case inputEO will be a directory
            if (_file.find("EO")!=-1):
                eoFilepath = os.path.join (eoFolder,_file)
            if(_file.find("Camera")!=-1):
                cameraFilepath = os.path.join (eoFolder,_file)


        openFile = open(eoFilepath, 'r') #Fetch the start image and end image
        read = openFile.readlines()
        for line in read:
            line = line.strip()
            if (line.startswith("Flight Date")):
                datetime= self.dttm(line.split(":")[1].strip(),0)
            if (line.startswith("Coordinate System")):
                srs.append(line.split("EPSG:")[1].replace("]",""))
                break
        ei = read[-1]
        end_image = ei.partition(',')[0].strip()
        for line in reversed(read):
            ep = line.rstrip()
            if line == '\n':
                if line in ['\n', '\r\n']:
                    break
            image_id = ep.partition(',')[0].strip()
            start_image = image_id

        openFile.close()
        units = 'radians'
        order = 'OPK'
        convFactor = (180/math.pi)
        frameLines = self.select_range(eoFilepath, "{0}".format(start_image), "{0}".format(end_image))
        totalLines,imgId,flightline,shotId,camId,prptX,prptY,prptZ,omega,phi,kappa = self.parseValues(frameLines,convFactor,cameraType,order,timediff)
        frameFields, frameRows = self.frameSanborn(rasterDir, totalLines,
                                                  flightline,
                                                  shotId,
                                                  imgId,
                                                  camId,
                                                  prptX,
                                                  prptY,
                                                  prptZ,
                                                  omega,
                                                  phi,
                                                  kappa,
                                                  srs[0],
                                                  postfix,
                                                  prefix,
                                                  datetime,
                                                  cameraType)
        frames = self.getDictList(frameFields, frameRows)
        cameraFields, cameraRows = self.cameraSanborn(cameraFilepath)
        cameras = self.getDictList(cameraFields, cameraRows)
        merged = self.merge_lists_by_key(frames, cameras, 'CameraID')
        self.writeToFC(merged, oicPath, defValues, averageZ)