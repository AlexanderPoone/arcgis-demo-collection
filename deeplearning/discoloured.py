##################################################
#
#   Discoloured Road Marks Test Program
#   Last updated: 2021-02-28
#
##################################################

# Debug mode: Stop automatic slideshow. The window has to be closed manually.
DEBUG_MODE = True

from gc import collect
from glob import glob
from json import dumps

from PIL import Image
from imgaug import augmenters as iaa

#---------------------------------

# import arcpy
import asyncio

import pandas

from imantics import Mask
from shapely.geometry import Polygon
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
from natsort import natsorted
import numpy as np
import matplotlib.pyplot as plt
# from scipy.stats import linregress
from scipy.optimize import curve_fit
from scipy.spatial.distance import euclidean
from skimage import img_as_ubyte
from skimage.feature import shape_index
from skimage.filters import threshold_otsu, rank
from skimage.measure import label, regionprops, regionprops_table
from skimage.morphology import disk, binary_erosion, binary_dilation, convex_hull_image, remove_small_holes, remove_small_objects
from skimage.transform import ProjectiveTransform, warp, warp_coords, resize
from skimage.segmentation import *
from sklearn.cluster import MeanShift
from os import chdir, remove, rename, mkdir
from shutil import copy2, rmtree
from os.path import basename, expanduser, exists
# from skimage.restoration import (denoise_tv_chambolle, denoise_bilateral,
#                                  denoise_wavelet, estimate_sigma)
from colorsys import rgb_to_hsv

from sklearn.model_selection import StratifiedShuffleSplit

#----------------------------------

from subprocess import Popen
import cv2
from skimage.restoration import inpaint

#----------------------------------

import os
import sys

from base64 import b64encode

import os
import json
import collections
from labelme import utils

'''
TODO: MaskRCNN double line, line+line
'''

IGNORE_THRESHOLD = 90
RCNN_THRESHOLD = 10
Y_IGNORE_THRESH = 80 #100

PYTHONPATH = '"C:/Program Files/ArcGIS/Pro/bin/Python/envs/pytorch-CycleGAN-and-pix2pix/python.exe"'

prevImage = None

'''
This function generate chips for training.
Sample data structure:

a
├───arrow
├───autotoll
├───chevron
├───chieng
├───grid
├───line
├───oxford
├───oxford_engnum
├───speed_limit
├───triangle
├───zebra_yellow
├───zzz_nothing
└───zzz_validation

b
├───arrow
├───autotoll
├───chevron
├───chieng
├───grid
├───line
├───oxford
├───oxford_engnum
├───speed_limit
├───triangle
└───zebra_crossing

c (for MaskRCNN models that classify numbers and alphabets)
├───x.jpg (generated)
└───x.json (generated)
'''
def prepare_chips():
    a = glob(expanduser(r'~\Desktop\discoloured\a\*\*.jpg'))
    b = glob(expanduser(r'~\Desktop\discoloured\b\*\*.jpg'))

    for i in range(len(a)):
        for _ in range(2):
            print(i, _)

            blank = Image.new('RGB',(512,256))
            aimg = Image.open(a[i])
            aimg = aimg.resize((256,256))
            # aimg.save(expanduser(fr'~/Desktop/discoloured/d/{i}.jpg'))

            try:
                bimg = Image.open(b[i])
                bimg = bimg.resize((256,256))
            except:
                bimg = Image.new('RGB',(256,256))

            if '_validation' in a[i]:
                outfolder = 'test'
            else:
                outfolder = 'train'


            if _ == 1:
                if exists(expanduser(fr'~/Desktop/pytorch-CycleGAN-and-pix2pix/datasets/roadmarks/{outfolder}/{i}_{_}.jpg')):
                    remove(expanduser(fr'~/Desktop/pytorch-CycleGAN-and-pix2pix/datasets/roadmarks/{outfolder}/{i}_{_}.jpg'))
                    remove(expanduser(fr'~/Desktop/pytorch-CycleGAN-and-pix2pix/datasets/roadmarks/{outfolder}/{i}_rot_{_}.jpg'))
                    remove(expanduser(fr'~/Desktop/pytorch-CycleGAN-and-pix2pix/datasets/roadmarks/{outfolder}/{i}_rot2_{_}.jpg'))
                    remove(expanduser(fr'~/Desktop/pytorch-CycleGAN-and-pix2pix/datasets/roadmarks/{outfolder}/{i}_moblur_{_}.jpg'))
                    remove(expanduser(fr'~/Desktop/pytorch-CycleGAN-and-pix2pix/datasets/roadmarks/{outfolder}/{i}_brightness_{_}.jpg'))
                    remove(expanduser(fr'~/Desktop/pytorch-CycleGAN-and-pix2pix/datasets/roadmarks/{outfolder}/{i}_saturation_{_}.jpg'))
                    remove(expanduser(fr'~/Desktop/pytorch-CycleGAN-and-pix2pix/datasets/roadmarks/{outfolder}/{i}_saturation2_{_}.jpg'))
                    remove(expanduser(fr'~/Desktop/pytorch-CycleGAN-and-pix2pix/datasets/roadmarks/{outfolder}/{i}_xtreme_{_}.jpg'))
                    remove(expanduser(fr'~/Desktop/pytorch-CycleGAN-and-pix2pix/datasets/roadmarks/{outfolder}/{i}_zoomed_{_}.jpg'))
                    remove(expanduser(fr'~/Desktop/pytorch-CycleGAN-and-pix2pix/datasets/roadmarks/{outfolder}/{i}_zoomedout_{_}.jpg'))

                if 'chieng' not in a[i] and 'speed_limit' not in a[i] and '_validation' not in a[i] and 'oxford_engnum' not in a[i]:
                    aimg = aimg.transpose(Image.FLIP_LEFT_RIGHT)
                    bimg = bimg.transpose(Image.FLIP_LEFT_RIGHT)
                else:
                    continue
            elif '_validation' not in a[i] and '_nothing' not in a[i]:
                bimg.save(expanduser(fr'~/Desktop/discoloured/c/{basename(a[i])[:-4]}.jpg'))

                if 'speed_limit' not in a[i] and 'chieng' not in a[i] and 'oxford_engnum' not in a[i]:
                    # create negative example
                    with open(expanduser(fr'~/Desktop/discoloured/c/{basename(a[i])[:-4]}.jpg'), 'rb') as bnwJpeg:
                        toJson = {
                            "version": "4.5.6",
                            "flags": {},
                            "shapes": [],
                            "imagePath": f"{basename(a[i])[:-4]}.jpg",
                            "imageData": b64encode(bnwJpeg.read()).decode('utf-8'),
                            "imageHeight": 256,
                            "imageWidth": 256
                        }
                    with open(expanduser(fr'~/Desktop/discoloured/c/{basename(a[i])[:-4]}.json'), 'w', encoding='utf-8') as falseExampleFile:
                        falseExampleFile.write(dumps(toJson))

            randaug = iaa.Affine(rotate=(-5, 5))._to_deterministic()
            images_rot = randaug.augment_image(np.array(aimg.convert('RGB')))
            images_rot1 = randaug.augment_image(np.array(bimg.convert('RGB')))

            randaug = iaa.Affine(rotate=(-5, 5))._to_deterministic()
            images_rot2 = randaug.augment_image(np.array(aimg.convert('RGB')))
            images_rot3 = randaug.augment_image(np.array(bimg.convert('RGB')))

            randaug = iaa.MotionBlur(k=(3,4), angle=(-10, 10))._to_deterministic()
            images_moblur = randaug.augment_image(np.array(aimg.convert('RGB')))

            randaug = iaa.AddToBrightness((-15, 10))._to_deterministic()
            images_brightness = randaug.augment_image(np.array(aimg.convert('RGB')))

            randaug = iaa.AddToSaturation((-30, 30))._to_deterministic()
            images_saturation = randaug.augment_image(np.array(aimg.convert('RGB')))

            randaug = iaa.Affine(scale=1.2)._to_deterministic()
            images_zoomed = randaug.augment_image(np.array(aimg.convert('RGB')))
            images_zoomed1 = randaug.augment_image(np.array(bimg.convert('RGB')))

            randaug = iaa.Affine(scale=0.95)._to_deterministic()
            images_zoomed2 = randaug.augment_image(np.array(aimg.convert('RGB')))
            images_zoomed3 = randaug.augment_image(np.array(bimg.convert('RGB')))

            randaug = iaa.Sequential([
                iaa.AddToSaturation((-30, 30)),
                iaa.MotionBlur(k=(3,4), angle=(-10, 10))
            ])._to_deterministic()
            images_saturation2 = randaug.augment_image(np.array(aimg.convert('RGB')))

            randaug = iaa.Sequential([
                iaa.AddToBrightness((-10, 10)),
                iaa.AddToSaturation((-30, 30)),
                iaa.MotionBlur(k=(3,4), angle=(-10, 10))
            ])._to_deterministic()
            randaug2 = iaa.Affine(rotate=(-6.6, -5.5))._to_deterministic()
            images_rot98 = randaug2.augment_image(np.array(aimg.convert('RGB')))
            images_rot98 = randaug.augment_image(images_rot98)
            images_rot99 = randaug2.augment_image(np.array(bimg.convert('RGB')))

            # if basename(a[i]).startswith('yyy'):
            #     randaug = iaa.Fliplr()._to_deterministic()
            #     images_lr = randaug.augment_image(np.array(aimg.convert('RGB')))

            aug = Image.fromarray(images_rot, 'RGB')
            # aug.save(expanduser(fr'~/Desktop/discoloured/rot/{i}.jpg'))

            aug1 = Image.fromarray(images_rot1, 'RGB')
            # aug1.save(expanduser(fr'~/Desktop/discoloured/rot1/{i}.jpg'))

            aug2 = Image.fromarray(images_rot2, 'RGB')
            aug3 = Image.fromarray(images_rot3, 'RGB')

            aug4 = Image.fromarray(images_moblur, 'RGB')
            # aug4.save(expanduser(fr'~/Desktop/discoloured/moblur/{i}.jpg'))

            aug5 = Image.fromarray(images_brightness, 'RGB')

            aug6 = Image.fromarray(images_saturation, 'RGB')

            aug7 = Image.fromarray(images_saturation2, 'RGB')

            aug8 = Image.fromarray(images_rot98, 'RGB')
            aug9 = Image.fromarray(images_rot99, 'RGB')

            aug10 = Image.fromarray(images_zoomed, 'RGB')
            aug11 = Image.fromarray(images_zoomed1, 'RGB')

            aug12 = Image.fromarray(images_zoomed2, 'RGB')
            aug13 = Image.fromarray(images_zoomed3, 'RGB')

            # if basename(a[i]).startswith('yyy'):
            #     aug14 = Image.fromarray(images_lr, 'RGB')
            # # aug4.save(expanduser(fr'~/Desktop/discoloured/brightness/{i}.jpg'))

            blank.paste(aimg, box=(0,0))
            blank.paste(bimg, box=(256,0))
            blank.save(expanduser(fr'~/Desktop/pytorch-CycleGAN-and-pix2pix/datasets/roadmarks/{outfolder}/{i}_{_}.jpg'))

            blank.paste(aug, box=(0,0))
            blank.paste(aug1, box=(256,0))
            blank.save(expanduser(fr'~/Desktop/pytorch-CycleGAN-and-pix2pix/datasets/roadmarks/{outfolder}/{i}_rot_{_}.jpg'))

            blank.paste(aug2, box=(0,0))
            blank.paste(aug3, box=(256,0))
            blank.save(expanduser(fr'~/Desktop/pytorch-CycleGAN-and-pix2pix/datasets/roadmarks/{outfolder}/{i}_rot2_{_}.jpg'))

            blank.paste(aug5, box=(0,0))
            blank.paste(bimg, box=(256,0))
            blank.save(expanduser(fr'~/Desktop/pytorch-CycleGAN-and-pix2pix/datasets/roadmarks/{outfolder}/{i}_moblur_{_}.jpg'))

            blank.paste(aug5, box=(0,0))
            blank.paste(bimg, box=(256,0))
            blank.save(expanduser(fr'~/Desktop/pytorch-CycleGAN-and-pix2pix/datasets/roadmarks/{outfolder}/{i}_brightness_{_}.jpg'))

            blank.paste(aug6, box=(0,0))
            blank.paste(bimg, box=(256,0))
            blank.save(expanduser(fr'~/Desktop/pytorch-CycleGAN-and-pix2pix/datasets/roadmarks/{outfolder}/{i}_saturation_{_}.jpg'))

            blank.paste(aug7, box=(0,0))
            blank.paste(bimg, box=(256,0))
            blank.save(expanduser(fr'~/Desktop/pytorch-CycleGAN-and-pix2pix/datasets/roadmarks/{outfolder}/{i}_saturation2_{_}.jpg'))

            blank.paste(aug8, box=(0,0))
            blank.paste(aug9, box=(256,0))
            blank.save(expanduser(fr'~/Desktop/pytorch-CycleGAN-and-pix2pix/datasets/roadmarks/{outfolder}/{i}_xtreme_{_}.jpg'))

            blank.paste(aug10, box=(0,0))
            blank.paste(aug11, box=(256,0))
            blank.save(expanduser(fr'~/Desktop/pytorch-CycleGAN-and-pix2pix/datasets/roadmarks/{outfolder}/{i}_zoomed_{_}.jpg'))

            blank.paste(aug12, box=(0,0))
            blank.paste(aug13, box=(256,0))
            blank.save(expanduser(fr'~/Desktop/pytorch-CycleGAN-and-pix2pix/datasets/roadmarks/{outfolder}/{i}_zoomedout_{_}.jpg'))

            # if basename(a[i]).startswith('yyy'):
            #     blank.paste(aug14, box=(0,0))
            #     blank.paste(bimg, box=(256,0))
            #     blank.save(expanduser(fr'~/Desktop/discoloured/{i}_flip.jpg'))


'''
Preserve the percentage of each class in the 80-20 train-split holdout.
'''
def stratified_shuffle():
    chdir(expanduser(r'~\Desktop\discoloured'))
    cnt = 0
    ys = []
    for _ in ('arrow', 'autotoll', 'chevron', 'chieng', 'grid', 'line', 'oxford', 'oxford_engnum', 'speed_limit', 'triangle', 'zebra_yellow', 'zzz_nothing'):
        catsize = len(glob(f'a/{_}/*.jpg'))
        print(catsize)
        # if _ in ('arrow', 'autotoll', 'chevron', 'grid', 'line', 'triangle', 'zebra_yellow', 'zzz_nothing'):
        #     multiplier = 20             # multiplier is the total number of samples derived from a single sample after image augmentation
        # else:
        #     multiplier = 10
        tmp = [cnt] * (catsize)# * multiplier)
        ys += tmp
        cnt += 1
        # cnt += catsize

    sss = StratifiedShuffleSplit(n_splits=1, test_size=0.2, random_state=0)
    chdir(expanduser(r'~\Desktop\pytorch-CycleGAN-and-pix2pix\datasets\roadmarks\train'))
    cnt = int(basename(natsorted(glob('*.jpg'))[-1]).split('_')[0])
    X = np.arange(cnt+1)
    ys = np.array(ys)
    # print(len(X))
    # print(len(ys))
    # print(X)
    # print(ys)
    try:
        mkdir('train')
        mkdir('test')
    except:
        pass
    for f in glob('train/*.jpg'):
        remove(f)
    for f in glob('test/*.jpg'):
        remove(f)
    for train_index, test_index in sss.split(X, ys):
        X_train, X_test = X[train_index], X[test_index]
        y_train, y_test = ys[train_index], ys[test_index]
    for e in X_train:
        for f in glob(f'{e}_*.jpg'):
            copy2(f,f'train/{f}')
    for e in X_test:
        for f in glob(f'{e}_*.jpg'):
            copy2(f,f'test/{f}')

    print('##############################')
    print(X_train)
    print(X_test)


'''
Resize annotations (JSON) if needed (to make training faster / feasible on low-memory GPUs)
'''
def resize_annotations():
    from labelme2coco import convert

    src_dir = r'./highways_testset_removepavement'
    dst_dir = r'./33'

    if not os.path.exists(dst_dir):
        os.makedirs(dst_dir)

    exts = dict()
    filesnames = os.listdir(src_dir)
    for filename in filesnames:
        name, ext = filename.rsplit('.',1)
        if ext != 'json':
            if exts.__contains__(ext):
                exts[ext] += 1
            else:
                exts[ext] = 1

    anno = collections.OrderedDict()
    for key in exts.keys():
        for img_file in glob(os.path.join(src_dir, '*.' + key)):
            try:
                file_name = os.path.basename(img_file)
                print(f"Processing {file_name}")
                img = cv2.imread(img_file)
                (h, w, c) = img.shape

                w_new = 1152
                h_new = int(h / w * w_new)
                ratio = w_new / w
                img_resize = cv2.resize(img, (w_new, h_new))
                cv2.imwrite(os.path.join(dst_dir, file_name), img_resize)


                json_file = os.path.join(src_dir, file_name.rsplit('.',1)[0] + '.json')
                save_to = open(os.path.join(dst_dir, file_name.rsplit('.',1)[0] + '.json'), 'w')
                with open(json_file, 'rb') as f:
                    anno = json.load(f)
                    for shape in anno["shapes"]:
                        points = shape["points"]
                        points = (np.array(points) * ratio).astype(int).tolist()
                        shape["points"] = points


                    anno['imageData']=str(utils.img_arr_to_b64(img_resize[..., (2, 1, 0)]), encoding='utf-8')
                    json.dump(anno, save_to, indent=4)
            except:
                pass
    chdir(dst_dir+'/annotations')
    try:
        remove('instances_train2017.json')
        remove('instances_val2017.json')
    except:
        pass
    convert('..','./instances_train2017.json')
    copy2('instances_train2017.json', 'instances_val2017.json')

    print("Done resizing annotations")


'''
Rotate annotations if needed
'''
def rotate_annotations():
    from labelme2coco import convert

    src_dir = r'./discoloured/c'

    for f in glob(src_dir+'/*.jpg'):
        if not exists(f.replace('.jpg','.json')):
            remove(f)

    for l in glob(src_dir + '/*___l.*'):
        remove(l)

    for r in glob(src_dir + '/*___r.*'):
        remove(r)

    for _ in ((-6, r'./discoloured/crotl', '___l'), (6, r'./discoloured/crotr', '___r')):
        angle = _[0]
        dst_dir = _[1]
        suffix = _[2]

        if not os.path.exists(dst_dir):
            os.makedirs(dst_dir)

        exts = dict()
        filesnames = os.listdir(src_dir)
        for filename in filesnames:
            if filename == 'annotations':
                continue
            name, ext = filename.rsplit('.',1)
            if ext != 'json':
                if exts.__contains__(ext):
                    exts[ext] += 1
                else:
                    exts[ext] = 1

        anno = collections.OrderedDict()
        for key in exts.keys():
            for img_file in glob(os.path.join(src_dir, '*.' + key)):
                file_name = os.path.basename(img_file)
                print(f"Processing {file_name}")
                img = cv2.imread(img_file)

                image_center = tuple(np.array(img.shape[1::-1]) / 2)
                rot_mat = cv2.getRotationMatrix2D(image_center, -angle, 1.0)
                img_rotate = cv2.warpAffine(img, rot_mat, img.shape[1::-1], flags=cv2.INTER_LINEAR)

                # (x - 128) * np.cos(0.017) - (y - 128) * np.sin(0.017) + 128
                # (x - 128) * np.sin(0.017) - (x - 128) * np.cos(0.017) + 128

                # w_new = 1152
                # h_new = int(h / w * w_new)
                # ratio = w_new / w
                #img_rotate = #cv2.resize(img, (w_new, h_new))
                cv2.imwrite(os.path.join(dst_dir, file_name).replace('.jpg',suffix+'.jpg'), img_rotate)


                json_file = os.path.join(src_dir, file_name.rsplit('.',1)[0] + '.json')
                with open(os.path.join(dst_dir, file_name.rsplit('.',1)[0] + suffix + '.json'), 'w') as save_to:
                    with open(json_file, 'rb') as f:
                        anno = json.load(f)
                        for shape in anno["shapes"]:
                            points = shape["points"]
                            points = [[np.round((pt[0] - 128) * np.cos(np.deg2rad(angle)) - (pt[1] - 128) * np.sin(np.deg2rad(angle)) + 128, 1), np.round((pt[0] - 128) * np.sin(np.deg2rad(angle)) + (pt[1] - 128) * np.cos(np.deg2rad(angle)) + 128, 1)] for pt in points]
                            #points = (np.array(points) * ratio).astype(int).tolist()
                            shape["points"] = points


                        anno['imageData']=str(utils.img_arr_to_b64(img_rotate[..., (2, 1, 0)]), encoding='utf-8')
                        anno['imagePath']=anno['imagePath'].replace('.jpg',suffix+'.jpg')
                        json.dump(anno, save_to, indent=4)


    for f in glob(r'./discoloured/crotl/*'):
        rename(f, src_dir+'/'+basename(f))
    for f in glob(r'./discoloured/crotr/*'):
        rename(f, src_dir+'/'+basename(f))
    
    rmtree(r'./discoloured/crotl')
    rmtree(r'./discoloured/crotr')

    chdir(src_dir+'/annotations')
    try:
        remove('instances_train2017.json')
        remove('instances_val2017.json')
    except:
        pass
    convert('..','./instances_train2017.json')
    copy2('instances_train2017.json', 'instances_val2017.json')

    print("Done rotating annotations")


def threshold():
    filelist = natsorted(glob(expanduser(r'~/Desktop/validation_continuous/*.jpg')))
    for g in filelist:
        i=Image.open(g)
        i=np.array(i.convert('L'))

        radius = 60 #25
        selem = disk(radius)

        local_otsu = rank.otsu(i, selem)


        #i = slic(i)

        # thresh=threshold_otsu(i[128:,96:156])
        # print('Otsu: ',thresh)
        # # if thresh < 90:
        # #     thresh = 190
        bnw = Image.fromarray(i>local_otsu)
        bnw.save(expanduser(fr'~\Desktop\otsu\{basename(g)}'))
    
    # for g in glob(expanduser(r'~\Desktop\discoloured\d\*')):
    #     i=Image.open(g)
    #     i=np.array(i.convert('L'))

    #     radius = 30 #25
    #     selem = disk(radius)

    #     local_otsu = rank.otsu(i, selem)


    #     #i = slic(i)

    #     # thresh=threshold_otsu(i[128:,96:156])
    #     # print('Otsu: ',thresh)
    #     # # if thresh < 90:
    #     # #     thresh = 190
    #     bnw = Image.fromarray(i>local_otsu)
    #     bnw.save(expanduser(fr'~\Desktop\pytorch-CycleGAN-and-pix2pix\datasets\roadmarks\otsu\{basename(g)}'))
    #     # plt.imshow(i)

    #     # plt.imshow(i>local_otsu,cmap=plt.cm.gray)
    #     # plt.show()

def eval_pix2pix():
    Popen(f'"{PYTHONPATH}" test.py --dataroot ./datasets/roadmarks --name roadmarks_pix2pix --model pix2pix --direction AtoB')


'''
Cubic curve fitting.
'''
def cubic(t,a,b,c,d):
    return a*pow(t,3) + b*pow(t,2) + c*t + d


async def handleBigPics():
    from glob import glob
    import os
    from os import chdir, remove
    from os.path import basename, expanduser
    from subprocess import run
    import sys
    import math
    import random
    from gc import collect
    from shutil import copy2

    import cv2
    import matplotlib.pyplot as plt
    import numpy as np
    from PIL import Image
    import skimage.io

    from colorthief import ColorThief
    from os import remove

    # Open the geodatabase
    # Shall be replaced by arcpy.SearchCursor in the real version

    geoDb = pandas.read_csv(expanduser('~/Desktop/HySQ0962020_20210123_image.csv'))

    print(geoDb)

    # Root directory of the project
    ROOT_DIR = os.path.abspath(os.path.dirname(os.path.realpath(__file__)) + r"\Mask_RCNN-tensorflowone")

    # Import Mask RCNN
    sys.path.append(ROOT_DIR)  # To find local version of the library

    sys.path.append(os.path.join(ROOT_DIR, "samples/coco/"))  # To find local version

    import mrcnn.model as modellib
    import coco
    from mrcnn import visualize
    import matplotlib.pyplot as plt
    import matplotlib

    # Directory to save logs and trained model
    MODEL_DIR = os.path.join(ROOT_DIR, "logs")

    # # Local path to trained weights file
    # COCO_MODEL_PATH = os.path.join(ROOT_DIR, "outliner_flat.h5")

    # class InferenceConfig(coco.CocoConfig):
    #     # Set batch size to 1 since we'll be running inference on
    #     # one image at a time. Batch size = GPU_COUNT * IMAGES_PER_GPU
    #     GPU_COUNT = 1
    #     IMAGES_PER_GPU = 1
    #     NUM_CLASSES = 1 + 12

    # config = InferenceConfig()

    # model = modellib.MaskRCNN(mode="inference", model_dir=MODEL_DIR, config=config)

    # model.load_weights(COCO_MODEL_PATH, by_name=True)

    class_names = ['BG', 'bitumen2','white_dash_ok','white_dash_bad','triangle_ok','word_ok','arrow_ok','concrete','arrow_bad','triangle_bad','zebra_ok','zebra_bad','word_bad']
    allowed_tags = ['bitumen2','white_dash_ok','white_dash_bad','triangle_ok','word_ok','arrow_ok','concrete','arrow_bad','triangle_bad','zebra_ok','zebra_bad','word_bad']

    background_buf = disk(20)
    filelist = natsorted(glob(expanduser(r'~/Desktop/validation_continuous/*.jpg')))
    # filelist.reverse()


    # '''
    # Now we define the second MaskRCNN model.
    # '''
    # COCO_MODEL_PATH_2 = os.path.join(ROOT_DIR, "discolouring_bounds.h5")

    # class InferenceConfig_2(coco.CocoConfig):
    #     GPU_COUNT = 1
    #     IMAGES_PER_GPU = 1
    #     NUM_CLASSES = 1 + 3

    # config_2 = InferenceConfig_2()

    # model_2 = modellib.MaskRCNN(mode="inference", model_dir=MODEL_DIR, config=config_2)

    # model_2.load_weights(COCO_MODEL_PATH_2, by_name=True)

    # class_names_2 = ['BG', 'chi', 'num', 'alpha']
    # allowed_tags_2 = ['chi', 'num', 'alpha']

    matplotlib.use('TkAgg')

    '''
    Buffer object to count every 5 m segment
    Filename, Length to Where Counting Stopped, Reprojected(X) of that point 3857(X, Y) of that point
    '''
    fiveMetreBuffer = np.empty((len(filelist), 3), dtype=object)


    # Show three pics at a time.
    cnt = 0
    for filename in filelist:
        # Local path to trained weights file
        COCO_MODEL_PATH = os.path.join(ROOT_DIR, "outliner_flat.h5")

        class InferenceConfig(coco.CocoConfig):
            # Set batch size to 1 since we'll be running inference on
            # one image at a time. Batch size = GPU_COUNT * IMAGES_PER_GPU
            GPU_COUNT = 1
            IMAGES_PER_GPU = 1
            NUM_CLASSES = 1 + 12
            DETECTION_MIN_CONFIDENCE = 0.45
            DETECTION_NMS_THRESHOLD = 0.3

        config = InferenceConfig()

        model = modellib.MaskRCNN(mode="inference", model_dir=MODEL_DIR, config=config)

        model.load_weights(COCO_MODEL_PATH, by_name=True)





        fig, axs = plt.subplots(9, 1)
        fig.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=0, hspace=0)

        fileInfo = geoDb.loc[geoDb['ImageName'] == basename(filename)]
        fig.suptitle(f'{basename(filename)}\n(Heading: {fileInfo["Kappa"].values[0]}\nPitch: {fileInfo["Phi_1"].values[0]})')


        visualisationHeadings = ('Original', 'Background removed', 'Pix2Pix', 'Pix2Pix eroded', 
            'Classification masks', 'Otsu thresholding', 'Pix2Pix reprojected', 
            'Otsu thresholding reprojected', 'Discolouring')

        for h in range(len(visualisationHeadings)):
            axs[h].annotate(visualisationHeadings[h], xy=(0, 0.5), xytext=(0, 0),
            xycoords=axs[h].yaxis.label, textcoords='offset points',
            size='small', ha='right', va='center')

        image = Image.open(filename)
        image = image.resize((int(image.size[0]/2),int(image.size[1]/2)))
        image = np.array(image)


        results = model.detect([image], verbose=0)

        image2 = np.copy(image)

        r = 0
        for i in results[0]['class_ids']:
            # print(class_names[i])
            if class_names[i] in ('bitumen2', 'concrete'):
                break
            r += 1

        ########################################
        #  Debug
        ########################################

        debug_lab, debug_num = label(results[0]['masks'][:,:,r], connectivity = 2, return_num=True)
        if debug_num > 2:
            # Debug: Remove MaskRCNN exclave
            print('Debug_num: ',debug_num)
            counts = [np.sum(debug_lab == x) for x in range(1, debug_num + 1)]
            print(counts)
            results[0]['masks'][:,:,r][debug_lab != (np.argmax(counts) + 1)] = False



        roadSurface = image2[results[0]['rois'][r][0]+Y_IGNORE_THRESH:results[0]['rois'][r][2],results[0]['rois'][r][1]:results[0]['rois'][r][3]]
        Image.fromarray(roadSurface).save('tmp_outline.png')
        color_thief = ColorThief('tmp_outline.png')

        # get the dominant color
        dominant_color = color_thief.get_color(quality=1)
        buffed_mask = binary_dilation(results[0]['masks'][:,:,r], selem=background_buf)

        # image2[np.invert(buffed_mask)] = (np.min([255,dominant_color[0]+20]), np.min([255,dominant_color[1]+20]), np.min([255,dominant_color[2]+20]))#127
        for row in range(len(image2)):
            # print(np.flip(buffed_mask[row]), np.argwhere(np.flip(buffed_mask[row]) == True))
            y = image2[row][len(buffed_mask[row]) - 30 - np.argmax(np.flip(buffed_mask[row]) == True)]
            # if len(y) == 0:
            #     continue
            # print(len(buffed_mask[row]) - 1 - np.argwhere(np.flip(buffed_mask[row]) == True))
            try:
                image2[row][np.invert(buffed_mask[row])] = [y] * len(image2[row][np.invert(buffed_mask[row])]) #[[0,0,0]] * len(image2[row][np.invert(buffed_mask[row])])
            except:
                pass
        # print('%%%%%%%%%%%%%%%%%%%%%')
        # print(results[0]['rois'][r])
        roadSurface = image2[results[0]['rois'][r][0]+Y_IGNORE_THRESH:results[0]['rois'][r][2],results[0]['rois'][r][1]:results[0]['rois'][r][3]]
        # image2[np.invert(binary_dilation(results[0]['masks'][:,:,r])] = 0

        # print(results[0])
        # cpy = np.copy(image2[results[0]['rois'][:,:,r]])

        # plt.imshow(image2[results[0]['rois'][:,:,r]])
        # mask = np.invert(results[0]['masks'][:,:,r])[results[0]['rois'][r][0]+Y_IGNORE_THRESH:results[0]['rois'][r][2],results[0]['rois'][r][1]:results[0]['rois'][r][3]]
        # roadSurface = inpaint.inpaint_biharmonic(roadSurface, mask,
        #                                   multichannel=True)


        roadSurfacePil = Image.fromarray(roadSurface)
        roadSurfacePilSave = Image.new('RGB', (roadSurfacePil.size[0]*2,roadSurfacePil.size[1]))
        roadSurfacePilSave.paste(roadSurfacePil, (0,0))
        # roadSurfacePilSave = Image.new('RGB', (roadSurfacePil.size[0]*2,roadSurfacePil.size[0]))
        # roadSurfacePilSave.paste(roadSurfacePil, (0,roadSurfacePil.size[0] - roadSurfacePil.size[1]))
        # roadSurfacePilSave.save(expanduser(fr'~/Desktop/validation/tmp/{basename(filename)}.png'))
        for f in glob(expanduser(fr'~\Desktop\pytorch-CycleGAN-and-pix2pix\datasets\bigpic\test\*.png')):
            remove(f)
        roadSurfacePilSave.save(expanduser(fr'~\Desktop\pytorch-CycleGAN-and-pix2pix\datasets\bigpic\test\{basename(filename).replace("jpg","png")}'))

        roadSurfaceGrey = np.array(Image.fromarray(roadSurface).convert('L'))

        radius = 60 #30 #25
        selem2 = disk(radius)

        local_otsu = rank.otsu(roadSurfaceGrey, selem2)


        #i = slic(i)

        # thresh=threshold_otsu(i[128:,96:156])
        # print('Otsu: ',thresh)
        # # if thresh < 90:
        # #     thresh = 190
        roadSurfaceBnw = Image.fromarray(roadSurfaceGrey>local_otsu)

        for n in range(8):
            axs[n].set_xticklabels(())            
            axs[n].set_yticklabels(())            
            axs[n].get_xaxis().set_visible(False)
            axs[n].get_yaxis().set_ticks([])

        axs[8].set_xticklabels(())            
        axs[8].set_yticklabels(())            
        axs[8].get_yaxis().set_ticks([])





        # chull = convex_hull_image(buffed_mask[results[0]['rois'][r][0]+Y_IGNORE_THRESH:results[0]['rois'][r][2],results[0]['rois'][r][1]:results[0]['rois'][r][3]])
        chull = buffed_mask[results[0]['rois'][r][0]+Y_IGNORE_THRESH:results[0]['rois'][r][2],results[0]['rois'][r][1]:results[0]['rois'][r][3]]

        c = -11
        for row in chull[-10:]:
            if np.sum(chull[c]) - np.sum(row) > 300:
                chull[c+1] = chull[c]
            c += 1

        # print('Sum:', np.sum(chull,axis=1))

        mask = Mask(chull)
        # polygons = mask.polygons().points[0]
        polygons = Polygon(mask.polygons().points[0])
        polygons = polygons.simplify(3)
        polygons = np.asarray(polygons.exterior.coords)[:-1]   

        chull_test = binary_erosion(chull, selem=disk(70))
        mask_test = Mask(chull_test)
        # polygons_test = mask_test.polygons().points[0]
        polygons_test = Polygon(mask_test.polygons().points[0])
        polygons_test = polygons_test.simplify(3)
        polygons_test = np.asarray(polygons_test.exterior.coords)[:-1]  
        



        chdir(expanduser(r'~/Desktop/pytorch-CycleGAN-and-pix2pix'))

        pathToPix2PixTest = expanduser(r'~\Desktop\pytorch-CycleGAN-and-pix2pix\test.py')
        pathToPix2PixDataset = expanduser(r'~\Desktop\pytorch-CycleGAN-and-pix2pix\datasets\bigpic')
        
        run(fr'"C:\Program Files\ArcGIS\Pro\bin\Python\envs\pytorch-CycleGAN-and-pix2pix\python.EXE" "{pathToPix2PixTest}" --dataroot "{pathToPix2PixDataset}" --name roadmarks_pix2pix --model pix2pix --direction AtoB --load_size 512 --crop_size 512')
        command_ran = False
        # while not command_ran or not exists(filename.replace('/validation_continuous','/pytorch-CycleGAN-and-pix2pix/results/roadmarks_pix2pix/test_latest/images').replace('.jpg', '_fake_B.png')):
        #     try:
        #         gc.collect()
        #         run(fr'"C:\Program Files\ArcGIS\Pro\bin\Python\envs\pytorch-CycleGAN-and-pix2pix\python.EXE" "{pathToPix2PixTest}" --dataroot "{pathToPix2PixDataset}" --name roadmarks_pix2pix --model pix2pix --direction AtoB --load_size 512 --crop_size 512')
        #         command_ran = True
        #     except:
        #         pass

        result_p2p = Image.open(filename.replace('/validation_continuous','/pytorch-CycleGAN-and-pix2pix/results/roadmarks_pix2pix/test_latest/images').replace('.jpg', '_fake_B.png'))
        result_p2p = np.array(result_p2p.convert('1').resize(roadSurfacePil.size))
        result_p2p[np.invert(chull)] = 0
        result_p2p = remove_small_holes(result_p2p, connectivity = 2, area_threshold=200)
        result_p2p = remove_small_objects(result_p2p, connectivity = 2, min_size=300)

        labelled_p2p, num_labels = label(result_p2p, connectivity = 2, return_num=True)
        # axs[7].set_xlabel('{}, {}'.format((num_labels, 'left' if solidLineOnLeft else 'right' if solidLineOnRight else ''  )))

        dilated_p2p = np.zeros(labelled_p2p.shape, dtype=np.uint8)
        for i in range(1,num_labels+1):
            # print('Debug1: ',np.sum(labelled_p2p==i))
            dilat = binary_erosion(labelled_p2p==i,selem=disk(1))
            # print('Avg color: ', rgb_to_hsv(*np.mean(roadSurface[dilat], axis=0)/255))
            # print('Shape index of segment ' + str(i) + ': ' + shape_index(dilat))
            # print('Debug2: ',np.sum(dilat))
            dilated_p2p[dilat] = i


        axs[0].imshow(image)
        axs[1].imshow(roadSurface)
        axs[2].imshow(labelled_p2p)                     #label
        axs[3].imshow(dilated_p2p)                     #label

        

        # ##################
        # #   PROJECTED
        # ##################
        testArea = np.copy(chull)
        testArea[chull_test] = False

        # # axs[3].imshow(testArea)

        # inside_area = False

        # inliners = []



        # (dilated_p2p != 0)[testArea == 1]

        inLeft = np.copy((dilated_p2p != 0)[:,0:999])

        inLeft[np.invert(testArea[:,0:999])] = False

        # print('Left: ', np.sum(inLeft)/np.sum(testArea[:,0:999]))

        inRight = np.copy((dilated_p2p != 0)[:,1000:])

        inRight[np.invert(testArea[:,1000:])] = False


        # print('Right: ', np.sum(inRight)/np.sum(testArea[:,1000:]))

        solidLineOnLeft = False
        solidLineOnRight = False

        if np.sum(inLeft)/np.sum(testArea[:,0:999]) > 0.1: #0.1:
            solidLineOnLeft = True
        if np.sum(inRight)/np.sum(testArea[:,1000:]) > 0.1: #0.1:
            solidLineOnRight = True

        if solidLineOnLeft or solidLineOnRight:
            # inliners = []
            inlinersLeft = []
            inlinersRight = []


            if solidLineOnLeft:
                num_labels += 1
                inlinersLeft.append(num_labels)
                inLeft2 = inLeft.astype(np.uint8)
                inLeft2[inLeft] = num_labels
                dilated_p2p[:,0:999] = inLeft2

            if solidLineOnRight:
                num_labels += 1
                inlinersRight.append(num_labels)
                inRight2 = inRight.astype(np.uint8)
                inRight2[inRight] = num_labels
                dilated_p2p[:,1000:] = inRight2


            '''
            for lblnum in range(1, num_labels + 1):
                #labelled_p2p
                

                if solidLineOnLeft:
                    cardinality = np.sum(dilated_p2p[:,0:999] == lblnum)
                    # inLeft = (dilated_p2p == lblnum)[:,0:999]
                    # inLeft[np.invert(testArea[:,0:999])] = False
                    cardinality2 = np.sum(inLeft)

                    # #################################################
                    # # EXPERIMENT: MANUAL SPLIT ALONG CYAN DASHED LINE
                    # #################################################
                    # num_labels += 1
                    # dilated_p2p[:,0:999] = num_labels
                    # #################################################
                    # # EXPERIMENT: MANUAL SPLIT ALONG CYAN DASHED LINE
                    # #################################################


                if solidLineOnRight:    # TODO: How about both lines are present ???
                    cardinality = np.sum(dilated_p2p[:,1000:] == lblnum)
                    # inRight = (dilated_p2p == lblnum)[:,1000:]
                    # inRight[np.invert(testArea[:,1000:])] = False
                    cardinality2 = np.sum(inRight)

                    # #################################################
                    # # EXPERIMENT: MANUAL SPLIT ALONG CYAN DASHED LINE
                    # #################################################
                    # num_labels += 1
                    # dilated_p2p[] = num_labels
                    # #################################################
                    # # EXPERIMENT: MANUAL SPLIT ALONG CYAN DASHED LINE
                    # #################################################


                # print(cardinality2/cardinality)
                
                if cardinality2/cardinality > 0.6:
                    inside_area = True
                    inliners.append(lblnum)
            # Test elements against dashed light blue line

            # if solidLineOnLeft and
            # if solidLineOnRight:
            '''

            axs[3].imshow(np.isin(dilated_p2p, np.concatenate((inlinersLeft, inlinersRight)) ))


            # TBD: Linear regression?







        # if inside_area:
        #     if cnt - 1 in fiveMetreBuffer:
        #         # Where is next viewpoint on this photo?
        #         nextViewpoint = reproject(geoDb[cnt+1]['Easting'], geoDb[cnt+1]['Northing'])

        #         # Get nearest neighbour. Get nearest point on line Last photo's coords.
        #         pointOnLine3857, pointOnLinePicX = NN(nextViewpoint, sampledLine)

        #         # 
        #         fiveMetreBuffer[cnt - 1][0] = [pointOnLine3857, pointOnLinePicX]

        #         #Update
        #     else:
        #         geoDb[cnt+1]['Easting'] + displacecmentX, geoDb[cnt+1]['Northing'] + displacementY 

        #     if cnt == len(filelist) - 1:
        #         continue


        #     fiveMetreBuffer[cnt+1] = [2.5, ]




    


        axs[3].plot(polygons[:,0], polygons[:,1], 'r--')
        axs[3].plot(polygons_test[:,0], polygons_test[:,1], 'c--')

        axs[1].text(0, 0, class_names[results[0]['class_ids'][r]], c='w', ha='left', va='top')


        '''
        Classification masks
        '''

        # off verbose in production
        '''
        Now we define the second MaskRCNN model.
        '''
        COCO_MODEL_PATH_2 = os.path.join(ROOT_DIR, "discolouring_bounds.h5")

        class InferenceConfig_2(coco.CocoConfig):
            GPU_COUNT = 1
            IMAGES_PER_GPU = 1
            NUM_CLASSES = 1 + 3

        config_2 = InferenceConfig_2()

        model_2 = modellib.MaskRCNN(mode="inference", model_dir=MODEL_DIR, config=config_2)

        model_2.load_weights(COCO_MODEL_PATH_2, by_name=True)

        class_names_2 = ['BG', 'chi', 'num', 'alpha', 'punct']
        allowed_tags_2 = ['chi', 'num', 'alpha', 'punct']
        sample_generator = Image.fromarray(result_p2p).convert('RGB')
        

        # Save as sample here:
        if not exists(expanduser(fr'~\Desktop\discoloured\c\{basename(filename)[:-4]}.jpg')):
            sample_generator_save = Image.fromarray(result_p2p[:,int(round(result_p2p.shape[1]/2-result_p2p.shape[0]/2)):int(round(result_p2p.shape[1]/2+result_p2p.shape[0]/2))]).convert('RGB')
            sample_generator_save = sample_generator_save.resize((256,256))
            sample_generator_save.save(expanduser(fr'~\Desktop\discoloured\c\{basename(filename)[:-4]}.jpg'))

        results_2 = model_2.detect([np.array(sample_generator)], verbose=0)

        del config_2
        del model_2

        if len(results_2[0]['class_ids']) > 0:
            # masks = np.copy(results_2[0]['masks'][:,:,0])
            masks = np.zeros(results_2[0]['masks'][:,:,0].shape, dtype=np.uint8)
            print(results_2[0]['class_ids'][r])
            for r in range(0,len(results_2[0]['class_ids'])):
                masks[results_2[0]['masks'][:,:,r]] = results_2[0]['class_ids'][r]
                # print(masks.shape, results_2[0]['masks'][:,:,r].shape)
                # masks =  masks | results_2[0]['masks'][:,:,r]
            axs[4].imshow(masks)
            axs[4].legend(handles=[Patch(facecolor=plt.get_cmap('viridis').colors[int(round(1/np.max(masks)*255))], label=allowed_tags_2[0]),
                Patch(facecolor=plt.get_cmap('viridis').colors[min(255,int(round(2/np.max(masks)*255)))], label=allowed_tags_2[1]),
                Patch(facecolor=plt.get_cmap('viridis').colors[min(255,int(round(3/np.max(masks)*255)))], label=allowed_tags_2[2]),
                Patch(facecolor=plt.get_cmap('viridis').colors[min(255,int(round(4/np.max(masks)*255)))], label=allowed_tags_2[3])][:np.max(masks)],
                bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0.)



        axs[2].legend(handles=[Line2D([0], [0], color='b', lw=4, label='Continuous line')],
            bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0.)
        axs[5].imshow(roadSurfaceBnw)

        # axs[1].annotate(class_names[results[0]['class_ids'][r]], xy=(3000, 0.5), xytext=(0, 0),
        # xycoords=axs[1].yaxis.label, textcoords='offset points',
        # size='small', ha='left', va='center')



        # print('@@@@@@@@@')
        # print((roadSurface.shape[1], roadSurface.shape[0] * 2))
        # w = h = 3840
        w = 1902
        h = 1500#1128
        reprojd = Image.new('L', (w, h))
        reprojd.paste(Image.fromarray(dilated_p2p), (0, h - roadSurface.shape[0]))

        reprojd_otsu = Image.new('1', (w, h))
        reprojd_otsu.paste(roadSurfaceBnw, (0, h - roadSurface.shape[0]))
        # reprojd_otsu = Image.new('RGB', (roadSurface.shape[1], roadSurface.shape[0] * 2))
        # reprojd_otsu.paste(roadSurfaceBnw, (0, roadSurface.shape[0]))

        src = np.asarray([[750,h - roadSurface.shape[0]],[w-750,h - roadSurface.shape[0]],[w,h],[0,h]])
        dst2 = np.asarray([[350,0],[w-350,0],[w-350,h],[350,h]])
        # print(src)
        # print(dst2)
        t2 = ProjectiveTransform()
        t2.estimate(src,dst2)

        reprojd_arr = warp(np.array(reprojd.convert('L')), t2.inverse)
        axs[6].imshow(reprojd_arr)#,cmap='gray')

        # regions = regionprops(labelled_p2p)
        # # regions_table = regionprops_table(labelled_p2p, properties=('centroid',
        # #                                          'orientation',
        # #                                          'major_axis_length',
        # #                                          'minor_axis_length'))

        # for props in regions:
        #     # print('Major axis length:', props.major_axis_length)

        #     y0, x0 = props.centroid
        #     orientation = props.orientation
        #     x1 = x0 + math.cos(orientation) * 0.5 * props.minor_axis_length
        #     y1 = y0 - math.sin(orientation) * 0.5 * props.minor_axis_length
        #     x2 = x0 - math.sin(orientation) * 0.5 * props.major_axis_length
        #     y2 = y0 - math.cos(orientation) * 0.5 * props.major_axis_length

        #     axs[2].plot((x0, x1), (y0, y1), '-r', linewidth=2.5)
        #     axs[2].plot((x0, x2), (y0, y2), '-r', linewidth=2.5)
        #     axs[2].plot(x0, y0, '.g', markersize=15)

        #     minr, minc, maxr, maxc = props.bbox
        #     bx = (minc, maxc, maxc, minc, minc)
        #     by = (minr, minr, maxr, maxr, minr)
        #     axs[2].plot(bx, by, '-b', linewidth=2.5)

        '''
        regions = regionprops(img_as_ubyte(reprojd_arr))
        # # regions_table = regionprops_table(labelled_p2p, properties=('centroid',
        # #                                          'orientation',
        # #                                          'major_axis_length',
        # #                                          'minor_axis_length'))

        for props in regions:
            # print('Major axis length:', props.major_axis_length)

            y0, x0 = props.centroid
            # orientation = props.orientation
            # x1 = x0 + math.cos(orientation) * 0.5 * props.minor_axis_length
            # y1 = y0 - math.sin(orientation) * 0.5 * props.minor_axis_length
            # x2 = x0 - math.sin(orientation) * 0.5 * props.major_axis_length
            # y2 = y0 - math.cos(orientation) * 0.5 * props.major_axis_length

            # axs[5].plot((x0, x1), (y0, y1), '-r', linewidth=2.5)
            # axs[5].plot((x0, x2), (y0, y2), '-r', linewidth=2.5)
            axs[5].plot(x0, y0, '.g', markersize=8)

            # minr, minc, maxr, maxc = props.bbox
            # bx = (minc, maxc, maxc, minc, minc)
            # by = (minr, minr, maxr, maxr, minr)
            # axs[5].plot(bx, by, '-b', linewidth=2.5)
            axs[5].plot((reprojd_arr.shape[1]/2, x0), (reprojd_arr.shape[0], y0), '--y', linewidth=1)
        '''

        axs[6].plot(reprojd_arr.shape[1]/2, reprojd_arr.shape[0], '*y', markersize=10)
        
        try:
            fileInfo = geoDb.loc[geoDb['ImageName'] == basename(filename)]
            print((fileInfo['Easting'], fileInfo['Northing']))
            
            axs[6].text(reprojd_arr.shape[1]/2, reprojd_arr.shape[0], '({}, {})'.format(fileInfo['Easting'].values[0], fileInfo['Northing'].values[0]), c='y')

            cntNotLast = True
            if cntNotLast:
                fileInfoNext = geoDb.loc[geoDb['ImageName'] == basename(filelist[cnt + 1])]

                axs[6].plot(reprojd_arr.shape[1]/2, reprojd_arr.shape[0] - 800, '*m', markersize=10)
                axs[6].text(reprojd_arr.shape[1]/2, reprojd_arr.shape[0] - 800, '{}, ({}, {})'.format(basename(filelist[cnt + 1]), fileInfoNext['Easting'].values[0], fileInfoNext['Northing'].values[0]), c='m')
                # Draw distance in white
                # axs[5].text(,c='w')
        except:
            pass


        reprojd_arr = img_as_ubyte(reprojd_arr)#np.rint(reprojd_arr)

        if solidLineOnLeft or solidLineOnRight:
            if solidLineOnLeft:
                print('||||||||||||||||||||||||||||')
                print(inlinersLeft)
                print(reprojd_arr)
                # print(np.sum(reprojd_arr == 7))
                # print(np.sum(reprojd_arr == 12))
                # print(np.sum(reprojd_arr == 25))

                solidLineImgCoords = np.argwhere(np.isin(dilated_p2p, inlinersLeft))
                # axs[3].plot(solidLineImgCoords[:,1], solidLineImgCoords[:,0],'b*',markersize=1)
                # print(len(solidLineImgCoords), solidLineImgCoords[:,0], solidLineImgCoords[:,1])
                bestCurve = curve_fit(cubic, solidLineImgCoords[:,1], solidLineImgCoords[:,0])
                print(bestCurve)


                samples = np.linspace(np.min(solidLineImgCoords[:,1]),np.max(solidLineImgCoords[:,1]),20)

                samplesXY = np.transpose(np.array([samples,cubic(samples,*(bestCurve[0]))]))
                print(samplesXY)
                solidLineImgCoords2 = t2([[s[0], s[1] + h - roadSurface.shape[0]] for s in samplesXY])
                print(solidLineImgCoords)


                nearestPoint = solidLineImgCoords2[np.argmin([euclidean(coord, (reprojd_arr.shape[1]/2, reprojd_arr.shape[0] - 800)) for coord in solidLineImgCoords2])]
                print(nearestPoint)
                axs[6].plot(*nearestPoint, '*w', markersize=10)


                axs[2].plot(samplesXY[:,0],samplesXY[:,1],'b-')
                axs[6].plot(solidLineImgCoords2[:,0],solidLineImgCoords2[:,1],'b-')
                print('^^^^^^^^^^^^^^^^^^^^^^^')

            if solidLineOnRight:
                print('||||||||||||||||||||||||||||')
                print(inlinersRight)
                print(reprojd_arr)
                # print(np.sum(reprojd_arr == 7))
                # print(np.sum(reprojd_arr == 12))
                # print(np.sum(reprojd_arr == 25))

                solidLineImgCoords = np.argwhere(np.isin(dilated_p2p, inlinersRight))
                # axs[3].plot(solidLineImgCoords[:,1], solidLineImgCoords[:,0],'b*',markersize=1)
                # print(len(solidLineImgCoords), solidLineImgCoords[:,0], solidLineImgCoords[:,1])
                bestCurve = curve_fit(cubic, solidLineImgCoords[:,1], solidLineImgCoords[:,0])
                print(bestCurve)


                samples = np.linspace(np.min(solidLineImgCoords[:,1]),np.max(solidLineImgCoords[:,1]),20)

                samplesXY = np.transpose(np.array([samples,cubic(samples,*(bestCurve[0]))]))
                print(samplesXY)
                solidLineImgCoords2 = t2([[s[0], s[1] + h - roadSurface.shape[0]] for s in samplesXY])
                print(solidLineImgCoords)


                nearestPoint = solidLineImgCoords2[np.argmin([euclidean(coord, (reprojd_arr.shape[1]/2, reprojd_arr.shape[0] - 800)) for coord in solidLineImgCoords2])]
                print(nearestPoint)
                axs[6].plot(*nearestPoint, '*w', markersize=10)


                axs[2].plot(samplesXY[:,0],samplesXY[:,1],'b-')
                axs[6].plot(solidLineImgCoords2[:,0],solidLineImgCoords2[:,1],'b-')
                print('^^^^^^^^^^^^^^^^^^^^^^^')





            '''
            skip manhole distance
            '''
            COCO_MODEL_PATH_3 = os.path.join(ROOT_DIR, "mask_rcnn_coco_0169.h5")

            class InferenceConfig_3(coco.CocoConfig):
                GPU_COUNT = 1
                IMAGES_PER_GPU = 1
                NUM_CLASSES = 1 + 8

            config_3 = InferenceConfig_3()

            model_3 = modellib.MaskRCNN(mode="inference", model_dir=MODEL_DIR, config=config_3)

            model_3.load_weights(COCO_MODEL_PATH_3, by_name=True)

            class_names_3 = ['BG', 'bitumen2','white_dash_ok','white_dash_bad','triangle_ok','word_ok','arrow_ok','concrete','arrow_bad','triangle_bad','zebra_ok','zebra_bad','word_bad']
            allowed_tags_3 = ['bitumen2','white_dash_ok','white_dash_bad','triangle_ok','word_ok','arrow_ok','concrete','arrow_bad','triangle_bad','zebra_ok','zebra_bad','word_bad']


            results_3 = model_3.detect([roadSurface], verbose=0)

            del config_3
            del model_3

            # No need to project the polygon
            # Check intersection unprojected samplesXY with results_3[0]['masks'][:,:,r] (unprojected polygons)
            '''
            skip manhole distance
            '''






        reprojd_otsu_arr = warp(np.array(reprojd_otsu.convert('1')), t2.inverse)

        '''
        Note: Needs binary_dilation(selem=disk(3)) for Chinese characters
        '''
        reprojd_otsu_arr = binary_dilation(reprojd_otsu_arr, selem=disk(3))



        axs[7].imshow(reprojd_otsu_arr,cmap='gray')

        # print('Otsu Arr', reprojd_otsu_arr)

        discoloured = np.copy(reprojd_otsu_arr != 0)
        # print('!@!!@@@', discoloured.dtype)
        # print(discoloured)
        discoloured[reprojd_arr == 0] = 1
        # discoloured = np.copy(roadSurfaceGrey>local_otsu)
        # discoloured[dilated_p2p == 0] = 1
        axs[8].imshow(discoloured,cmap='gray')
        axs[8].set_xlabel('{}, {}'.format(num_labels, 'solid lines (shown in blue) on the left and right' if solidLineOnLeft and solidLineOnRight else 'solid line (shown in blue) on the left' if solidLineOnLeft else 'solid line (shown in blue) on the right' if solidLineOnRight else 'no solid lines'))

        ########################################
        #
        #     Show homeogaphy
        #
        ########################################
        # if cnt != 0:
        #     reallbls = np.zeros((image.shape[0],image.shape[1]))
        #     reallbls[results[0]['rois'][r][0]+Y_IGNORE_THRESH:results[0]['rois'][r][2],results[0]['rois'][r][1]:results[0]['rois'][r][3]] = labelled_p2p
        #     reproj_clustering(reprojd_arr)
        #     # kaze_match(prevImage, roadSurface[:, :, ::-1].copy(), reallbls)
        #     # kaze_match(prevImage, roadSurface[:, :, ::-1].copy(), reallbls)
        
        prevImage = roadSurface#[:, :, ::-1].copy()

        mng = plt.get_current_fig_manager()
        mng.window.state('zoomed')

        if DEBUG_MODE:
            plt.show()
        else:
            plt.show(block=False)
            plt.pause(5)
            plt.close()


        r = results[0]
        matplotlib.use('TkAgg')
        visualize.display_instances(image, r['rois'], r['masks'], r['class_ids'], class_names, r['scores'])

        cnt += 1
        
        '''TODO: Publish part'''
        if cnt % 10 == 0:
            dumps
        
        # await asyncio.sleep(5)
        # plt.close()


def reproj_clustering(reprojd):
    params = [{}, {}, {}]
    for param in params:
        myms = MeanShift(bandwidth=0.5) #(distance_threshold=0.5, n_clusters=None)

        # myms.fit(bufferedObjs)
        # print(myms.labels_)
        # print(myms.cluster_centers_)



# def reproj_clustering(prevColorImg, currColorImg, lbls):
#     reprojd = Image.new('RGB', (currColorImg.shape[0], currColorImg.shape[1] * 2))
#     reprojd.paste(currColorImg, (0,currColorImg[1]))

#     src = np.asarray([[0,0],[512,0],[512,512],[0,512]])
#     dst2 = np.asarray([[UPPER_MARGIN-50,UPPER_MARGIN-50],[LOWER_MARGIN+50,UPPER_MARGIN-50],[200+50,LOWER_MARGIN+50],[160-50,LOWER_MARGIN+50]])
    
    # t2 = ProjectiveTransform()
    # t2.estimate(src,dst2)

#     erosion_warped = warp(erosion, t2.inverse)
#     pass



def false_positive_chip_generator():
    pass
    #Use MaskRCNN to cut
    #Stride: 10 pictures
    #Look for with 0 



# Use clustering instead.
def kaze_match(prevColorImg, currColorImg, lbls):
    pass
    # print(prevColorImg.shape)
    # print(lbls.shape)


#     # load the image and convert it to grayscale

#     gray1 = cv2.cvtColor(currColorImg, cv2.COLOR_BGR2GRAY)
#     gray2 = cv2.cvtColor(prevColorImg, cv2.COLOR_BGR2GRAY)   

#     detector = cv2.AKAZE_create()
#     (kps1, descs1) = detector.detectAndCompute(gray1, None)
#     (kps2, descs2) = detector.detectAndCompute(gray2, None)

    # print("keypoints: {}, descriptors: {}".format(len(kps1), descs1.shape))
    # print("keypoints: {}, descriptors: {}".format(len(kps2), descs2.shape)) 

#     bf = cv2.BFMatcher(cv2.NORM_HAMMING)
#     matches = bf.knnMatch(descs1,descs2, k=2)   # typo fixed

#     good = []
#     for m,n in matches:
#         if m.distance < 0.99*n.distance:
#             good.append([m])

#     # filtered = good

    # filtered = list(filter(lambda x: #print(int(kps1[x[0].queryIdx].pt[1]), int(kps1[x[0].queryIdx].pt[0])) and
#         True#lbls[int(kps1[x[0].queryIdx].pt[1]),int(kps1[x[0].queryIdx].pt[0])] != 0
#         # and kps1[x[0].queryIdx].pt[1] < kps2[x[1].queryIdx].pt[1]
#         , good))

#     src_pts = np.float32([ kps1[m[0].queryIdx].pt for m in filtered ]).reshape(-1,1,2)
#     dst_pts = np.float32([ kps2[m[0].trainIdx].pt for m in filtered ]).reshape(-1,1,2)
    # print(src_pts, dst_pts)
#     try:
#         M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC,5.0)
#         matchesMask = mask.ravel().tolist()
        # print('Homography okay.')

#         # filtered = list(filter(lambda x: 
#         #     kps1[x[0].queryIdx].pt[0] > 2020 and kps1[x[0].queryIdx].pt[1] > 600 and kps1[x[0].queryIdx].pt[0] < 2440 and kps1[x[0].queryIdx].pt[1] < 1600 #or 
#         #     # kps1[x[0].queryIdx].pt[0] > 87 and kps1[x[0].queryIdx].pt[1] > 687 and kps1[x[0].queryIdx].pt[0] < 87+951 and kps1[x[0].queryIdx].pt[1] < 687+934 #or 
#         #     # kps1[x[0].queryIdx].pt[0] > 909 and kps1[x[0].queryIdx].pt[1] > 674 and kps1[x[0].queryIdx].pt[0] < 909+38 and kps1[x[0].queryIdx].pt[1] < 674+23
#         #     , good))
        # print( kps1[good[5][0].queryIdx].pt[0] )


#         draw_params = dict(
#                        matchColor = (0,255,0), # draw matches in green color
#                        singlePointColor = None,
#                        matchesMask = matchesMask, # draw only inliers
#                        flags = 2)
#         im3 = cv2.drawMatches(currColorImg,kps1,prevColorImg,kps2,[m[0] for m in filtered],None,**draw_params)


#         # im3 = cv2.drawMatchesKnn(currColorImg, kps1, prevColorImg, kps2, filtered, None, flags=2)
#         im3 = cv2.resize(im3, (int(2048/1.5), int(512/1.5)))
        # print(kps1[good[0][0].queryIdx].pt, kps2[good[0][0].trainIdx].pt)
#         cv2.imshow("AKAZE matching", im3)
#     except Exception as e:
        # print('**************************')
        # print(e)
        # print('**************************')
#     cv2.waitKey(0)




def evaluateDiscoloredPercentage(A, B, T):

    from glob import glob
    import os
    from os import chdir, remove
    from os.path import basename, expanduser
    from subprocess import run
    import sys
    import math
    import random
    from gc import collect
    from shutil import copy2

    import cv2
    import matplotlib.pyplot as plt
    import numpy as np
    from PIL import Image
    import skimage.io
    # from numba import cuda



    # Root directory of the project
    ROOT_DIR = os.path.abspath(os.path.dirname(os.path.realpath(__file__)) + r"\Mask_RCNN-tensorflowone")# OIC imagery\Mask_RCNN-master")

    # Import Mask RCNN
    sys.path.append(ROOT_DIR)  # To find local version of the library

    sys.path.append(os.path.join(ROOT_DIR, "samples/coco/"))  # To find local version

    import mrcnn.model as modellib
    import coco
    from mrcnn import visualize
    import matplotlib.pyplot as plt
    import matplotlib

    # Directory to save logs and trained model
    MODEL_DIR = os.path.join(ROOT_DIR, "logs")

    # Local path to trained weights file
    COCO_MODEL_PATH = os.path.join(ROOT_DIR, "discolouring_bounds.h5")

    class InferenceConfig(coco.CocoConfig):
        # Set batch size to 1 since we'll be running inference on
        # one image at a time. Batch size = GPU_COUNT * IMAGES_PER_GPU
        GPU_COUNT = 1
        IMAGES_PER_GPU = 1
        NUM_CLASSES = 1 + 3

    config = InferenceConfig()
    # config.display()

    # Create model object in inference mode.
    model = modellib.MaskRCNN(mode="inference", model_dir=MODEL_DIR, config=config)

    # print(COCO_MODEL_PATH)
    # Load weights trained on MS-COCO
    model.load_weights(COCO_MODEL_PATH, by_name=True)

    class_names = ['BG', 'chi', 'num', 'alpha']
    allowed_tags = ['chi', 'num', 'alpha']

    matplotlib.use('TkAgg')
    # Compare two segmentations A (moulded) and B (unmoulded)

    # black = background
    # Get white pixels from A

    # Otsu's method
    for filename in natsorted(glob(expanduser(r'~/Desktop/pytorch-CycleGAN-and-pix2pix/datasets/roadmarks/otsu/*.jpg')))[17:]:
        result_otsu = Image.open(filename)
        result_otsu = np.array(result_otsu.convert('1'))


        # GAN impainted
        result_p2p = Image.open(filename.replace('/datasets/roadmarks/otsu','/results/roadmarks_pix2pix/test_latest/images').replace('.jpg', '_fake_B.png'))
        


        #################################
        #    MaskRCNN
        #################################
        results = model.detect([np.array(result_p2p)], verbose=0)

        del config
        del model

        # from skimage import img_as_ubyte
        # result_p2p = Image.fromarray(img_as_ubyte(denoise_tv_chambolle(np.array(result_p2p.convert('L')))))
        result_p2p = remove_small_holes(np.array(result_p2p.convert('1')), connectivity = 2, area_threshold=2)
        labelled_p2p, num_labels = label(result_p2p, connectivity = 1, return_num=True)
        # labelled_p2p=label2rgb(a)

        markTypes = np.empty((num_labels+1,2),dtype=object)

        cnt1 = 0
        for n in range(num_labels+1)[1:]:
            if np.sum(labelled_p2p == n) >= IGNORE_THRESHOLD:
                
                #############################################
                #    Get the Intersection by AND operator
                #############################################
                markType = 'individual'
                instanceNum = None
                for r in range(len(results[0]['class_ids'])):
                    # print('##########################################')
                    # print(np.sum(results[0]['masks'][:,:,r] & (labelled_p2p == n)))

                    if np.sum(results[0]['masks'][:,:,r] & (labelled_p2p == n)) >= RCNN_THRESHOLD:
                        markType = class_names[results[0]['class_ids'][r]]
                        instanceNum = r
                        break

                    # print('##########################################')

                if instanceNum is not None and instanceNum in markTypes[:,1]:
                    replacement = np.argmax(markTypes[:,1] == instanceNum)
                    labelled_p2p[labelled_p2p == n] = replacement
                else:
                    markTypes[n,0] = markType
                    markTypes[n,1] = instanceNum
                    cnt1 += 1

        # print('()()()', markTypes)

        fig, axs = plt.subplots(7, cnt1)
        fig.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=0, hspace=0)

        fig.suptitle(basename(filename))

        cnt=0
        if cnt1 > 1:
            axs[0,0].annotate('Original', xy=(0, 0.5), xytext=(0, 0),
                    xycoords=axs[0,0].yaxis.label, textcoords='offset points',
                    size='small', ha='right', va='center')
            # axs[1,0].annotate('Segmentation', xy=(0, 0.5), xytext=(0, 0),
            #         xycoords=axs[2,0].yaxis.label, textcoords='offset points',
            #         size='small', ha='right', va='center')
            axs[1,0].annotate('Pix2Pix', xy=(0, 0.5), xytext=(0, 0),
                    xycoords=axs[1,0].yaxis.label, textcoords='offset points',
                    size='small', ha='right', va='center')
            axs[2,0].annotate('Pix2Pix eroded (to prevent edges)', xy=(0, 0.5), xytext=(0, 0),
                    xycoords=axs[2,0].yaxis.label, textcoords='offset points',
                    size='small', ha='right', va='center')
            axs[3,0].annotate('Otsu Thresholding', xy=(0, 0.5), xytext=(0, 0),
                    xycoords=axs[3,0].yaxis.label, textcoords='offset points',
                    size='small', ha='right', va='center')
            axs[4,0].annotate('Pix2Pix reprojected (rot/pitch/roll/height are wild guesses)', xy=(0, 0.5), xytext=(0, 0),
                    xycoords=axs[4,0].yaxis.label, textcoords='offset points',
                    size='small', ha='right', va='center')
            axs[5,0].annotate('Otsu Thresholding reprojected (rot/pitch/roll/height are wild guesses)', xy=(0, 0.5), xytext=(0, 0),
                    xycoords=axs[5,0].yaxis.label, textcoords='offset points',
                    size='small', ha='right', va='center')
            axs[6,0].annotate('Discolouring', xy=(0, 0.5), xytext=(0, 0),
                    xycoords=axs[6,0].yaxis.label, textcoords='offset points',
                    size='small', ha='right', va='center')        
            axs[6,0].annotate('Discoloured percentage', xy=(0, 0.5), xytext=(-50, -40),
                    xycoords=axs[6,0].yaxis.label, textcoords='offset points',
                    size='small', ha='right', va='center')
            axs[6,0].annotate('Category', xy=(0, 0.5), xytext=(-50, -50),
                    xycoords=axs[6,0].yaxis.label, textcoords='offset points',
                    size='small', ha='right', va='center')
            axs[6,0].annotate('Pass?', xy=(0, 0.5), xytext=(-50, -60),
                    xycoords=axs[6,0].yaxis.label, textcoords='offset points',
                    size='small', ha='right', va='center')
        else:
            axs[0].annotate('Original', xy=(0, 0.5), xytext=(0, 0),
                    xycoords=axs[0].yaxis.label, textcoords='offset points',
                    size='small', ha='right', va='center')
            # axs[1].annotate('Segmentation', xy=(0, 0.5), xytext=(0, 0),
            #         xycoords=axs[2].yaxis.label, textcoords='offset points',
            #         size='small', ha='right', va='center')
            axs[1].annotate('Pix2Pix', xy=(0, 0.5), xytext=(0, 0),
                    xycoords=axs[1].yaxis.label, textcoords='offset points',
                    size='small', ha='right', va='center')
            axs[2].annotate('Pix2Pix eroded (to prevent edges)', xy=(0, 0.5), xytext=(0, 0),
                    xycoords=axs[2].yaxis.label, textcoords='offset points',
                    size='small', ha='right', va='center')
            axs[3].annotate('Otsu Thresholding', xy=(0, 0.5), xytext=(0, 0),
                    xycoords=axs[3].yaxis.label, textcoords='offset points',
                    size='small', ha='right', va='center')
            axs[4].annotate('Pix2Pix reprojected (rot/pitch/roll/height are wild guesses)', xy=(0, 0.5), xytext=(0, 0),
                    xycoords=axs[4].yaxis.label, textcoords='offset points',
                    size='small', ha='right', va='center')
            axs[5].annotate('Otsu Thresholding reprojected (rot/pitch/roll/height are wild guesses)', xy=(0, 0.5), xytext=(0, 0),
                    xycoords=axs[5].yaxis.label, textcoords='offset points',
                    size='small', ha='right', va='center')
            axs[6].annotate('Discolouring', xy=(0, 0.5), xytext=(0, 0),
                    xycoords=axs[6].yaxis.label, textcoords='offset points',
                    size='small', ha='right', va='center')        
            axs[6].annotate('Discoloured percentage', xy=(0, 0.5), xytext=(-50, -40),
                    xycoords=axs[6].yaxis.label, textcoords='offset points',
                    size='small', ha='right', va='center')
            axs[6].annotate('Category', xy=(0, 0.5), xytext=(-50, -50),
                    xycoords=axs[6].yaxis.label, textcoords='offset points',
                    size='small', ha='right', va='center')
            axs[6].annotate('Pass?', xy=(0, 0.5), xytext=(-50, -60),
                    xycoords=axs[6].yaxis.label, textcoords='offset points',
                    size='small', ha='right', va='center')

        for n in range(num_labels+1)[1:]:



            if np.sum(labelled_p2p == n) < IGNORE_THRESHOLD:
                continue

            # #############################################
            # #    Get the Intersection by AND operator
            # #############################################
            # markType = 'line'
            # for r in range(len(results[0]['class_ids'])):
                # print('##########################################')
                # print(np.sum(results[0]['masks'][:,:,r] & (labelled_p2p == n)))

            #     if np.sum(results[0]['masks'][:,:,r] & (labelled_p2p == n)) >= RCNN_THRESHOLD:
            #         markType = class_names[results[0]['class_ids'][r]]

                # print('##########################################')
            markType = markTypes[n, 0]


            if cnt1 > 1:
                # axs[0,cnt].axis('off')
                axs[0,cnt].set_xticklabels(())            
                axs[0,cnt].set_yticklabels(())            
                axs[0,cnt].get_xaxis().set_visible(False)
                axs[0,cnt].get_yaxis().set_ticks([])
                # axs[0,cnt].get_yaxis().set_visible(False)
                axs[0,cnt].imshow(Image.open(filename.replace('/datasets/roadmarks/otsu','/results/roadmarks_pix2pix/test_latest/images').replace('.jpg', '_real_A.png')))

                # # axs[1,cnt].axis('off')
                # axs[1,cnt].set_xticklabels(())            
                # axs[1,cnt].set_yticklabels(())            
                # axs[1,cnt].get_xaxis().set_visible(False)
                # axs[1,cnt].get_yaxis().set_ticks([])
                # # axs[1,cnt].get_yaxis().set_visible(False)
                # from matplotlib.colors import ListedColormap
                # import matplotlib.cm
                # import math

                # def generate_colormap(N):
                #     arr = np.arange(N)/N
                #     N_up = int(math.ceil(N/7)*7)
                #     arr.resize(N_up)
                #     arr = arr.reshape(7,N_up//7).T.reshape(-1)
                #     ret = matplotlib.cm.hsv(arr)
                #     n = ret[:,3].size
                #     a = n//2
                #     b = n-a
                #     for i in range(3):
                #         ret[0:n//2,i] *= np.arange(0.2,1,0.8/a)
                #     ret[n//2:,3] *= np.arange(1,0.1,-0.9/b)
                #     print(ret)
                #     return ret
                # axs[1,cnt].imshow(np.copy(labelled_p2p),cmap=ListedColormap(generate_colormap(999)))

                # axs[0,cnt].axis('off')
                axs[1,cnt].set_xticklabels(())            
                axs[1,cnt].set_yticklabels(())            
                axs[1,cnt].get_xaxis().set_visible(False)
                axs[1,cnt].get_yaxis().set_ticks([])
                # axs[1,cnt].get_yaxis().set_visible(False)
                axs[1,cnt].imshow(labelled_p2p == n)


                erosion = binary_erosion(np.copy(labelled_p2p == n), selem=disk(2))
                # Scales the image up so that the road mark will not out of the image borders after reprojection
                erosion = resize(erosion, (512,512))
                axs[2,cnt].set_xticklabels(())            
                axs[2,cnt].set_yticklabels(())
                axs[2,cnt].get_xaxis().set_visible(False)
                axs[2,cnt].get_yaxis().set_ticks([])
                # axs[2,cnt].get_yaxis().set_visible(False)
                axs[2,cnt].imshow(erosion,cmap='gray')


                show_otsu = np.copy(result_otsu)
                # Scales the image up so that the road mark will not out of the image borders after reprojection
                show_otsu = resize(show_otsu, (512,512))
                show_otsu[erosion != 1]=0            #show_otsu[labelled_p2p!=n]=0
                # axs[1,cnt].axis('off')
                axs[3,cnt].set_xticklabels(())            
                axs[3,cnt].set_yticklabels(())
                axs[3,cnt].get_xaxis().set_visible(False)
                axs[3,cnt].get_yaxis().set_ticks([])
                # axs[3,cnt].get_yaxis().set_visible(False)
                axs[3,cnt].imshow(show_otsu,cmap='gray')
                # mask_num_pixels = np.sum(show_otsu==1)
                
                # src = np.asarray([[927,2251],[1878,1321],[2491,1301],[3999,2251]])
                # dst2 = np.asarray([[0,2300],[0,0],[1000,0],[1000,2200]])

                src = np.asarray([[0,0],[255,0],[255,255],[0,255]])
                dst2 = np.asarray([[0-50,0-50],[255+50,0-50],[105+50,255+50],[75-50,255+50]])
                
                MARGIN = 36
                UPPER_MARGIN = 0 + MARGIN - 1
                LOWER_MARGIN = 512 - MARGIN - 1


                src = np.asarray([[0,0],[512,0],[512,512],[0,512]])
                dst2 = np.asarray([[UPPER_MARGIN-50,UPPER_MARGIN-50],[LOWER_MARGIN+50,UPPER_MARGIN-50],[200+50,LOWER_MARGIN+50],[160-50,LOWER_MARGIN+50]])
                
                t2 = ProjectiveTransform()
                t2.estimate(src,dst2)

                erosion_warped = warp(erosion, t2.inverse)
                axs[4,cnt].set_xticklabels(())            
                axs[4,cnt].set_yticklabels(())
                axs[4,cnt].get_xaxis().set_visible(False)
                axs[4,cnt].get_yaxis().set_ticks([])
                axs[4,cnt].imshow(erosion_warped)
                # plt.imshow(z)
                # plt.show()
                # #z = z[:,:3280,:]
                # #fig.set_size_inches(z.shape[1]/100,z.shape[0]/100)

                # src = np.asarray([[927,2251],[1878,1321],[2491,1301],[3999,2251]])
                # dst2 = np.asarray([[0,2300],[0,0],[1000,0],[1000,2200]])
     
                # src = np.asarray([[0,0],[255,0],[255,255],[0,255]])
                # dst2 = np.asarray([[0-50,0-50],[255+50,0-50],[105+50,255+50],[75-50,255+50]])
                # t2 = ProjectiveTransform()
                # t2.estimate(src,dst2)

                otsu_warped = warp(show_otsu, t2.inverse)
                axs[5,cnt].set_xticklabels(())            
                axs[5,cnt].set_yticklabels(())
                axs[5,cnt].get_xaxis().set_visible(False)
                axs[5,cnt].get_yaxis().set_ticks([])
                axs[5,cnt].imshow(otsu_warped,cmap='gray')
                mask_num_pixels = np.sum(otsu_warped==1)
                if mask_num_pixels == 0:
                    continue

                # plt.imshow(z)
                # plt.show()
                # #z = z[:,:3280,:]
                # #fig.set_size_inches(z.shape[1]/100,z.shape[0]/100)



                show_discolouring = np.copy(otsu_warped)
                # print(erosion_warped)

                show_discolouring[erosion_warped != 1]=1            # show_discolouring[labelled_p2p!=n]=1
                # axs[2,cnt].axis('off')
                axs[6,cnt].set_xticklabels(())            
                axs[6,cnt].set_yticklabels(())
                axs[6,cnt].get_xaxis().set_ticks([])
                # axs[6,cnt].get_xaxis().set_visible(False)
                axs[6,cnt].get_yaxis().set_ticks([])
                # axs[6,cnt].get_yaxis().set_visible(False)
                discolouring_num_pixels = np.sum(show_discolouring==0)
                axs[6,cnt].imshow(Image.fromarray(np.array(show_discolouring, dtype="bool")),cmap='gray')
                perc = int(np.min((79., round(discolouring_num_pixels/mask_num_pixels*100))))
                axs[6,cnt].set_xlabel('{0}%\n{1} (thresh: {2}%)\n{3}'.format(perc,markType, (50 if markType in ('chi','punct') else 20), ('DISCOLOURED' if perc > (50 if markType in ('chi','punct') else 20) else 'Pass')),{'weight': 'bold'})
            else:
                # axs[0,cnt].axis('off')
                axs[0].set_xticklabels(())            
                axs[0].set_yticklabels(())            
                axs[0].get_xaxis().set_visible(False)
                axs[0].get_yaxis().set_ticks([])
                # axs[0].get_yaxis().set_visible(False)
                axs[0].imshow(Image.open(filename.replace('/datasets/roadmarks/otsu','/results/roadmarks_pix2pix/test_latest/images').replace('.jpg', '_real_A.png')))

                # # axs[1].axis('off')
                # axs[1].set_xticklabels(())            
                # axs[1].set_yticklabels(())            
                # axs[1].get_xaxis().set_visible(False)
                # axs[1].get_yaxis().set_ticks([])
                # # axs[1].get_yaxis().set_visible(False)
                # from matplotlib.colors import ListedColormap
                # import matplotlib.cm
                # import math

                # def generate_colormap(N):
                #     arr = np.arange(N)/N
                #     N_up = int(math.ceil(N/7)*7)
                #     arr.resize(N_up)
                #     arr = arr.reshape(7,N_up//7).T.reshape(-1)
                #     ret = matplotlib.cm.hsv(arr)
                #     n = ret[:,3].size
                #     a = n//2
                #     b = n-a
                #     for i in range(3):
                #         ret[0:n//2,i] *= np.arange(0.2,1,0.8/a)
                #     ret[n//2:,3] *= np.arange(1,0.1,-0.9/b)
                #     print(ret)
                #     return ret
                # axs[1].imshow(np.copy(labelled_p2p),cmap=ListedColormap(generate_colormap(999)))

                # axs[0].axis('off')
                axs[1].set_xticklabels(())            
                axs[1].set_yticklabels(())            
                axs[1].get_xaxis().set_visible(False)
                axs[1].get_yaxis().set_ticks([])
                # axs[1].get_yaxis().set_visible(False)
                axs[1].imshow(labelled_p2p == n)


                erosion = binary_erosion(np.copy(labelled_p2p == n), selem=disk(1))
                # Scales the image up so that the road mark will not out of the image borders after reprojection
                erosion = resize(erosion, (512,512))
                axs[2].set_xticklabels(())            
                axs[2].set_yticklabels(())
                axs[2].get_xaxis().set_visible(False)
                axs[2].get_yaxis().set_ticks([])
                # axs[2].get_yaxis().set_visible(False)
                axs[2].imshow(erosion,cmap='gray')


                show_otsu = np.copy(result_otsu)
                # Scales the image up so that the road mark will not out of the image borders after reprojection
                show_otsu = resize(show_otsu, (512,512))
                show_otsu[erosion != 1]=0            #show_otsu[labelled_p2p!=n]=0
                # axs[1].axis('off')
                axs[3].set_xticklabels(())            
                axs[3].set_yticklabels(())
                axs[3].get_xaxis().set_visible(False)
                axs[3].get_yaxis().set_ticks([])
                # axs[3].get_yaxis().set_visible(False)
                axs[3].imshow(show_otsu,cmap='gray')
                # mask_num_pixels = np.sum(show_otsu==1)
                
                # src = np.asarray([[927,2251],[1878,1321],[2491,1301],[3999,2251]])
                # dst2 = np.asarray([[0,2300],[0,0],[1000,0],[1000,2200]])

                src = np.asarray([[0,0],[255,0],[255,255],[0,255]])
                dst2 = np.asarray([[0-50,0-50],[255+50,0-50],[105+50,255+50],[75-50,255+50]])
                
                MARGIN = 36
                UPPER_MARGIN = 0 + MARGIN - 1
                LOWER_MARGIN = 512 - MARGIN - 1


                src = np.asarray([[0,0],[512,0],[512,512],[0,512]])
                dst2 = np.asarray([[UPPER_MARGIN-50,UPPER_MARGIN-50],[LOWER_MARGIN+50,UPPER_MARGIN-50],[200+50,LOWER_MARGIN+50],[160-50,LOWER_MARGIN+50]])
                
                t2 = ProjectiveTransform()
                t2.estimate(src,dst2)

                erosion_warped = warp(erosion, t2.inverse)
                axs[4].set_xticklabels(())            
                axs[4].set_yticklabels(())
                axs[4].get_xaxis().set_visible(False)
                axs[4].get_yaxis().set_ticks([])
                axs[4].imshow(erosion_warped)
                # plt.imshow(z)
                # plt.show()
                # #z = z[:,:3280,:]
                # #fig.set_size_inches(z.shape[1]/100,z.shape[0]/100)

                # src = np.asarray([[927,2251],[1878,1321],[2491,1301],[3999,2251]])
                # dst2 = np.asarray([[0,2300],[0,0],[1000,0],[1000,2200]])
     
                # src = np.asarray([[0,0],[255,0],[255,255],[0,255]])
                # dst2 = np.asarray([[0-50,0-50],[255+50,0-50],[105+50,255+50],[75-50,255+50]])
                # t2 = ProjectiveTransform()
                # t2.estimate(src,dst2)

                otsu_warped = warp(show_otsu, t2.inverse)
                axs[5].set_xticklabels(())            
                axs[5].set_yticklabels(())
                # axs[5].get_xaxis().set_visible(False)
                axs[5].get_yaxis().set_ticks([])
                axs[5].imshow(otsu_warped,cmap='gray')
                
                # axs[5].set_xlabel('({}, {})'.format(fileInfo['Easting'], fileInfo['Northing']))



                mask_num_pixels = np.sum(otsu_warped==1)
                if mask_num_pixels == 0:
                    continue

                # plt.imshow(z)
                # plt.show()
                # #z = z[:,:3280,:]
                # #fig.set_size_inches(z.shape[1]/100,z.shape[0]/100)



                show_discolouring = np.copy(otsu_warped)
                # print(erosion_warped)

                show_discolouring[erosion_warped != 1]=1            # show_discolouring[labelled_p2p!=n]=1
                # axs[2].axis('off')
                axs[6].set_xticklabels(())            
                axs[6].set_yticklabels(())
                axs[6].get_xaxis().set_ticks([])
                # axs[6].get_xaxis().set_visible(False)
                axs[6].get_yaxis().set_ticks([])
                # axs[6].get_yaxis().set_visible(False)
                discolouring_num_pixels = np.sum(show_discolouring==0)
                axs[6].imshow(Image.fromarray(np.array(show_discolouring, dtype="bool")),cmap='gray')
                perc = int(np.min((90., round(discolouring_num_pixels/mask_num_pixels*100))))
                axs[6].set_xlabel('{0}%\n{1} (thresh: {2}%)\n{3}'.format(perc,markType, (50 if markType in ('chi','punct') else 20), ('DISCOLOURED' if perc > (50 if markType in ('chi','punct') else 20) else 'Pass')),{'weight': 'bold'})
            cnt += 1
        mng = plt.get_current_fig_manager()
        mng.window.state('zoomed')

        if DEBUG_MODE:
            plt.show()
        else:
            plt.show(block=False)
            plt.pause(5)
            plt.close()


            # show_otsu[labelled_p2p==n]=np.invert(show_otsu[labelled_p2p==n])
            # plt.imshow(show_otsu, cmap='gray')
            # plt.show()

    percentage = np.sum(B == 1) / np.sum(A == 1)

    if T in ('chi', 'punct'):
        if percentage >= 0.5 :
            print(f'{T} {percentage}')
        else:
            pass
    elif T in ('alpha', 'num', 'white', 'yellow'):
        if percentage >= 0.2 :
            print(f'{T} {percentage}')
        else:
            pass

if __name__ == '__main__':
    prepare_chips()

    # resize_annotations()
    # rotate_annotations()
    # stratified_shuffle()

    # from labelme2coco import convert
    #



    # threshold()
    
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(handleBigPics())
    
    # evaluateDiscoloredPercentage(1,2,3)
    # eval_pix2pix()
    # slice_characters()