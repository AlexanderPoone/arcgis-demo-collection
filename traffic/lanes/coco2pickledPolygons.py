'''
under construction

dictOfLanes.npz format:
```
{'camid': {'<starts from 1>': {'polygon': <binary mask>, 'description': '<lane description>'}}}
```

| Camera code     | Traffic lane | Mapping       |
|-----------------|--------------|---------------|
| H106F | 1 | Connaught Rd Central near Exchange Square |
| H109F | 1 | Garden Road Flyover towards Cotton Tree Drive |
| H109F | 2 | Queensway heading towards Queen's Road Central |
| H207F | 1 | Cross Harbour Tunnel Hong Kong Side |
| H210F | 1 | Aberdeen Tunnel - Wan Chai Side (entering, southwards) |
| H210F | 2 | Aberdeen Tunnel - Wan Chai Side (exiting, northwards) |
| H210F | 3 | Wong Nai Chung Road / Queen's Road East |
| H801F | 1 | Island Eastern Corridor near Ka Wah Center towards Central / Causeway Bay (westwards) |
| H801F | 2 | Island Eastern Corridor near Ka Wah Center towards Eastern Harbour Crossing (eastwards) |
| H801F | 3 | Island Eastern Corridor near Ka Wah Center towards Shau Kei Wan / Chai Wan (eastwards) |
| K107F | 1 | Cross Harbour Tunnel Kownloon Side (exiting, northwards) |
| K107F | 2 | Cross Harbour Tunnel Kownloon Side (entering, southwards) |
| K109F | 1 | Chatham Road S near Prince Margaret Road (eastwards) |
| K109F | 2 | Chatham Road S near Prince Margaret Road towards West Kowloon Corridor (westwards) |
| K409F | 1 | Princess Margaret Road near Argyle Street |
| K409F | 2 | Argyle Street Flyover near Princess Margaret Road (eastwards) |
| K409F | 3 | Argyle Street Flyover near Princess Margaret Road (westwards) |
| K502F | 1 | Waterloo Road Flyover (southwards) |
| K502F | 2 | Waterloo Road Flyover towards Lion Rock Tunnel (northwards) |
| K502F | 3 | Waterloo Road towards Cornwall Street (northwards) |
| K502F | 4 | Waterloo Road (northwards) |
| K614F | 1 | Clear Water Bay Road (eastwards) |
| K614F | 2 | Clear Water Bay Road towards Lung Cheung Road (westwards) |

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

ROOT_DIR = os.path.abspath(os.path.dirname(os.path.realpath(__file__)) + r"\Mask_RCNN-tensorflowone_sewer")

sys.path.append(os.path.join(ROOT_DIR, "samples/coco/")) 		# To find local version

import coco

C=coco.COCO(r'lanes\annotations\instances_train2017.json')		# https://stackoverflow.com/a/69175547

C.annToMask(C.loadAnns(1)[0])

np.savez('dictOfLanes', dictOfLanes)