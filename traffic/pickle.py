import sys
import numpy as np

ROOT_DIR = os.path.abspath(os.path.dirname(os.path.realpath(__file__)) + r"\Mask_RCNN-tensorflowone_sewer")

sys.path.append(os.path.join(ROOT_DIR, "samples/coco/"))  # To find local version

import coco

C=coco.COCO(r'lanes\annotations\instances_train2017.json')  # https://stackoverflow.com/a/69175547

C.annToMask(C.loadAnns(1)[0])

np.savez('dictOfLanes', dictOfLanes)