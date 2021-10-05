################################################
#
#	TomTom Traffic
#
################################################

# Upload
from arcgis.gis import GIS

from base64 import b64encode, b64decode

from google.protobuf.json_format import MessageToDict
import ProtobufTrafficFlow_v8_pb2 as TF


from json import loads

from zipfile import ZipFile

import requests
import shapefile

from glob import glob
from datetime import datetime

from concurrent.futures import ThreadPoolExecutor

from pickle import dump as pdump, load as pload

from os.path import expanduser

#from pymssql import connect

from datetime import datetime

# Conversion from 4326 to 3857 needed to measure length
'https://pyproj4.github.io/pyproj/stable/api/geod.html#pyproj.Geod.line_length'
'https://stackoverflow.com/a/35025274'
from pyproj import Proj
from pyproj.transformer import Transformer

from shapely.geometry import Point, LineString

layer_name = 'TomTom Traffic Updated'

def create():
	gis = GIS('https://www.arcgis.com', username='<ENTER YOUR ARCGIS ONLINE USERNAME HERE>', password='<WARNING! PLEASE ENCRYPT YOUR PASSWORD AND PUT IT IN A SAFE LOCATION INSTEAD OF DIRECTLY ENTERING THE PASSWORD HERE>')



	content_proto = "content_20210715-Thu-152118-HKT+0800.proto"   #"D:/content_20210715-Thu-152118-HKT+0800.proto"
	my_trafficFlowGroup = TF.TrafficFlowGroup()

	f = open(content_proto, 'r+b')
	my_trafficFlowGroup.ParseFromString(f.read())
	f.close()




	openlr_avgspeed_dict = {}
	# Check if there is section

	for trafficflow in my_trafficFlowGroup.trafficFlow:
		openlr = str(b64encode(trafficflow.location.openlr),"utf-8")			#average_speed_all_segments
		if len(trafficflow.sectionSpeed)>0:
			openlr_avgspeed_dict[openlr] = ({
				'startOffsetInMeters': [ss.startOffsetInMeters for ss in trafficflow.sectionSpeed],
				# 'averageSpeedKmph': [ss.speed.averageSpeedKmph for ss in trafficflow.sectionSpeed],
				# 'travelTimeSeconds': [ss.speed.travelTimeSeconds for ss in trafficflow.sectionSpeed],
				# 'relativeSpeed': [ss.speed.relativeSpeed for ss in trafficflow.sectionSpeed],
				'trafficCondition': [ss.speed.DESCRIPTOR.fields_by_name['trafficCondition'].enum_type.values_by_number[ss.speed.trafficCondition].name for ss in trafficflow.sectionSpeed]
			})
		else:
			openlr_avgspeed_dict[openlr] = {
				'startOffsetInMeters': 0,
				# 'averageSpeedKmph': trafficflow.speed[0].averageSpeedKmph,
				# 'travelTimeSeconds': trafficflow.speed[0].travelTimeSeconds,
				# 'relativeSpeed': trafficflow.speed[0].relativeSpeed,
				'trafficCondition': trafficflow.speed[0].DESCRIPTOR.fields_by_name['trafficCondition'].enum_type.values_by_number[trafficflow.speed[0].trafficCondition].name
			}


	fail_openlr_dict = []
	succeed_openlr_dict = {}


	dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

	def decode_openlr(openlr):
		url = 'http://localhost:9000/v1/o2local'
		myobj = {'openLrCode': openlr}
		response = requests.post(url, data=myobj)

		json_data = loads(response.text)
		if response.status_code == 200:
			speed = openlr_avgspeed_dict[openlr]
			succeed_openlr_dict[openlr] = {
				'startOffsetInMeters': speed['startOffsetInMeters'],
				'shape': sum([x['geometry']['coordinates'] for x in json_data['features']],[]),			# Flatten array
				'isOneway': True in [x['properties']['dir'] for x in json_data['features']],
				'averageSpeedKmph': -1,#speed['averageSpeedKmph'],
				'travelTimeSeconds': -1,#speed['travelTimeSeconds'],
				'relativeSpeed': -1,#speed['relativeSpeed'],
				'trafficCondition': speed['trafficCondition'],
				'lastUpdate': dt
			}

		
		elif response.status_code == 500:
			fail_openlr_dict.append((openlr,json_data['errMsg'][85:]))
		else:
			print(code, response.status_code)
		return json_data

	print(len(openlr_avgspeed_dict))

	##############################################################################

	# get past keys and set speed to -1 (hide)
	all_protos = glob('D:/traffic_protos/*')#D:/traffic_protos/*

	print(len(all_protos))

	for content_proto in all_protos:
		print(content_proto)
		my_trafficFlowGroup = TF.TrafficFlowGroup()

		f = open(content_proto, 'r+b')
		my_trafficFlowGroup.ParseFromString(f.read())
		f.close()


		for trafficflow in my_trafficFlowGroup.trafficFlow:
			openlr = str(b64encode(trafficflow.location.openlr),"utf-8")
			if openlr not in openlr_avgspeed_dict:
				#average_speed_all_segments = trafficflow.speed[0].averageSpeedKmph
				if len(trafficflow.sectionSpeed)>0:
					openlr_avgspeed_dict[openlr] = ({
						'startOffsetInMeters': [ss.startOffsetInMeters for ss in trafficflow.sectionSpeed],
						# 'averageSpeedKmph': [ss.speed.averageSpeedKmph for ss in trafficflow.sectionSpeed],
						# 'travelTimeSeconds': [ss.speed.travelTimeSeconds for ss in trafficflow.sectionSpeed],
						# 'relativeSpeed': [ss.speed.relativeSpeed for ss in trafficflow.sectionSpeed],
						'trafficCondition': [ss.speed.DESCRIPTOR.fields_by_name['trafficCondition'].enum_type.values_by_number[ss.speed.trafficCondition].name for ss in trafficflow.sectionSpeed]
					})
				else:
					openlr_avgspeed_dict[openlr] = {
						'startOffsetInMeters': 0,
						# 'averageSpeedKmph': -1,
						# 'travelTimeSeconds': -1,
						# 'relativeSpeed': -1,
						'trafficCondition': trafficflow.speed[0].DESCRIPTOR.fields_by_name['trafficCondition'].enum_type.values_by_number[trafficflow.speed[0].trafficCondition].name
					}

	##############################################################################

	cnt = 0
	for key in openlr_avgspeed_dict.keys():
		print(cnt)
		cnt+=1
		decode_openlr(key)



	#print(succeed_openlr_dict)

	# Upload as CSV/JSON

	w = shapefile.Writer(expanduser(f'~/Desktop/{layer_name}.shp'))


	"""
	'shape': sum([x['geometry']['coordinates'] for x in json_data['features']],[]),			# Flatten array
	'isOneway': True in [x['properties']['dir'] for x in json_data['features']],
	'averageSpeedKmph': speed['averageSpeedKmph'],
	'travelTimeSeconds': speed['travelTimeSeconds'],
	'relativeSpeed': speed['relativeSpeed'],
	'trafficCondition': speed['trafficCondition'],
	'lastUpdate': dt
	"""

	w.field('openLR', 'C')
	w.field('offset', 'N')
	w.field('isOneway', 'L')
	w.field('avgSpdKmph', 'N')
	w.field('traSeconds', 'N')
	w.field('relSpeed', 'N')
	w.field('condition', 'C')
	w.field('lastUpdate', 'C')

	# convert the flattened array to WebMercator if it can be bisected
	
	transformer = Transformer.from_crs(
		"epsg:4326",
		"epsg:3857",
		# area_of_interest=AreaOfInterest(114.200322, 22.312877, 114.215299, 22.329041),
	)	
	transformerRev = Transformer.from_crs(
		"epsg:3857",
		"epsg:4326",
		# area_of_interest=AreaOfInterest(114.200322, 22.312877, 114.215299, 22.329041),
	)
	for x in succeed_openlr_dict:
		if isinstance(succeed_openlr_dict[x]['startOffsetInMeters'], list):
			print(succeed_openlr_dict[x]['shape'])
			shapeInMerc = [transformer.transform(y[1],y[0]) for y in succeed_openlr_dict[x]['shape']]
			#print(shapeInMerc)
			lstr = LineString(shapeInMerc)
			#print(lstr)

			diffs = []
			for z in range(1,len(succeed_openlr_dict[x]['startOffsetInMeters'])):
				diffs.append(succeed_openlr_dict[x]['startOffsetInMeters'][z]-succeed_openlr_dict[x]['startOffsetInMeters'][z-1])
			
			print(succeed_openlr_dict[x]['startOffsetInMeters'], diffs)

			def break_line_max_length(line):
				if len(diffs) == 0:
					dist = 999999999
				else:
					dist = diffs.pop(0)

				if line.length <= dist:
					return [line]
				else: 
					segments = cut(line, dist)
					return [segments[0]] + break_line_max_length(segments[1])

			def cut(line, distance):
				# Cuts a line in two at a distance from its starting point
				if distance <= 0.0 or distance >= line.length:
					return [line]
				coords = list(line.coords)
				for i, p in enumerate(coords):
					pd = line.project(Point(p)) 
					if pd == distance:
						return [
							LineString(coords[:i+1]),
							LineString(coords[i:])]
					if pd > distance:
						cp = line.interpolate(distance)
						return [
							LineString(coords[:i] + [(cp.x, cp.y)]),
							LineString([(cp.x, cp.y)] + coords[i:])]

			splat = [list(s.coords) for s in break_line_max_length(lstr)]

			for s in range(len(splat)):
				# Project back to (lng, lat) for shapefile
				out = [transformerRev.transform(*t)[::-1] for t in splat[s]]

				w.line([ out ])
				w.record(x,
					succeed_openlr_dict[x]['startOffsetInMeters'][s],
					succeed_openlr_dict[x]['isOneway'],
					succeed_openlr_dict[x]['averageSpeedKmph'],
					succeed_openlr_dict[x]['travelTimeSeconds'],
					succeed_openlr_dict[x]['relativeSpeed'],
					succeed_openlr_dict[x]['trafficCondition'][s],
					succeed_openlr_dict[x]['lastUpdate'])

			print('*********************************')

			##########################################
		else:
			w.line([ succeed_openlr_dict[x]['shape'] ])
			w.record(x,
				succeed_openlr_dict[x]['startOffsetInMeters'],
				succeed_openlr_dict[x]['isOneway'],
				succeed_openlr_dict[x]['averageSpeedKmph'],
				succeed_openlr_dict[x]['travelTimeSeconds'],
				succeed_openlr_dict[x]['relativeSpeed'],
				succeed_openlr_dict[x]['trafficCondition'],
				succeed_openlr_dict[x]['lastUpdate'])

	w.close()




	with ZipFile(expanduser(f'~/Desktop/{layer_name}.zip'), 'w') as z:
		z.write(expanduser(f'~/Desktop/{layer_name}.dbf'))
		z.write(expanduser(f'~/Desktop/{layer_name}.shp'))
		z.write(expanduser(f'~/Desktop/{layer_name}.shx'))


	data = expanduser(f"~/Desktop/{layer_name}.zip")
	shpfile = gis.content.add({}, data)
	published_service = shpfile.publish()

	# Somewhere to store the array of keys
	with open('openlr.pickle','wb') as f:
		pdump(list(succeed_openlr_dict.keys()), f) 


def nullifyAll():
	gis = GIS('https://www.arcgis.com', username='<ENTER YOUR ARCGIS ONLINE USERNAME HERE>', password='<WARNING! PLEASE ENCRYPT YOUR PASSWORD AND PUT IT IN A SAFE LOCATION INSTEAD OF DIRECTLY ENTERING THE PASSWORD HERE>')

	lyr = gis.content.search(layer_name, item_type='Feature')[0].layers[0]
	feats = lyr.query().to_dict()['features']

	for f in feats:
		f['attributes']['avgSpdKmph'] = None
		f['attributes']['relSpeed'] = None

	status = lyr.edit_features(updates=feats)



def update():
	gis = GIS('https://www.arcgis.com', username='<ENTER YOUR ARCGIS ONLINE USERNAME HERE>', password='<WARNING! PLEASE ENCRYPT YOUR PASSWORD AND PUT IT IN A SAFE LOCATION INSTEAD OF DIRECTLY ENTERING THE PASSWORD HERE>')

	lyr = gis.content.search(layer_name, item_type='Feature')[0].layers[0]
	feats = lyr.query().to_dict()
	

	print('************************************')

	with open('openlr.pickle','rb') as f:
		allOpenLR = set(pload(f))
		#print(allOpenLR)
 






	while True:
		try:
			req = requests.get('https://traffic.tomtom.com/tsq/hdf-detailed/HKG-HDF_DETAILED-OPENLR/<ENTER YOUR TOMTOM INTERMEDIATE TRAFFIC SERVICE API KEY HERE>/content.proto')
		except:
			print('Could not reach TomTom. Retrying...')
			continue
		req_ts = datetime.now()
		req_ts_readable = req_ts.strftime("%Y-%m-%d %H:%M:%S")

		my_trafficFlowGroup = TF.TrafficFlowGroup()
		my_trafficFlowGroup.ParseFromString(req.content)



		########################################################
		#History
		mytime = datetime.now().strftime("%Y%m%d %H%M%S")
		with open(f'D:/TomTomHistory/{mytime}.proto', 'wb') as f:
			f.write(req.content)
		########################################################



		openlr_avgspeed_dict = {}

		def payload(trafficflow):

			# TODO: Handle fine sections


			featuresToBeUpdated = []

			openlr = str(b64encode(trafficflow.location.openlr),"utf-8")
			openlr_avgspeed_dict[openlr] = {
				'averageSpeedKmph': trafficflow.speed[0].averageSpeedKmph,
				'travelTimeSeconds': trafficflow.speed[0].travelTimeSeconds,
				'relativeSpeed': trafficflow.speed[0].relativeSpeed,
				'trafficCondition': trafficflow.speed[0].DESCRIPTOR.fields_by_name['trafficCondition'].enum_type.values_by_number[trafficflow.speed[0].trafficCondition].name
			}

			"""
			try:
				conn=connect('localhost', 'sa', 'p@ssw0rd', 'TomTomHistory')
				crs=conn.cursor()
				'''
				[openlr]
				,[averageSpeedKmph]
				,[travelTimeSeconds]
				,[relativeSpeed]
				,[trafficCondition]
				,[startOffsetInMeters]
				,[fetchTime]
				'''
				crs.execute(f"INSERT INTO TomTomHistory VALUES (%s,%d,%d,%d,%s,%d,%d,%s)",
					(openlr,
					trafficflow.speed[0].averageSpeedKmph,
					trafficflow.speed[0].travelTimeSeconds,
					trafficflow.speed[0].relativeSpeed,
					trafficflow.speed[0].DESCRIPTOR.fields_by_name['trafficCondition'].enum_type.values_by_number[trafficflow.speed[0].trafficCondition].name,
					0,
										0,
					req_ts
					))
				conn.commit()

				for section in trafficflow.sectionSpeed:
					crs.execute(f"INSERT INTO TomTomHistory VALUES (%s,%d,%d,%d,%s,%d,%d,%s)",
					(openlr,
					section.speed.averageSpeedKmph,
					section.speed.travelTimeSeconds,
					section.speed.relativeSpeed,
					section.speed.DESCRIPTOR.fields_by_name['trafficCondition'].enum_type.values_by_number[section.speed.trafficCondition].name,
										1,
					section.startOffsetInMeters,
					req_ts
					))
					conn.commit()


				conn.close()
			except Exception as e:
				print(225,e)
			"""

			findResults = [x for x in feats['features'] if x['attributes']['openLR'] == openlr]

			if len(findResults) > 0:
				#	May change to upsert


				speed = openlr_avgspeed_dict[openlr]
				'''
				avgSpdKmph
				traSeconds
				relSpeed
				condition
				lastUpdate
				'''
				findResults[0]['attributes']['avgSpdKmph'] = speed['averageSpeedKmph']
				findResults[0]['attributes']['traSeconds'] = speed['travelTimeSeconds']
				findResults[0]['attributes']['relSpeed'] = speed['relativeSpeed']
				findResults[0]['attributes']['condition'] = speed['trafficCondition']
				findResults[0]['attributes']['lastUpdate'] = req_ts_readable

				#print(findResults[0])

				featuresToBeUpdated.append(findResults[0])

				status = lyr.edit_features(updates=featuresToBeUpdated)
				#print('Status: ',	status)
			else:
			# 	# Add a new record

			# 	w = shapefile.Writer(expanduser('~/Desktop/newroad.shp'))

			# 	w.field('OpenLR', 'C')
			# 	w.field('Oneway', 'L')
			# 	w.field('Speed', 'N')
			# 	w.field('SpeedClass', 'N')
			# 	w.field('LastUpdate', 'C')


			# 	# lyr.append(item_id='', source_table_name='', upload_format='shapefile')

			# 	# downingtown_fgdb_item = gis.content.add(item_properties=downingtown_props,
			# 	# 					data=downingtown_zip,
			# 	# 					folder="Downingtown")
			# 	# downingtown_item = downingtown_fgdb_item.publish()
				pass


		with ThreadPoolExecutor(max_workers=40) as executor:
			for trafficflow in my_trafficFlowGroup.trafficFlow:
				executor.submit(payload, trafficflow)


		#TODO: Update all keys not in -1
		print(allOpenLR.difference(set(openlr_avgspeed_dict.keys())))

if __name__ == '__main__':
	create()
	nullifyAll()
	#update()
