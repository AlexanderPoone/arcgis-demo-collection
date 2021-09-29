##############################################
#
#	Propagate Pitch, Roll
#
#	Author:		Alex Poon (Esri China (H.K.))
#	Date:		  Sep 29, 2021
#	Last update:   Sep 29, 2021
#
##############################################
import arcpy

class Toolbox(object):
	def __init__(self):
		self.label =  "Propagate Pitch, Roll"
		self.alias  = "PropagatePitchRoll"

		# List of tool classes associated with this toolbox
		self.tools = [PropagatePitchRoll] 

class PropagatePitchRoll(object):
	def __init__(self):
		self.label	   = "Propagate Pitch, Roll"
		self.description = "Propagate Pitch, Roll by jointable.xlsx"

	def getParameterInfo(self):
		# Input
		in_xlsx = arcpy.Parameter(
			displayName="jointable.xlsx",
			name="in_xlsx",
			datatype="DEFile",
			parameterType="Required",
			direction="Input")
		in_xlsx.filter.list = ['xlsx']

		parameters = [in_xlsx]
		
		return parameters

	def execute(self, parameters, messages):
		arcpy.conversion.ExcelToTable
		arcpy.management.Merge
