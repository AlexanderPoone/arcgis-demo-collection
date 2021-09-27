#######################################
#
#	Generate sample data (.txt) for the GeoEvent Simulator desktop app
#
#	SensorsDashboard
#	https://demo2.hkgisportal.com/sensors/
#
#   Author:        Alex Poon (Esri China (H.K.))
#   Date:          Jun 29, 2021
#   Last update:   Jun 29, 2021
#
#######################################


from datetime import datetime
from random import choice,randint,uniform,sample

'''
from urllib.request import urlopen as u
'''

with open('testdata.csv','w') as f1:

	f1.write('Type,DeviceBuildingID,DeviceFloor,DeviceFlat,ReportTime,RawDeviceReading,Issues\n')

	heatsamp = {}
	othersamp = {}
	leadsamp = {}
	for bld in ('3739819140T20200513', '3740419095T20200513'):
		for flo in [x for x in range(5,37) if x not in (14,24,34)]:
			for fla in [chr(x) for x in range(65,75) if x != 73]:
				heatsamp[f'{bld}{flo}{fla}'] = uniform(27-5,32)
				othersamp[f'{bld}{flo}{fla}'] = uniform(-0.07-.5,0.08)
				leadsamp[f'{bld}{flo}{fla}'] = uniform(-0.9-.5,-0.35)

	for arr in range(41):
		for bld in ('3739819140T20200513', '3740419095T20200513'):
			for flo in [x for x in range(5,37) if x not in (14,24,34)]:
				for fla in [chr(x) for x in range(65,75) if x != 73]:

					for SENSORTYPE in ((
						# ('lead', ('Water Lead Level Exceeded',), (0.1,0.508), 0.5), #'Lead Flat Testing', 
						('leaks', ('Aircon Leaking',), (0,1.1), 1), #'Leak Under', 
						# ('pests', ('Mosquitoes',), (0,1.1), 1), #, 'Needs Painting'
						('aircon', ('',), (0,1.1), 1), #, 'Needs Painting'
						('heat', ('Exterior Overheated',), (20,35), 35), #, 'Convector Cover OOO'
						('mildew', ('Mould',), (0,1.1), 1), #'Mice', 
						('lift', ('User Trapped in Lift', 'Lift Out of Order'), (0,1.2), 0.9),
					)):

						# bldg = choice((('3739819140T20200513',1),('3739819140T20200513',2),('3740419095T20200513',3),('3740419095T20200513',4)))

						if SENSORTYPE[0] == 'lift':
							if flo!=5:
								continue
							floor = ''
							if bld == '3739819140T20200513':
								n = choice((1,2))
							elif bld == '3740419095T20200513':
								n = choice((3,4))
							flat = f'LIFT SHAFT {n}'
							reading=int(uniform(*SENSORTYPE[2]))
						elif SENSORTYPE[0] == 'aircon':
							flat = choice(('Clubhouse Air Vent','Children Play Air Con #1','Children Play Air Con #2','Lobby Corridor','Children Play Air Con #3'))
						else:
							floor = f'{flo}F'
							flat = f'Flat {fla}'  #f'Flat {choice([chr(x) for x in range(65,75) if x != 73])}'
							reading=uniform(*SENSORTYPE[2])
						x = arr/4
						if SENSORTYPE[0] in ('heat'):
							reading = 0.00147739* x**4 - 0.0354574* x**3 + 0.155158* x**2 + 0.691041* x + heatsamp[f'{bld}{flo}{fla}'] + uniform(0,0.1)
						elif SENSORTYPE[0] in ('aircon'):
							reading = 0.00147739* x**4 - 0.0354574* x**3 + 0.155158* x**2 + 0.691041* x + heatsamp[f'{bld}{flo}{fla}'] -9+ uniform(0,0.1)
							reading=max(18.5,reading)
						elif SENSORTYPE[0] == 'lift':
							reading=int(uniform(*SENSORTYPE[2]))
						elif SENSORTYPE[0] == 'lead':
							reading = 0.000284963 *x**4 - 0.00683912 *x**3 + 0.0238181 *x**2 + 0.206599 *x + leadsamp[f'{bld}{flo}{fla}'] + uniform(0,0.05)
						else:
							reading = 0.000284963 *x**4 - 0.00683912 *x**3 + 0.0238181 *x**2 + 0.206599 *x + othersamp[f'{bld}{flo}{fla}'] + uniform(0,0.05)
						reading = max(0.0001,reading)

						content = f'{SENSORTYPE[0]},{"" if SENSORTYPE[0] == "aircon" else bld},{"" if SENSORTYPE[0] == "aircon" else floor},{flat},{datetime.utcnow().isoformat()},{round(reading,5)},{choice(SENSORTYPE[1]) if reading > SENSORTYPE[3] else ""}\n'

						f1.write(content)
