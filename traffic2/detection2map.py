'''
Image warping using manually inputted homeography points

Output Warped GeoTIFF for reference (GDAL)
'''
import arcpy

from datetime import datetime
from json import dumps, loads
import numpy as np
from os import remove
from PIL import Image
from skimage.transform import warp
from subprocess import check_output, DEVNULL

# For offset Web Mercator translation (from gdalinfo)
xmin = 					
ymin = 
xmax = 
ymax = 

# Generate large mapping grid


# The problem is y is flipped: (imgHeight - y) + ymin
warpCoords = {
	1: [],
	2: [],
	3: [],
	4: [],
	5: [],
	6: []
}

map_args =
[[],
[],
[]]

# Warp from list of coordinates to list of coordinates
'''
For N-D images, you can directly pass an array of coordinates. The first dimension specifies the coordinates in the input image, while the subsequent dimensions determine the position in the output image. E.g. in case of 2-D images, you need to pass an array of shape (2, rows, cols), where rows and cols determine the shape of the output image, and the first dimension contains the (row, col) coordinate in the input image. See scipy.ndimage.map_coordinates for further documentation.
'''
warped = warp(image, inverse_map)
warped = PIL.fromarray(warped)
warped.save('warped.png')

remove('warped.png')

# Offset

# either gdal_translate or gdal_create to create GeoTIFF
check_output(f'gdal_translate -of GTiff -a_srs EPSG:4326 -a_ullr {xmin} {ymin} {xmax} {ymax} warped.png preview.tif')

##########################################
#
#   Create polyline from points
#
##########################################

# The outputs should be the vehicle type (from YOLO), object identifier (from SiamMask), oriented bounding box (from SiamMask), and a list of timestamps.

# TODO: How to continue
fc = arcpy.CreateFeatureclass_management(arcpy.env.workspace, f'{date}_Trajectories', 'POLYLINE', None, 
                            'DISABLED', 'DISABLED', arcpy.SpatialReference(3857))

arcpy.AddField_management(fc, "id", "LONG")
arcpy.AddField_management(fc, "object_type", "TEXT", field_length = 50)
arcpy.AddField_management(fc, "obb", "TEXT", field_length = 9999)
arcpy.AddField_management(fc, "timestamps", "TEXT", field_length = 9999)

datetime.now().strftime()

cursor = arcpy.da.InsertCursor(fc, ["SHAPE@","id","object_type","obb","timestamps"])

for r in myJson:
	print([float(x) for x in r['coords'][6:-1].split(' ')])
	lng, lat = [float(x) for x in r['coords'][6:-1].split(' ')]
	pl = arcpy.Point(lng, lat)
	objectId=cursor.insertRow([])
del cursor


##########################################
#
#   Analysis: Peak Hours
#
##########################################