####################################################
#
#	Thumbnail Creator (rotating GIF)
#
####################################################

# Pagination 40, 60

import base64
from copy import copy
from glob import glob
import lxml.etree as ET
import os
from subprocess import run, check_output, DEVNULL
from zipfile import ZipFile

from elasticsearch import Elasticsearch
from flask import render_template
import imageio
from io import BytesIO
import pandas as pd
from pyproj import Proj
from pyproj.transformer import Transformer#, AreaOfInterest
from tika import parser
from re import findall, match

'''
{
	"objectId": null,
	"itemTitle": "",
	"typeTitle": "",
	"uploadUser": "",
	"description": "",
	"type": "",
	"createDate": "",
	"lastUpdateDate": "",
	"xmin": "",
	"xmax": "",
	"ymin": "",
	"ymax": "",
	"zmin": "",
	"zmax": "",
	"footprint": "shpfile",
	"isTextured": "",
	"fileSize": "",
	"tags": [],
	"xcentroid": "",
	"ycentroid": "",
	"zcentroid": "",
	"thumbnail": ""
}
'''


root = 'Z:/Shares/3D/spatialRepo/example_repo'

fileDescriptions = {'3ds': '3DS (Autodesk 3ds)',
'bmp': 'BMP (Bitmap Image)',
'citygml': 'CityGML',
'csv': 'CSV (Comma-separated Values)',
'dgn': 'DGN (CAD Design)',
'doc': 'DOC (Microsoft Word 97-2003)',
'docx': 'DOCX (Microsoft Word)',
'dwg': 'DWG (Autodesk Drawing)',
'fbx': 'FBX (Autodesk Filmbox)',
'fgdb': 'FGDB (File Geodatabase)',
'geotif': 'GeoTIFF (Georefenced Tag Image File Format)',
'geotiff': 'GeoTIFF (Georefenced Tag Image File Format)',
'glb': 'GLB (GL Transmission Format Binary)',
'gltf': 'GLTF (GL Transmission Format)',
'gml': 'GML (Geography Markup Language)',
'ifc': 'IFC (Industry Foundation Classes)',
'jpeg': 'JPEG Image',
'jpg': 'JPEG Image',
'max': '3DS MAX (Autodesk 3ds MAX project)',
'mdb': 'MDB (Microsoft Access Database)',
'obj': 'OBJ (Wavefront)',
'osgb': 'OSGB (OpenSceneGraph binary)',
'pdf': 'PDF (Adobe Acrobat)',
'png': 'PNG (Portable Network Graphics)',
'ppt': 'PPT (Microsoft PowerPoint 97-2003)',
'pptx': 'PPTX (Microsoft PowerPoint)',
'shp': 'SHP (Esri Shapefile)',
'skp': 'SKP (SketchUp)',
'tar': 'TAR (Tarball archive)',
'tif': 'TIFF (Tag Image File Format)',
'tiff': 'TIFF (Tag Image File Format)',
'wrl': 'WRL (VRML)',
'x3d': 'X3D (VRML)',
'xls': 'XLS (Microsoft Excel 97-2003)',
'xlsx': 'XLSX (Microsoft Excel)',
'zip': 'ZIP (Zipped file)'}

meshFormats = ('gltf', 'glb', '3ds', 'fbx', 'dae', 'ifc', 'obj', 'osgb', 'skp', 'wrl', 'x3d')

export_dict = {
	'fbx': 'FBX (Autodesk Filmbox)',
	'glb': 'GLB (glTF 2.0)',
	'obj': 'Zipped OBJ (Wavefront)',
	'osgb': 'OSGB (OpenSceneGraph binary)',
	'wrl': 'WRL (VRML)'
}

##################################################################

def init():
	for g in glob(f'{root}/*'):
		generateThumbnail(g)

def convertMetadata(dom=None, xmlfile=None):
	xsltPath = 'metadata_to_html_full.xsl'
	if dom is None:
		dom = ET.parse(xmlfile)
	xslt = ET.parse(xsltPath)
	transform = ET.XSLT(xslt)
	newdom = transform(dom)
	with open('dest.html', 'w') as f:
		f.write(ET.tostring(newdom).decode(encoding='utf8'))

def initDb():
	#'localhost'
	es = Elasticsearch()
	return es

def connectDb():
	db = 'localhost'
	return db

def insertDb():
	df = pd.read_excel(r'Z:\Shares\3D-i100_BUILDINGS_metadata.xlsx')
	print('Sample loaded.')
	for f in glob(r'D:\Project\repo_thumbnails\*.gif'):
		f.split('\\')[-1]
		#Base64 thumbnail
		image = Image.open(f)
		buffered = BytesIO()
		image.save(buffered, format="GIF")
		img_str = base64.b64encode(buffered.getvalue())
		#Extract tags

#@app.route('/repo', methods = ['GET'])
def repo():
	connectDb()

	listings = [{
	
	}]

	return render_template(
		'template.html',
		listings = listings
		# post=post,
		# tags=tags,
		# comments=comments,
		# recent=recent,
		# top_tags=top_tags,
		# form=form
	)

#@app.route('/repo/query', methods = ['GET'])
def repo_query():
	connectDb()

	listings = [{

	}]

	for x in range(res.page):
		exportFormats = copy(export_dict)
		if x['filename'] in meshFormats:
			try:
				del exportFormats[x['typeTitle']]
			except:
				pass
			x['exportFormats'] = exportFormats

	return render_template(
		'template.html',
		listings = listings
		# post=post,
		# tags=tags,
		# comments=comments,
		# recent=recent,
		# top_tags=top_tags,
		# form=form
	)

#@app.route('/repo_uploads', methods = ['POST'])
def repo_uploads():
	# WRITE
	generateThumbnail()

#@app.route('/repo_uploads/fetch/<path:text>', methods=['GET', 'POST'])
def repo_uploads_dl(text):
	return send_from_directory('repo_uploads', text)

# Test against 80 Grid
def test80Grid():
	return

def generateExample():
	df = pd.read_excel(r'Z:\Shares\3D-i100_BUILDINGS_metadata.xlsx')
	print('Sample loaded.')
	lst = df[(df['IS_DUPLICATE'] == 0) & (df['MATERIAL'] != 'UNTEXTURED')]['PATH'].dropna().tolist()

	paths = [fr'Z:/Shares/3D-i100/VRML_extracted/{x}' for x in lst]

	for p in paths:
		#writeFileStat(filename)
		generateThumbnail(p)
	# Write to db


def scanFile(filename):
	return parser.from_file(filename)

def generateThumbnail(filename, archive=None, archived=None):
	autofill = {}
	extension = filename.split('.')[-1].lower()

	if archive is not None:
		# unzip to tmp
		filename = f'C:/temp/{archived.filename}'#tmp.{extension}'
		archive.extract(archived, path='C:/temp')#filename)
		autofill['filesize'] = f'{archived.file_size} bytes'
	else:
		autofill['filesize'] = f'{os.stat(filename).st_size} bytes'

	if extension in ('gltf', 'glb', '3ds', 'fbx', 'dae', 'ifc', 'obj', 'osgb', 'skp', 'wrl', 'x3d'):
		autofill3d = thumbnail3d(filename)
		autofill = {**autofill, **autofill3d}
	elif extension in ('gml', 'citygml'):
		# check if the gml is a 3d mesh
		with open(filename, 'r') as f:
			gml = f.readall()
		res = match('<cityObjectMember>', gml) # find <cityObjectMember> by regex <bldg:Building<app:appearance>
		if res is not None:
			print('GML: This is a 3D object')
		else:
			print('GML: This is just gml')
	elif extension in ('tif', 'tiff', 'geotif', 'geotiff'):
		transformer = Transformer.from_crs(
			"epsg:2326",
			"epsg:3857",
			# area_of_interest=AreaOfInterest(114.200322, 22.312877, 114.215299, 22.329041),
		)

		# TIF
		run(f'magick convert "{filename}" -thumbnail "256x256>" D:/Project/repo_thumbnail/{filename}.gif')
		# DAL goes here...
		info = check_output(f'"C:/Image_Mgmt_Workflows/OptimizeRasters/GDAL/bin/gdalinfo.exe" "{filename}"', stdin=DEVNULL, stderr=DEVNULL).decode(encoding='utf-8')

		xmin, ymin = [float(x) for x in findall(r'(?<=Lower Left).*?(?=\))',info)[0].replace('(','').split(',  ')]
		if xmin == 0:
			extension = 'tif'
		else:
			extension = 'geotif'
			xmax, ymax = [float(x) for x in findall(r'(?<=Upper Right).*?(?=\))',info)[0].replace('(','').split(',  ')]

			coords = [*transformer.transform(xmin, ymin), *transformer.transform(xmax, ymax)]
	elif extension in ('jpg', 'jpeg', 'png', 'bmp'):
		# Graphics
		run(f'magick convert "{filename}" -thumbnail "256x256>" D:/Project/repo_thumbnail/{filename}.gif')
		info = check_output(f'magick identify -verbose "{filename}"', stdin=DEVNULL, stderr=DEVNULL).decode(encoding='utf-8')
		# TODO: magick info !!!!!!!!!!!!!!!!!!!!!!!!!!!
	elif extension == 'pdf':
		# PDF
		run(f'magick convert "{filename}" -thumbnail "256x256>" D:/Project/repo_thumbnail/{filename}.gif')
		meta = scanFile(filename)
		autofill = {*autofill, *meta['metadata']}
	elif extension in ('doc', 'docx'):
		# PowerPoint
		meta = scanFile(filename)
		autofill = {*autofill, *meta['metadata']}
	elif extension in ('ppt', 'pptx'):
		# PowerPoint
		meta = scanFile(filename)
		autofill = {*autofill, *meta['metadata']}
	elif extension in ('xls', 'xlsx'):
		# Excel
		meta = scanFile(filename)
		autofill = {*autofill, *meta['metadata']}
	elif extension == 'fgdb':
		# Spreadsheet
		pass
	elif extension == 'shp':
		# SHP
		pass
	elif extension == 'zip':
		# ZIP
		z = ZipFile(filename, 'a')
		compressed = [x for x in z.infolist() if not x.is_dir()]		  #.split('.')[-1]

		# one metadata file per individual 3D object, otherwise it does not make any sense
		# recurse
		for f in compressed:
			if f.filename.split('.')[-1] in meshFormats:
				generateThumbnail(f.filename, archive=z, archived=f)
	elif extension == 'tar':
		# TAR
		pass
	elif extension == 'csv':
		# CSV
		pass
	else:
		return

	if extension in fileDescriptions:
		autofill['format'] = fileDescriptions[extension]
	else:
		autofill['format'] = extension.upper()
	transform(filename, autofill)

def getCswProfile(extension):
	# Return generic tree for now
	xmlfile = 'CswProfiles/md_2.0_datasets_example.xml'
	dom = ET.parse(xmlfile)
	return dom

def transform(filename, autofill):
	ext = filename.split('.')[-1].lower()
	xmltree = getCswProfile(ext)

	def createSubNode(top, *args, **kwargs): 
		if top is None:
			root = xmltree.getroot()
		else:
			root = xmltree.Element(top)
		for key, val in kwargs.items():
			if type(val) == dict:
				c = CreateSubNode(key, **val)
			else:
				c = xmltree.Element(key)
				c.text = str(val)
			root.append(c)
		return root
	"""
	xmltree['metadata']['extent']														extent
	xmltree['metadata']['distinfo']['stdorder']['digform']['digtopt']['offoptn']		filesize
																						footprint
	xmltree['metadata']['distinfo']['stdorder']											format
	xmltree['metadata']['idinfo']['citation']['citeinfo']['edition']					version

	<digform>
		<digtinfo>
		 <formname>GEOTIFF</formname>G
		 <formvern>Geo-referenced Tagged-Image File Format</formvern>
		 <formcont>Data specifies at http://www.landsd.gov.hk/mapping/en/digital_map/digital_map.htm</formcont>
		</digtinfo>

	<offoptn>
	  <offmedia>DVD</offmedia>
	  <reccap>
	   <recden>4.7</recden>
	   <recdenu>Gigabytes</recdenu>
	  </reccap>
	  <recfmt>ISO 9660</recfmt>
	</offoptn>

	"""

	# TODO: <gmd:extent><gmd:EX_Extent><gmd:geographicElement><gmd:EX_GeographicBoundingBox><gmd:{azimuth}BoundLongitude><gco:Decimal>

	if 'extent' in autofill:
		createSubNode(None, {'metadata': {'extent': autofill['extent']}})									# extent
		#xmltree['metadata']['extent'] = autofill['extent']
	if 'filesize' in autofill:
		createSubNode(None, {'metadata': {'stdorder': {'digform': {'digtopt': {'offoptn': autofill['filesize']}}}}})
		#xmltree['metadata']['distinfo']['stdorder']['digform']['digtopt']['offoptn'] = autofill['filesize'] # filesize
	if 'format' in autofill:
		createSubNode(None, {'metadata': {'distinfo': {'stdorder': autofill['format']}}})
		#xmltree['metadata']['distinfo']['stdorder'] = autofill['format']									# format
	if 'edition' in autofill:
		createSubNode(None, {'metadata': {'idinfo': {'citation': {'citeinfo': {'edition': autofill['edition']}}}}})
		#xmltree['metadata']['idinfo']['citation']['citeinfo']['edition'] = autofill['edition']				# version
	if 'footprint' in autofill:
		createSubNode(None, {'metadata': {'CUSTOM': {'footprint': autofill['footprint']}}})
		#xmltree['metadata']['idinfo']['citation']['citeinfo']['edition'] = autofill['edition']				# version
	print(autofill)

coords2 = ''
extent3 = ''
# Async method
def thumbnail3d(filename):   #, fileptr
	global coords2
	global extent3

	autofill = {}
	ext = filename.split('.')[-1].lower()





	isTextured = False




	convertor = 'x3d' if ext == 'wrl' else ('autodesk_3ds' if ext == '3ds' else ext)
	convcomm = 'ifc.bim' if ext == 'ifc' else f'scene.{convertor}'
	threeDS = "obs[0].active_material.node_tree.nodes['Principled BSDF'].inputs['Emission Strength'].default_value = 0;" if ext == '3ds' else ''
	wrl = "mtl = bpy.data.materials['Material'];imn = mtl.node_tree.nodes.new('ShaderNodeTexImage');imn.image = bpy.data.images[[x for x in bpy.data.images.keys() if '.jpg' in x][0]];bsdf = mtl.node_tree.nodes['Principled BSDF'];mtl.node_tree.links.new(bsdf.inputs['Base Color'], imn.outputs['Color']);obs[0].active_material = mtl;" if ext == 'wrl' else ''
	axes = ", axis_forward='-Z', axis_up='Y'" if ext == 'wrl' else ('' if ext == 'skp' or ext == 'ifc' else ", axis_forward='Y', axis_up='Z'")
	if ext == '3ds':
		extenable = "from addon_utils import enable;enable('io_scene_3ds',default_set=True,persistent=True);"
	elif ext == 'skp':
		extenable = "from addon_utils import enable;enable('SketchUp_Importer',default_set=True,persistent=True);"
	elif ext == 'ifc':
		extenable = "from addon_utils import enable;enable('blenderbim',default_set=True,persistent=True);"
	else:
		extenable = ""

	###############################################
	#	Footprint extraction
	###############################################

	# Compress mesh to plane by overriding all z
	# Get vertice coordinates

	'''
	Footprint algorithm

	Check if mesh is big
	Big Blender bounds
	Small Blender Import
	All y = 0
	Remesh
	Merge vertices if close
	Laplace smoothing
	Select all
	Select interior
	Get (x,z) of all vertices
	Generate shapefile
	'''

	transformer = Transformer.from_crs(
		"epsg:2326",
		"epsg:3857",
		# area_of_interest=AreaOfInterest(114.200322, 22.312877, 114.215299, 22.329041),
	)

	fallbackAmount = 500000000

	if fallbackAmount:
		footprint = check_output(f"\"C:/Program Files/Blender Foundation/Blender 2.92/blender.exe\" -t 0 -b --python-expr \"import bpy;bpy.data.objects.remove(bpy.data.objects['Cube']);{extenable}bpy.ops.import_{convcomm}(filepath='{filename}'{axes});scene = bpy.context.scene;obj = [ob for ob in scene.objects if ob.type == 'MESH'][0];ctx = bpy.context.copy();ctx['active_object'] = obj;bpy.context.view_layer.objects.active = obj;bpy.ops.object.mode_set(mode = 'OBJECT');obj = bpy.context.active_object;bpy.ops.object.mode_set(mode = 'EDIT');bpy.ops.mesh.select_mode(type = 'VERT');bpy.ops.mesh.select_all(action = 'DESELECT');bpy.ops.object.mode_set(mode = 'OBJECT');\nfor v in obj.data.vertices:\n\tv.co.y = 0\nbpy.ops.object.modifier_add(type='REMESH');bpy.context.object.modifiers['Remesh'].voxel_size = 0.1;bpy.context.object.modifiers['Remesh'].adaptivity = 10;bpy.ops.object.modifier_apply(modifier='Remesh');bpy.ops.object.mode_set(mode = 'EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.mesh.remove_doubles(threshold=0.1);bpy.ops.object.mode_set(mode = 'OBJECT');bpy.ops.object.modifier_add(type='LAPLACIANSMOOTH');bpy.context.object.modifiers['LaplacianSmooth'].use_y = False;bpy.context.object.modifiers['LaplacianSmooth'].use_z = False;bpy.ops.object.modifier_set_active(modifier='LaplacianSmooth');bpy.context.object.modifiers['LaplacianSmooth'].lambda_border = 10;bpy.ops.object.modifier_apply(modifier='LaplacianSmooth');bpy.ops.object.mode_set(mode = 'EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.mesh.region_to_loop();bpy.ops.object.mode_set(mode = 'OBJECT');y = [list(v.vertices) for v in obj.data.edges if v.select];ordered = [];duple = y[0];\nwhile True:\n\tif duple[0] in ordered:\n\t\ttest = duple[1]\n\telse:\n\t\ttest = duple[0]\n\tordered.append(test)\n\ty.remove(duple)\n\ttestarr = [e for e in y if test in e]\n\tif len(testarr) == 0:\n\t\tbreak\n\tduple = testarr[0]\nprint([(obj.location.y - obj.data.vertices[v].co.z, obj.location.x + obj.data.vertices[v].co.x) for v in ordered])\"", stdin=DEVNULL, stderr=DEVNULL).decode(encoding='utf-8')

		coords = findall(r'\[.*?\]', footprint)
		exec(f'coords2 = {coords[0]}',globals())
		print(coords2)
		coords2 = [[list(transformer.transform(c[0],c[1])) for c in coords2]]
		
		autofill['footprint'] = coords2

	#######################################################
	#		Extent
	#######################################################
	# xmin ymin zmin xmax ymax zmax
	extent = check_output(f"\"C:/Program Files/Blender Foundation/Blender 2.92/blender.exe\" -t 0 -b --python-expr \"import bpy;bpy.data.objects.remove(bpy.data.objects['Cube']);{extenable}bpy.ops.import_{convcomm}(filepath='{filename}'{axes});scene = bpy.context.scene;obs = [ob for ob in scene.objects if ob.type == 'MESH'];ctx = bpy.context.copy();ctx['active_object'] = obs[0];ctx['selected_editable_objects'] = obs;bpy.ops.object.join(ctx);bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY',center='BOUNDS');print([obs[0].location.y - obs[0].dimensions.z / 2, obs[0].location.x - obs[0].dimensions.x / 2, obs[0].location.z - obs[0].dimensions.y / 2, obs[0].location.y + obs[0].dimensions.z / 2, obs[0].location.x + obs[0].dimensions.x / 2, obs[0].location.z + obs[0].dimensions.y / 2])\"", stdin=DEVNULL, stderr=DEVNULL).decode(encoding='utf-8')
	extent2 = findall(r'\[.*?\]', extent)
	exec(f'extent3 = {extent2[0]}',globals())
	print(extent3)
	'''
	>= 800000 and < 900000	 =>  normal
	>= 1000 and < 80000		=>  centeredAt800k
	else					   =>  "Not Georeferenced"
	'''
	georefType = 'not_georeferenced'
	if extent3[0] >= 800000 and extent3[0] < 900000:
		georefType = 'normal'

		extent3 = [*transformer.transform(extent3[0],extent3[1],extent3[2]), *transformer.transform(extent3[3],extent3[4],extent3[5])]
	elif extent3[0] >= 1000 and extent3[0] < 90000:
		georefType = 'centeredAt800k'
		extent3[0] += 800000
		extent3[1] += 800000
		extent3[3] += 800000
		extent3[4] += 800000

		extent3 = [*transformer.transform(extent3[0],extent3[1],extent3[2]), *transformer.transform(extent3[3],extent3[4],extent3[5])]

	autofill['extent'] = extent3

	#######################################################
	#		Thumbnail
	#######################################################
	#run(f"\"C:/Program Files/Blender Foundation/Blender 2.92/blender.exe\" -t 0 -b --python-expr \"import bpy;from math import radians;from os.path import join;bpy.data.objects.remove(bpy.data.objects['Cube']);{extenable}bpy.ops.import_{convcomm}(filepath='{filename}'{axes});scene = bpy.context.scene;obs = [ob for ob in scene.objects if ob.type == 'MESH'];ctx = bpy.context.copy();ctx['active_object'] = obs[0];ctx['selected_editable_objects'] = obs;bpy.ops.object.join(ctx);bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY',center='BOUNDS');obs[0].location.x = 0;obs[0].location.y = 0;obs[0].location.z = 0;obs[0].scale.x *= 0.05;obs[0].scale.y *= 0.05;obs[0].scale.z *= 0.05;{threeDS}{wrl}original_rotation = obs[0].rotation_euler;bpy.context.scene.render.film_transparent = True;bpy.context.scene.render.resolution_x = 256;bpy.context.scene.render.resolution_y = 256;\nfor step in range(32):\n\tobs[0].rotation_euler[2] = radians(step * (360.0 / 32));\n\tbpy.context.scene.render.filepath = join('D:/Project/repo_thumbnails', ('render%d.png' % step));\n\tbpy.ops.render.render(write_still = True);\n\tobs[0].rotation_euler = original_rotation\"")
	run(f"\"C:/Program Files/Blender Foundation/Blender 2.92/blender.exe\" -t 0 -b --python-expr \"import bpy;from math import radians;from os.path import join;bpy.data.objects.remove(bpy.data.objects['Cube']);{extenable}bpy.ops.import_{convcomm}(filepath='{filename}'{axes});scene = bpy.context.scene;obs = [ob for ob in scene.objects if ob.type == 'MESH'];ctx = bpy.context.copy();ctx['active_object'] = obs[0];ctx['selected_editable_objects'] = obs;bpy.ops.object.join(ctx);bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY',center='BOUNDS');obs[0].location.x = 0;obs[0].location.y = 0;obs[0].location.z = 0;obs[0].scale.x *= 0.05;obs[0].scale.y *= 0.05;obs[0].scale.z *= 0.05;{threeDS}original_rotation = obs[0].rotation_euler;bpy.context.scene.render.film_transparent = True;bpy.context.scene.render.resolution_x = 256;bpy.context.scene.render.resolution_y = 256;\nfor step in range(32):\n\tobs[0].rotation_euler[2] = radians(step * (360.0 / 32));\n\tbpy.context.scene.render.filepath = join('D:/Project/repo_thumbnails', ('render%d.png' % step));\n\tbpy.ops.render.render(write_still = True);\n\tobs[0].rotation_euler = original_rotation\"")
	#TODO: List scale

	images = []
	for f in range(32):
		a = imageio.imread(f'D:/Project/repo_thumbnails/render{f}.png')
		for q in range(256):
			for w in range(256):
				if a[q,w][3] == 0:
					a[q,w] = [255,255,255,255]
		images.append(a)

	savef = filename.replace("\\","/").split("/")[-1]
	imageio.mimsave(fr'D:/Project/repo_thumbnails/{savef}.gif', images)

	return autofill

if __name__ == '__main__':
	init()		#generateExample()