'''
under construction
'''

from glob import glob
from json import dumps, loads

glob('build/SegmentationClassPNG/*')
with open('meta.json', 'w', encoding='utf-8') as f:
	f.write(loads())