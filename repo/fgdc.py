import shapely


        <placekey>Tsuen Wan</placekey>
        <placekey>Kwai Tsing</placekey>
        <placekey>Tuen Mun</placekey>
        <placekey>Yuen Long</placekey>
        <placekey>Sheung Shui</placekey>
        <placekey>Fanling</placekey>
        <placekey>Tai Po</placekey>
        <placekey>Shatin</placekey>
        <placekey>Sai Kung</placekey>
        <placekey>Islands</placekey>

'''
Projection Declaration
'''

epsg2326 = '''<spref>
    <horizsys>
      <planar>
        <mapproj>
          <mapprojn>Transverse Mercator</mapprojn>
          <mapprojp>
            <feast>836694.05</feast>
            <fnorth>819069.80</fnorth>
            <latprjo>22.3121333</latprjo>
            <longcm>114.1785554</longcm>
            <sfctrmer>1.0</sfctrmer>
          </mapprojp>
        </mapproj>
        <planci>
          <plance>distance and bearing</plance>
          <distbrep>
            <distres>1</distres>
            <bearres>0.0002778</bearres>
            <bearunit>Degrees and decimal minutes</bearunit>
            <bearrefd>North</bearrefd>
            <bearrefm>Magnetic</bearrefm>
          </distbrep>
          <plandu>Millimetres</plandu>
        </planci>
      </planar>
      <planar>
        <gridsys>
          <gridsysn>Other Grid System's Definition</gridsysn>
          <othergrd>Hong Kong 1980 Grid</othergrd>
        </gridsys>
        <planci>
          <plance>coordinate pair</plance>
          <coordrep>
            <absres>1</absres>
            <ordres>1</ordres>
          </coordrep>
          <plandu>Millimetres</plandu>
        </planci>
      </planar>
      <geodetic>
        <horizdn>Hong Kong 1980 Geodetic Datum</horizdn>
        <ellips>International Hayford (1910)</ellips>
        <semiaxis>6378388</semiaxis>
        <denflat>297.0</denflat>
      </geodetic>
    </horizsys>
  </spref>'''

import shapely

def generatePlace():
	placekey = []

	l1 = {'hk':Hong Kong Special Administrative Region',{'nt': ['New Territories',{'': ''}],
	'kl': ['Kowloon',{'': ''}],
	'is': ['Hong Kong',{'': ''}]
	}}

	for in l1:
		if intersect():
			placekey.append()
			for in l2:
				if intersect():
					for in l3:
						if intersect():

    pass


def versioning:



descript.abstract



'''
<digtinfo>
  <formname>WRL</formname>
  <formvern>VRML 97</formvern>
  <formcont>Data specifies at &lt;http://www.landsd.gov.hk/mapping/en/digital_map/digital_map.htm&gt;.</formcont>
</digtinfo>
'''






fileDescriptions = {'3ds': '3DS (Autodesk 3ds)',
'bmp': '',
'citygml': 'CityGML',
'csv': '',
'fbx': 'FBX (Autodesk Filmbox)',
'fgdb': 'FGDB (File Geodatabase)',
'geotif': '',
'geotiff': '',
'glb': '',
'gltf': '',
'gml': '',
'ifc': '',
'jpeg': '',
'jpg': '',
'max': '3DS MAX (Autodesk 3ds MAX project)',
'obj': 'OBJ (Wavefront)',
'osgb': 'OSGB (OpenSceneGraph binary)',
'pdf': 'PDF (Adobe Acrobat)',
'png': '',
'shp': 'SHP (Esri Shapefile)',
'skp': 'SKP (SketchUp)',
'tar': '',
'tif': '',
'tiff': '',
'wrl': 'VRML 97',
'x3d': 'X3D (VRML)',
'zip': ''}