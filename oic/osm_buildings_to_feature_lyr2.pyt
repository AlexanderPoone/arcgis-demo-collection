##############################################
#
#    OSM-Buildings to Feature Layer
#
#    Author:        Alex Poon (Esri China (H.K.))
#    Date:          Sep 27, 2021
#    Last update:   Sep 27, 2021
#
##############################################

'''
import bpy

bpy.data.window_managers["WinMan"].addon_search = "osm"
bpy.context.scene.blosm.minLon = 31.256
bpy.context.scene.blosm.maxLon = 31.258
bpy.context.scene.blosm.minLat = 55.748
bpy.context.scene.blosm.minLon = 31.21
bpy.context.scene.blosm.maxLon = 31.26
bpy.context.scene.blosm.minLon = 31.21
bpy.context.scene.blosm.minLat = 31.21
bpy.context.scene.blosm.maxLon = 31.26
bpy.context.scene.blosm.maxLat = 31.26
bpy.context.scene.blosm.minLon = 121.468
bpy.context.scene.blosm.maxLon = 121.54
#A valid directory for data in the addon preferences isn't set
bpy.context.space_data.system_bookmarks_active = 1
bpy.context.scene.blosm.water = False
bpy.context.scene.blosm.forests = False
bpy.context.scene.blosm.vegetation = False
bpy.context.scene.blosm.highways = False
bpy.ops.object.join()
bpy.ops.blosm.import_data()
bpy.context.scene.blosm.terrainObject = "map.osm_buildings"
bpy.context.scene.blosm.terrainObject = ""
bpy.context.scene.blosm.dataType = 'terrain'
bpy.ops.object.shade_smooth()
bpy.ops.blosm.import_data()
bpy.context.scene.hide_viewport = True
bpy.context.space_data.shading.type = 'WIREFRAME'
bpy.context.space_data.shading.type = 'MATERIAL'
bpy.context.space_data.shading.type = 'SOLID'
bpy.context.space_data.shading.type = 'SOLID'
bpy.context.scene.hide_viewport = False
bpy.context.scene.blosm.dataType = 'osm'
bpy.context.scene.blosm.terrainObject = "Terrain"
bpy.ops.outliner.item_activate(extend=False, deselect_all=True)
bpy.ops.outliner.delete()
bpy.context.scene.blosm.singleObject = False
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
bpy.ops.object.editmode_toggle()
bpy.ops.mesh.select_all(action='DESELECT')
bpy.ops.mesh.select_mode(type='FACE')
bpy.ops.object.editmode_toggle()
bpy.ops.object.editmode_toggle()
bpy.ops.mesh.select_mode(type='VERT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.remove_doubles()
bpy.ops.mesh.region_to_loop()
bpy.ops.mesh.select_all(action='INVERT')
bpy.ops.mesh.dissolve_verts(use_face_split=False, use_boundary_tear=False)
bpy.ops.object.editmode_toggle()
bpy.ops.object.join()
bpy.ops.object.join()
bpy.ops.object.join()
bpy.ops.object.join()
bpy.ops.blosm.import_data()
bpy.context.scene.hide_viewport = True
bpy.ops.outliner.item_activate(extend=False, deselect_all=True)
bpy.ops.outliner.item_activate(extend=False, deselect_all=True)
bpy.ops.outliner.item_activate(extend=False, deselect_all=True)
bpy.ops.outliner.item_activate(extend=False, deselect_all=True)
bpy.ops.outliner.item_activate(extend=False, deselect_all=True)
bpy.ops.outliner.item_activate(extend=False, deselect_all=True)
bpy.ops.outliner.item_activate(extend=False, deselect_all=True)
bpy.data.window_managers["WinMan"].(null) = True
bpy.context.space_data.system_bookmarks_active = 1
bpy.context.space_data.params.filename = "test.obj"
'''

import arcpy
from json import loads, dumps
from time import sleep
from urllib.request import urlopen, Request
from subprocess import check_output
from zipfile import ZipFile
#import sys

class Toolbox(object):
    def __init__(self):
        self.label =  "OSM-Buildings to Feature Layer2"
        self.alias  = "OSMBldsToFeatureLyr2"

        # List of tool classes associated with this toolbox
        self.tools = [OSMBldsToFeatureLyr2] 

class OSMBldsToFeatureLyr2(object):
    def __init__(self):
        self.label       = "OSM-Buildings to Feature Layer2"
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
        xmin.value="22.029637800701"

        # Extent xmax
        xmax = arcpy.Parameter(
            displayName="Extent max longitude (xmax)",
            name="xmax",
            datatype="GPDouble",
            parameterType="Required",
            direction="Input")
        xmax.value="22.252877311245"

        # Extent ymin
        ymin = arcpy.Parameter(
            displayName="Extent min latitude (ymin)",
            name="ymin",
            datatype="GPDouble",
            parameterType="Required",
            direction="Input")
        ymin.value="113.41117858887"

        # Extent ymax
        ymax = arcpy.Parameter(
            displayName="Extent max latitude (ymax)",
            name="ymax",
            datatype="GPDouble",
            parameterType="Required",
            direction="Input")
        ymax.value="113.82316589355"

        # Output
        out_features = arcpy.Parameter(
            displayName="Output Features",
            name="out_features",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Output")
        
        #out_features.schema.clone = True

        #"22.029637800701" w="113.41117858887" n="22.252877311245" e="113.82316589355"
        parameters = [xmin, xmax, ymin, ymax, out_features]
        
        return parameters


    def execute(self, parameters, messages):

        # Download dependencies

        v = urlopen('')
        with open(v):
            ZipFile

        # Filter buildings





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

        r = Request('http://overpass-api.de/api/interpreter', data=query.encode())

        v = urlopen(r)
        # Convert unstructured GeoJSON into structured data

        obj = loads(v.read().decode(encoding='utf-8'))

        try:
            sysPath = 'C:\\Program Files\\ArcGIS\\Pro\\bin\\Python\\envs\\arcgispro-py3'      #sys.path[4]
            a=check_output([fr"{sysPath}\python.exe", fr"{sysPath}\Scripts\pip-script.py", "install", "osm2geojson"])
        except:
            pass

        from osm2geojson import json2geojson

        obj = json2geojson(obj)

        keys = set()

        for x in obj['features']:
            x['properties']['tags']['id'] = x['properties']['id']
            x['properties'] = x['properties']['tags']
            for y in x['properties']:
                keys.add(y)

        for x in range(len(obj['features'])):
            extrude = 6.0                           # Ugly shim: Default extrude height to 6 metres if data is not available
            if 'height' in obj['features'][x]['properties']:
                extrude = float(obj['features'][x]['properties']['height'])
            elif 'maxheight' in obj['features'][x]['properties']:
                extrude = float(obj['features'][x]['properties']['maxheight'])
            elif 'building:levels' in obj['features'][x]['properties']:
                extrude = float(obj['features'][x]['properties']['building:levels'].split(';')[0]) * 3

            for y in keys:
                if y not in obj['features'][x]['properties']:
                    obj['features'][x]['properties'][y] = ''

            obj['features'][x]['properties']['height'] = extrude

        with open('export2.geojson', 'w', encoding='utf-8') as f:
            f.write(dumps(obj))

        arcpy.conversion.JSONToFeatures('export2.geojson', parameters[4].valueAsText)