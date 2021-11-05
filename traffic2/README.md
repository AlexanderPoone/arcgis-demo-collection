# Traffic (Part 2)
## Counting using YOLO + SiamMask

*Under Construction*

YOLO is family of object identification model, while SiamMask is a VOS+VOT (video object segmentation + video object tracking) model. In this showcase, we combine the two models.

From the official document [https://developers.arcgis.com/python/guide/track-objects-using-siammask/](https://developers.arcgis.com/python/guide/track-objects-using-siammask/):

> When we have data in Youtube_VOS dataset format, we can call the prepare_data function with dataset_type='ObjectTracking' and for better results use batch_size=64.

The **YouTube_VOS format** (NOT to be confused with YouTube_V*I*S, which is based on COCO rather than VOC2012) is a JSON format similar to VOC2012 dataset format. To start, convert LabelMe segmentations to VOC2012 format.

```json
    "videos": [{
        "license": 1,
        "coco_url": "",
        "height": 720,
        "width": 1280,
        "length": 36,
        "date_captured": "2019-04-11 00:18:45.652544",
        "flickr_url": "",
        "file_names": ["00f88c4f0a/00000.jpg", "00f88c4f0a/00005.jpg", "00f88c4f0a/00010.jpg", "00f88c4f0a/00015.jpg", "00f88c4f0a/00020.jpg", "00f88c4f0a/00025.jpg", "00f88c4f0a/00030.jpg", "00f88c4f0a/00035.jpg", "00f88c4f0a/00040.jpg", "00f88c4f0a/00045.jpg", "00f88c4f0a/00050.jpg", "00f88c4f0a/00055.jpg", "00f88c4f0a/00060.jpg", "00f88c4f0a/00065.jpg", "00f88c4f0a/00070.jpg", "00f88c4f0a/00075.jpg", "00f88c4f0a/00080.jpg", "00f88c4f0a/00085.jpg", "00f88c4f0a/00090.jpg", "00f88c4f0a/00095.jpg", "00f88c4f0a/00100.jpg", "00f88c4f0a/00105.jpg", "00f88c4f0a/00110.jpg", "00f88c4f0a/00115.jpg", "00f88c4f0a/00120.jpg", "00f88c4f0a/00125.jpg", "00f88c4f0a/00130.jpg", "00f88c4f0a/00135.jpg", "00f88c4f0a/00140.jpg", "00f88c4f0a/00145.jpg", "00f88c4f0a/00150.jpg", "00f88c4f0a/00155.jpg", "00f88c4f0a/00160.jpg", "00f88c4f0a/00165.jpg", "00f88c4f0a/00170.jpg", "00f88c4f0a/00175.jpg"],
        "id": 1
    }]
```

It is possible to store the flight lines.