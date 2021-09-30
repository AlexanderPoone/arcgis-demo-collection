from json import loads, dumps

from urllib.request import urlopen as u

from os.path import expanduser

import arcpy


v=u(f'https://geodata.gov.hk/gs/download-dataset/d4ccd9be-3bc0-449b-bd27-9eb9b615f2db/GeoJSON?fullset=1')

with open(expanduser('~/Desktop/download.geojson'), 'wb') as doc:
    doc.write(v.read())

with open(expanduser('~/Desktop/download.geojson'), encoding='utf-8') as file:
    d = loads(file.read())

for f in range(len(d['features'])):
	x,y = d['features'][f]['geometry']['coordinates']

	pointGeometry = arcpy.PointGeometry(arcpy.Point(x,y),arcpy.SpatialReference(2326))
	abc = pointGeometry.projectAs(arcpy.SpatialReference(4326), "Hong_Kong_1980_To_WGS_1984_1")
	d['features'][f]['geometry']['coordinates'] = [abc.firstPoint.X, abc.firstPoint.Y]
	del d['features'][f]['properties']['OBJECTID']

endres = dumps(d)

with open(expanduser('~/Desktop/test.geojson'), 'w', encoding='utf-8') as file:
	file.write(endres)

# arcpy.conversion.JSONToFeatures(expanduser('~/Desktop/test.geojson'), out_features, 'POINT')
