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
		in_oic = arcpy.Parameter(
			displayName="Input Oriented Imagery Catalog",
			name="in_oic",
			datatype=["DEFile", "GPGroupLayer"],
			parameterType="Required",
			direction="Input")		# Input

		in_xlsx = arcpy.Parameter(
			displayName="jointable.xlsx",
			name="in_xlsx",
			datatype="DEFile",
			parameterType="Required",
			direction="Input")
		in_xlsx.filter.list = ['xlsx']

		parameters = [in_oic, in_xlsx]
		
		return parameters

	def execute(self, parameters, messages):
		resultTbl = arcpy.conversion.ExcelToTable(parameters[1].valueAsText)
		arcpy.management.CalculateField(resultTbl, 'joinField', '$Name$.split("/")')
		arcpy.management.Merge([resultTbl, parameters[0].valueAsText], parameters[0].valueAsText)
