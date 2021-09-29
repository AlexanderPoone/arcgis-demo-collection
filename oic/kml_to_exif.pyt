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


	def execute(self, parameters, messages):
		try:
			a = check_output('conda install -y openpyxl pandas pil piexif')
		except:
			pass

		from pandas import DataFrame
		from PIL import Image

		##########################################
		tree = ET.parse(parameters[0].valueAsText)

		chdir(dirname(parameters[0].valueAsText))

		ns = findall(r'\{.*?\}',tree.getroot().tag)[0]

		data = {}
		i = 0
		# mkdir
		for photo in tree.findall(f'.//{ns}PhotoOverlay'):
			path = photo.find(f'{ns}Icon').getchildren()[0].text
			_,_,_,heading,tilt,roll = [float(x.text) for x in photo.find(f'{ns}Camera').getchildren()]
			x,y,z = [float(x) for x in photo.find(f'{ns}Point').getchildren()[0].text.split(',')]    # KML always use (lng, lat)

			try:
				im = Image.open(path)
			except:
				# Log goes here
				pass

			data[i] = {'Name': path, 'CamHeading': heading, 'CamPitch': tilt, 'CamRoll': roll, 'POINT_X': x, 'POINT_Y': y, 'POINT_Z': z}

			i += 1

		df = DataFrame.from_dict(data, orient='index')
		df.to_excel('jointable.xlsx')