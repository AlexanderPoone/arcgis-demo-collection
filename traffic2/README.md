# Traffic (Part 2)
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
```

Obtaining custom training data is easy:

```
ffmpeg -i https://s35.ipcamlive.com/streams/<replace id here w selenium-wire>/stream.m3u8 -vsync 0 -vf fps=1 one%d.png
```

The outputs should be the vehicle type (from YOLO), object identifier (from SiamMask), oriented bounding box (from SiamMask), and timestamp.

Trajectories can be constructed from these four columns afterwards. One way of registering pixel coordinates to map coordinates involves warping the image.

## Installation
To install the dependencies of SiamMask, open a bundled Command Prompt and type the following:
```
conda install pyarrow numpy
conda install pyg -c conda-forge
```

To convert *labelme annotations* into *YOLO format*:
```
under construction
```

To convert *labelme annotations* into *VOC2012 format*:
```
rm -rf build
python "C:/Users/Alex/Desktop/labelme/examples/semantic_segmentation/labelme2voc.py" --labels labels.txt "_internal/CUH-Dataset/JPEGImages/two" build
```

To convert *VOC2012 format* into *YouTube_VOS format*:
```
under construction
```