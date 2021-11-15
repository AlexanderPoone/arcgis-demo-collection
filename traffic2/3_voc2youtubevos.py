'''
VOC2012 to YouTube_VOS
'''

from glob import glob
from json import dumps, loads
from os.path import basename
from natsort import natsorted

if __name__ == '__main__':

	obj = {'videos': {}}

	for g in glob('_internal/CUH-Dataset/JPEGImages/*/'):
		od = {}

		# Read json files
		for h in natsorted(glob(f'{g}/*.json')):
			print(h)
			with open(h, 'r') as h2:
				h3 = loads(h2.read())
			for shape in h3['shapes']:
				if shape['label'] in od:
					od[shape['label']]['frames'].append(basename(h).split('.')[0])
				else:
					od[shape['label']] = {'category': shape['label'].split('_')[0], 'frames': [basename(h).split('.')[0]]}


		obj['videos'][basename(g[:-1])] = {"objects": od}


	jsn=dumps(obj, indent=4)
	print(jsn)

	with open('_internal/CUH-Dataset/meta.json', 'w', encoding='utf-8') as f:
		f.write(jsn)