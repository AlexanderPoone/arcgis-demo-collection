'''
under construction
'''

from glob import glob
from json import dumps, loads
from os.path import basename

if __name__ == '__main__':

	obj = {'video': {}}

	for g in glob('_internal/CUH-Dataset/JPEGImages/*'):
		# Get info from 2_

		obj['video'][basename(g)] = {"objects": {}}
		{
	        "category": "penguin", 
	        "frames": []
        }

	jsn=dumps(obj, indent=4)
	print(jsn)

	with open('_internal/CUH-Dataset/meta.json', 'w', encoding='utf-8') as f:
		f.write(jsn)