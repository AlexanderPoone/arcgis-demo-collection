##############################################
#
#	KML to EXIF
#
#	Author:		Alex Poon (Esri China (H.K.))
#	Date:		  Sep 28, 2021
#	Last update:   Sep 29, 2021
#
##############################################
import arcpy

from os import chdir, mkdir
from os.path import dirname
from re import findall
from subprocess import check_output
import xml.etree.ElementTree as ET
import warnings

class Toolbox(object):
	def __init__(self):
		self.label =  "KML to EXIF"
		self.alias  = "KMLToExif"

		# List of tool classes associated with this toolbox
		self.tools = [KMLToExif] 

class KMLToExif(object):
	def __init__(self):
		self.label	   = "KML to EXIF"
		self.description = "Propagate EXIF metadata of image files from a KML file."

	def getParameterInfo(self):
		# Input
		in_kml = arcpy.Parameter(
			displayName="Input KML File",
			name="in_kml",
			datatype="DEFile",
			parameterType="Required",
			direction="Input")
		in_kml.filter.list = ['kml','xml']

		parameters = [in_kml]
		
		return parameters

	def decdeg2dms(self, dd):
		mnt,sec = divmod(dd*3600,60)
		deg,mnt = divmod(mnt,60)
		return deg,mnt,sec

	def execute(self, parameters, messages):
		warnings.filterwarnings("ignore", category=DeprecationWarning) 

		try:
			a = check_output('conda install -y openpyxl pandas pil')
		except:
			pass
		try:
			sysPath = 'C:\\Program Files\\ArcGIS\\Pro\\bin\\Python\\envs\\arcgispro-py3'		  #sys.path[4]
			a=check_output([fr"{sysPath}\python.exe", fr"{sysPath}\Scripts\pip-script.py", "install", "piexif"])
			#a = check_output('conda install -y -c conda-forge piexif')
		except:
			pass

		from pandas import DataFrame
		from piexif import load, dump
		from PIL import Image

		##########################################
		tree = ET.parse(parameters[0].valueAsText)

		chdir(dirname(parameters[0].valueAsText))
		arcpy.AddMessage(dirname(parameters[0].valueAsText))
		ns = findall(r'\{.*?\}',tree.getroot().tag)[0]

		data = {}
		i = 0
		# mkdir
		for photo in tree.findall(f'.//{ns}PhotoOverlay'):
			path = photo.find(f'{ns}Icon').getchildren()[0].text
			_,_,_,heading,tilt,roll = [float(x.text) for x in photo.find(f'{ns}Camera').getchildren()]
			x,y,z = [float(x) for x in photo.find(f'{ns}Point').getchildren()[0].text.split(',')]	# KML always use (lng, lat)

			try:
				arcpy.AddMessage(path)

				im = Image.open(path)
				try:
					exif_dict = load(im.info["exif"])
				except:
					exif_dict = {}
					pass

				xRes = self.decdeg2dms(y)
				degX = xRes[0]
				minutesX = xRes[1]
				secondsX = xRes[2]

				yRes = self.decdeg2dms(x)
				degY = yRes[0]
				minutesY = yRes[1]
				secondsY = yRes[2]

				# 11 and 13 are reserved for PitchAngle and RollAngle

				exif_dict['GPS'] = {0: (2, 2, 0, 0), 1: b'N', 2: ((int(degX), 1), (int(minutesX), 1), (int(round(secondsX*1000)), 1000)), 3: b'E', 4: ((int(degY), 1), (int(minutesY), 1), (int(round(secondsY*1000)), 1000)), 5: 0, 6: (int(round(z*1000)), 1000), 17: (int(round(heading * 100)), 100), 18: b'WGS-8', 24: (int(round(heading * 100)), 100)}#, 29: dates}

				exif_bytes = dump(exif_dict)
				im.save(path, "jpeg", exif=exif_bytes)
			except Exception as e:
				# Log goes here
				arcpy.AddMessage(str(e))

			data[i] = {'Name': path, 'CamHeading': heading, 'CamPitch': tilt, 'CamRoll': roll, 'POINT_X': x, 'POINT_Y': y, 'POINT_Z': z}

			i += 1

		df = DataFrame.from_dict(data, orient='index')
		df.to_excel('jointable.xlsx', index=False)

		return True