# Traffic (Part 2)

## Multiple Object Tracking (MOT) using DeepSORT-ResNet101

Tracking demo here: [https://www.youtube.com/watch?v=a-X71Ce5R7E](https://www.youtube.com/watch?v=a-X71Ce5R7E)

<!-- 
## Counting using YOLO + SiamMask

*Under Construction*

YOLO is family of object identification model, while SiamMask is a VOS+VOT (video object segmentation + video object tracking) model. In this showcase, we combine the two models.

From the official document [https://developers.arcgis.com/python/guide/track-objects-using-siammask/](https://developers.arcgis.com/python/guide/track-objects-using-siammask/):

> When we have data in Youtube_VOS dataset format, we can call the prepare_data function with dataset_type='ObjectTracking' and for better results use batch_size=64.

The **YouTube_VOS format** mentioned above (NOT to be confused with YouTube_V*I*S, which is based on COCO rather than VOC2012) is a dataset format similar to VOC2012 dataset format. To start, convert LabelMe segmentations to the VOC2012 format.

`meta.json`:
```json
{
    "videos": {
        "003234408d": {
            "objects": {
                "1": {
                    "category": "penguin", 
                    "frames": [
                        "00000", 
                        "00005", 
                        "00010", 
                        "00015", 
                        "00020", 
                        "00025", 
                        "00030", 
                        "00035", 
                        "00040"
                    ]
                }
            }
        }
    }
}
``` -->

## Obtaining raw data for training 

Obtaining custom training data is easy. Get the open-source ffmpeg and execute the following command (JPEG must be used):

```
ffmpeg -i https://s35.ipcamlive.com/streams/<replace id here w selenium-wire>/stream.m3u8 -vsync 0 -vf fps=1 %d.jpg
```

The outputs should be the vehicle type (from YOLO), object identifier (from SiamMask), oriented bounding box (from SiamMask), and timestamp.

Trajectories can be constructed from these four columns afterwards. One way of registering pixel coordinates to map coordinates involves warping the image.

## Processing data for training

We label the images with suffix: `<type>_<objectid>`.

To convert *labelme annotations* into *YOLO format*:
```
python 1_labelme2yolo.py
```

To convert *labelme annotations* into *VOC2012 format* (under construction, to be refactored to Python):
```
python 2_labelme2voc.py
```

To convert *VOC2012 format* into *YouTube_VOS format*:
```
python 3_voc2youtubevos.py
```

## Installation
To install the dependencies of SiamMask, open a bundled Command Prompt and type the following:
```
conda install -c esri deep-learning-essentials
```
<!-- conda install pyarrow fastai torchvision scikit-image opencv pyg numpy tensorflow onnx onnx-tf -c pyg -c conda-forge -->
<!--
conda install pyarrow fastai torchvision scikit-image opencv
conda install pyg -c pyg -c conda-forge
conda install -c conda-forge numpy
-->
**(It is the best to use CUDA 11.1)**

To start the Jupyter notebook:
```
"C:\Program Files\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe" "C:\Program Files\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\Scripts\jupyter-notebook-script.py"
```

## Image coordinates to Web Mercator points
Image warping using manually inputted homeography points
