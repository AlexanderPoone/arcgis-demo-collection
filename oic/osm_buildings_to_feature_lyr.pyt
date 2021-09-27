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
from urllib.request import urlopen, Request

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

        # BBox xmin
        xmin = arcpy.Parameter(
            displayName="Extent min longitude (xmin)",
            name="xmin",
            datatype="GPDouble",
            parameterType="Required",
            direction="Input")

        # Extent xmax
        xmax = arcpy.Parameter(
            displayName="Extent max longitude (xmax)",
            name="xmax",
            datatype="GPDouble",
            parameterType="Required",
            direction="Input")

        # Extent ymin
        ymin = arcpy.Parameter(
            displayName="Extent min latitude (ymin)",
            name="ymin",
            datatype="GPDouble",
            parameterType="Required",
            direction="Input")

        # Extent ymax
        ymax = arcpy.Parameter(
            displayName="Extent max latitude (ymax)",
            name="ymax",
            datatype="GPDouble",
            parameterType="Required",
            direction="Input")

        # Output
        out_features = arcpy.Parameter(
            displayName="Output Features",
            name="out_features",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Output")
        
        out_features.schema.clone = True

        parameters = [table, zcolumn, out_features]
        
        return parameters


    def execute(self, parameters, messages):
        '''[out:json][timeout:999];(
way["building"]({parameters[0].valueAsText},{parameters[2].valueAsText},{parameters[1].valueAsText},{parameters[3].valueAsText});
relation["building"]["type"="multipolygon"]({parameters[0].valueAsText},{parameters[2].valueAsText},{parameters[1].valueAsText},{parameters[3].valueAsText});
);out;>;out qt;'''

        query = f'''<osm-script output="json" output-config="" timeout="999">
  <union into="_">
    <query into="_" type="way">
      <has-kv k="building" modv="" v=""/>
      <bbox-query s="{parameters[0].valueAsText}" w="{parameters[2].valueAsText}" n="{parameters[1].valueAsText}" e="{parameters[3].valueAsText}"/>
    </query>
    <query into="_" type="relation">
      <has-kv k="building" modv="" v=""/>
      <has-kv k="type" modv="" v="multipolygon"/>
      <bbox-query s="{parameters[0].valueAsText}" w="{parameters[2].valueAsText}" n="{parameters[1].valueAsText}" e="{parameters[3].valueAsText}"/>
    </query>
  </union>
  <print e="" from="_" geometry="skeleton" ids="yes" limit="" mode="body" n="" order="id" s="" w=""/>
  <recurse from="_" into="_" type="down"/>
  <print e="" from="_" geometry="skeleton" ids="yes" limit="" mode="body" n="" order="quadtile" s="" w=""/>
</osm-script>'''

        r = Request('http://overpass-api.de/api/interpreter', data=query)

        v = urlopen(r)
        # Convert unstructured GeoJSON into structured data

        obj = loads(v.read().decode(encoding='utf-8'))

        keys = set()

        for x in obj['features']:
            for y in x['properties']:
                keys.add(y)

        for x in range(len(obj['features'])):
            extrude = 6.0                           # Ugly shim: Default extrude height to 6 metres if data is not available
            if 'height' in obj['features'][x]['properties']:
                extrude = float(obj['features'][x]['properties']['height'])
            elif 'maxheight' in obj['features'][x]['properties']:
                extrude = float(obj['features'][x]['properties']['maxheight'])
            elif 'building:levels' in obj['features'][x]['properties']:
                extrude = float(obj['features'][x]['properties']['building:levels']) * 3

            for y in keys:
                if y not in obj['features'][x]['properties']:
                    obj['features'][x]['properties'][y] = ''

            obj['features'][x]['properties']['height'] = extrude

        with open('export2.geojson', 'w', encoding='utf-8') as f:
            f.write(dumps(obj))

        arcpy.conversion.JSONToFeatures('export2.geojson', parameters[4].valueAsText)