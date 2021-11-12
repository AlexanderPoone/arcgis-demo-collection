'''
under construction

dictOfLanes.npz format:
```
{'camid': {'<starts from 1>': {'polygon': <binary mask>, 'description': '<lane description>'}}}
```

TR119F Tuen Mun Road - Sam Shing Hui
TR116F Tuen Mun Road - Siu Lam Section
TR107F Tuen Mun Road - Sham Tseng Section
TR103F Tuen Mun Road - Yau Kom Tau Section
TR101F Tuen Mun Road - Chai Wan Kok
TW103F Tsuen Wan Road near Tsuen Tsing Intchg
TW105F Kwai Tsing Road near Tsing Yi Bridge
TW102F Kwai Chung Road near Container Terminal
TW117F Castle Peak Road near Texaco Road North
TW120F Tsuen Wan Road near Tai Chung Road
'''

import sys
import numpy as np
import os
import os.path

dictOfLanes = {
'H106F': {'1': {'description': "Connaught Rd Central near Exchange Square"}},
'H109F': {'1': {'description': "Garden Road Flyover towards Cotton Tree Drive"}, '2': {'description': "Queensway heading towards Queen's Road Central"}},
'H207F': {'1': {'description': "Cross Harbour Tunnel Hong Kong Side"}},
'H210F': {'1': {'description': "Aberdeen Tunnel - Wan Chai Side (entering, southwards)"}, '2': {'description': "Aberdeen Tunnel - Wan Chai Side (exiting, northwards)"}, '3': {'description': "Wong Nai Chung Road / Queen's Road East"}},
'H801F': {'1': {'description': "Island Eastern Corridor near Ka Wah Center towards Central / Causeway Bay (westwards)"}, '2': {'description': "Island Eastern Corridor near Ka Wah Center towards Eastern Harbour Crossing (eastwards)"}, '3': {'description': "Island Eastern Corridor near Ka Wah Center towards Shau Kei Wan / Chai Wan (eastwards)"}},
'K107F': {'1': {'description': "Cross Harbour Tunnel Kownloon Side (exiting, northwards)"}, '2': {'description': "Cross Harbour Tunnel Kownloon Side (entering, southwards)"}},
'K109F': {'1': {'description': "Chatham Road S near Prince Margaret Road (eastwards)"}, '2': {'description': "Chatham Road S near Prince Margaret Road towards West Kowloon Corridor (westwards)"}},
'K409F': {'1': {'description': "Princess Margaret Road near Argyle Street towards Kowloon Tong (northwards)"}, '2': {'description': "Princess Margaret Road near Argyle Street towards Hong Hom (southwards)"}, '3': {'description': "Argyle Street Flyover near Princess Margaret Road (eastwards)"}},
'K502F': {'1': {'description': "Waterloo Road Flyover (southwards)"}, '2': {'description': "Waterloo Road Flyover towards Lion Rock Tunnel (northwards)"}, '3': {'description': "Waterloo Road towards Cornwall Street (northwards)"}, '4': {'description': "Waterloo Road (northwards)"}},
'K614F': {'1': {'description': "Clear Water Bay Road (eastwards)"}, '2': {'description': "Clear Water Bay Road towards Lung Cheung Road (westwards)"}}
}

ROOT_DIR = os.path.abspath(os.path.expanduser("~/Desktop/Mask_RCNN-tensorflowone_sewer"))
sys.path.append(ROOT_DIR)
sys.path.append(os.path.join(ROOT_DIR, "samples/coco/")) 		# To find local version

import coco

C=coco.COCO(r'annotations\instances_train2017.json')		# https://stackoverflow.com/a/69175547

import matplotlib
gui_env = ['TKAgg','GTKAgg','Qt4Agg','WXAgg']
for gui in gui_env:
    try:
        matplotlib.use(gui,warn=False, force=True)
        from matplotlib import pyplot as plt
        break
    except:
        continue

for k in C.imgs:
	camid = os.path.basename(C.imgs[k]['file_name']).split('.')[0]
	print(k,camid)
	'''
	print(dir(C))
	print(C.imgs)
	print(C.info)
	'''
	cnt = 1
	for ann in C.getAnnIds(k):
		# Syntax: C.loadAnns(imageId)[catId]
		polygon = C.annToMask(C.loadAnns(ann)[0]).astype(bool)
		#plt.imshow(polygon)
		#plt.show()
		try:
			dictOfLanes[camid][f'{cnt}']['polygon'] = polygon
		except:
			pass
		cnt += 1
	
	print(dictOfLanes)

np.savez('dictOfLanes', dictOfLanes)