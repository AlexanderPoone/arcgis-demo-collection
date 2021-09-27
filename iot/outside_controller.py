#######################################
#
#	For external access (without Remote Desktop)
#
#	SensorsDashboard
#	https://demo2.hkgisportal.com/sensors2/
#
#   Author:        Alex Poon (Esri China (H.K.))
#   Date:          Jun 29, 2021
#   Last update:   Jun 29, 2021
#
#######################################

from datetime import datetime
from json import dumps
from random import choice
from time import sleep
from urllib import request, parse
from urllib.request import urlopen as u

randomrooms = [('3739819140T20200513', 'BF', 'LIFT MACHINE ROOM (CAR LIFT)'),
('3739819140T20200513', 'BF', 'F.S. & SPRINKER WATER PUMP AND TANK ROOM (PODIUM)'),
('3739819140T20200513', 'BF', 'MAIN SWITCH ROOM (PODIUM)'),
('3739819140T20200513', 'BF', 'F.S. & SPRINKLER WATER PUMP AND TANK ROOM (TOWER 1&2)'),
('3739819140T20200513', 'BF', 'FRESH & FLUSH WATER PUMP ROOM (TOWER)'),
('3739819140T20200513', 'BF', 'FRESH & FLUSH WATER PUMP ROOM (PODIUM)'),
('3739819140T20200513', 'BF', 'LIFT T SHAFT 4'),
('3739819140T20200513', 'BF', 'LIFT T SHAFT 8'),
('3739819140T20200513', 'BF', 'WATER TANK (PODIUM NORTH)'),
('3739819140T20200513', 'BF', 'WATER TANK (PODIUM SOUTH)'),
('3739819140T20200513', '1F', 'PAU ROOM (TOWER 1 G/F, 1/F & 2/F)'),
('3739819140T20200513', '1F', 'CHILLER PLANT AREA'),
('3739819140T20200513', '1F', 'WATER PUMP ROOM'),
('3739819140T20200513', '1F', 'PAU ROOM (TOWER 2 G/F & 1/F)'),
('3739819140T20200513', '1F', 'LIFT SHAFT 7'),
('3739819140T20200513', '2F', 'LIFT PIT 3'),
('3739819140T20200513', '2F', 'MAIN SWITCH ROOM (2/F)'),
('3739819140T20200513', '2F', 'FUEL TANK RM.'),
('3739819140T20200513', '2F', 'LIFT PIT 1'),
('3739819140T20200513', '2F', 'GENSET ROOM'),
('3739819140T20200513', '2F', 'LIFT SHAFT 6'),
('3739819140T20200513', '3F', 'MAIN SWITCH ROOM (3/F)'),
('3740419095T20200513', 'TR', 'WATER TANK (ROOF TOWER 2 NORTH)'),
('3740419095T20200513', 'TR', 'LIFT MACHINE ROOM (TOWER 2)'),
('3739819140T20200513', 'TR', 'WATER TANK (ROOF TOWER 1)'),
('3739819140T20200513', 'TR', 'LIFT MACHINE ROOM (TOWER 1)'),
('3740419095T20200513', 'TR', 'WATER TANK (ROOF TOWER 2 SOUTH)'),
('3740419095T20200513', 'RF', 'POTABLE & FLUSHING WATER PUMP ROOM (TOWER 2)'),
('3739819140T20200513', 'RF', 'POTABLE & FLUSHING WATER PUMP ROOM (TOWER 1)')]

url = 'https://demo2.hkgisportal.com/iot_outside_access'

while True:
	tmp = choice(randomrooms)
	onOff = choice([0,1])
	payload = f'engineering,{tmp[0]},{tmp[1]},{tmp[2]},{datetime.utcnow().isoformat()},{onOff},'

	req =  request.Request(url, data=bytes(dumps({'payload': payload}), encoding='utf-8'))
	req.add_header('Content-Type', 'application/json')
	resp = u(req)
	print(resp.read())
	sleep(1)