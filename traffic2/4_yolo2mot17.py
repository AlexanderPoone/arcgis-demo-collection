'''
YOLO to MOT17

•	YOLO format
o	Space-separated
o	Relative image coordinates
<class> <x> <y> <width> <height>
4 0.298566 0.795066 0.043243 0.030067
6 0.248597 0.698886 0.045933 0.057742
7 0.348536 0.717507 0.034402 0.025967
7 0.377513 0.773159 0.042203 0.034912
7 0.463967 0.764091 0.042669 0.026185
7 0.580191 0.800187 0.036312 0.024561
4 0.759125 0.804318 0.035254 0.036882
1 0.721695 0.82134 0.034674 0.033787
6 0.498835 0.726219 0.052083 0.038245
1 0.432211 0.791703 0.044008 0.033735
1 0.506612 0.802779 0.035017 0.027193
7 0.775131 0.630798 0.026396 0.021395
7 0.801932 0.627922 0.023968 0.019238
3 0.14862 0.166018 0.258094 0.330856

•	MOT17 format
o	MOT17/train/MOT17-02-DPM/gt\
o	Comma-separated
o	Absolute image coordinates

<frame number>,	<identity number>,	<bb_left>,	<bb_top>,	<bb_width>,	<bb_height>,	<confidence score>,	<class>,	<visibility>
1,				1,					912,		484,		97,			109,			0,					7,			1
'''

from glob import glob
from json import loads, dumps
from os import mkdir, remove
from os.path import basename, exists
from shutil import copy2, copytree, rmtree
from subprocess import check_output
from pprint import pprint

from natsort import natsorted

if __name__ == '__main__':
	# Stills needs to read labelme for objectId

	for g in glob('_internal/CUH-Dataset/JPEGImages/*/'):

		# Read json files
		for h in natsorted(glob(f'{g}/YOLODataset/labels/*/*.txt')):
			if 'labels.txt' in h:
				continue

			with open(h, 'r') as i:
				x = [[float(k)for k in j.strip().split(' ')] for j in i.readlines()]

			pprint(h)
			#pprint(x)

			pprint([[int(l[0]), l[1]*width, l[2]*height, l[3]*width, l[4]*height] for l in x])

