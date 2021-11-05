# Traffic (Part 2)
## Counting using YOLO + SiamMask

*Under Construction*

YOLO is family of object identification model, while SiamMask is a VOS+VOT (video object segmentation + video object tracking) model. In this showcase, we combine the two models.

From the official document [https://developers.arcgis.com/python/guide/track-objects-using-siammask/](https://developers.arcgis.com/python/guide/track-objects-using-siammask/):

> When we have data in Youtube_VOS dataset format, we can call the prepare_data function with dataset_type='ObjectTracking' and for better results use batch_size=64.

The **YouTube_VOS format** (NOT to be confused with YouTube_V*I*S, which is based on COCO rather than VOC2012) is a JSON format similar to VOC2012 dataset format. To start, convert LabelMe segmentations to VOC2012 format.

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
                        "00040", 
                        "00045", 
                        "00050", 
                        "00055", 
                        "00060", 
                        "00065", 
                        "00070", 
                        "00075", 
                        "00080", 
                        "00085", 
                        "00090", 
                        "00095", 
                        "00100", 
                        "00105", 
                        "00110", 
                        "00115", 
                        "00120", 
                        "00125", 
                        "00130", 
                        "00135", 
                        "00140", 
                        "00145", 
                        "00150", 
                        "00155", 
                        "00160", 
                        "00165", 
                        "00170", 
                        "00175"
                    ]
                }
            }
        }
    }
}
```

It is possible to store the flight lines.