##############################################
#
#    OSM-Buildings to Feature Layer
#
#    Author:        Alex Poon (Esri China (H.K.))
#    Date:          Sep 27, 2020
#    Last update:   Sep 27, 2020
#
##############################################
import arcpy
from json import loads, dumps
from time import sleep
from urllib.request import urlopen

class Toolbox(object):
    def __init__(self):
        self.label =  "OSM-Buildings to Feature Layer"
        self.alias  = "OSMBldsToFeatureLyr"

        # List of tool classes associated with this toolbox
        self.tools = [OSMBldsToFeatureLyr] 

class OSMBldsToFeatureLyr(object):
    def __init__(self):
        self.label       = "OSM-Buildings to Feature Layer"
        self.description = "Get all OSM-Buildings data within a given extent to a Feature Layer."

    def getParameterInfo(self):
        #Define parameter definitions

        # Input table
        table = arcpy.Parameter(
            displayName="Input table",
            name="table",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Input")

        # Source Z Column
        zcolumn = arcpy.Parameter(
            displayName="Z Column",
            name="zcolumn",
            datatype="Field",
            parameterType="Required",
            direction="Input")

        zcolumn.filter.list = ['Short', 'Long', 'Float', 'Single', 'Double']
        zcolumn.parameterDependencies = [table.name]

        # Output
        out_features = arcpy.Parameter(
            displayName="Output Features",
            name="out_features",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Output")
        
        out_features.parameterDependencies = [table.name]
        out_features.schema.clone = True

        parameters = [table, zcolumn, out_features]
        
        return parameters


    def execute(self, parameters, messages):
        arcpy.FeatureTo3DByAttribute_3d(parameters[0].valueAsText, parameters[2].valueAsText, parameters[1].valueAsText)
        
        arcpy.AddField_management(parameters[2].valueAsText, "Height", "DOUBLE", field_alias="Height")
        
        arr = []
        with arcpy.da.SearchCursor(parameters[2].valueAsText, ["SHAPE@XY", parameters[1].valueAsText], spatial_reference=arcpy.SpatialReference(4326)) as cursor:
            for row in cursor:
                # Print x,y coordinates of each point feature
                x, y = row[0]

                for a in range(10):
                    try:
                        url = urlopen(f'https://www.geodetic.gov.hk/transform/v2/?inSys=wgsgeog&lat={y}&long={x}&h={row[1]}')

                        outjson = loads(url.read().decode(encoding='utf8'))
                        
                        arr.append((outjson['hkE'], outjson['hkN'], outjson['hkpd']))
                        break
                    except:
                        print('Retry after 2 seconds...')
                        sleep(2)

        arcpy.DefineProjection_management(parameters[2].valueAsText, arcpy.SpatialReference(2326, 5738))

        arr.reverse()

        with arcpy.da.UpdateCursor(parameters[2].valueAsText, ["SHAPE@XYZ", "Height"]) as cursor:
            for row in cursor:

                updateMat = arr.pop()

                row[0] = updateMat
                row[1] = updateMat[2]

                cursor.updateRow(row)

        arcpy.RecalculateFeatureClassExtent_management(parameters[2].valueAsText)