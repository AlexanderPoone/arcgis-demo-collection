# 2D Demos

## Georeference Plat+

An enhanced version of the [Georeference Plat widget](https://www.arcgis.com/home/item.html?id=68f3890767a843c0940eb7e9840c5244) by North Point Geographic Solutions. There are four additional features: saving geoferenced floor plans and loading them on the next launch, background removal, <!--skew,--> and rotate.

For loading images that are already georeferenced (e.g. `GeoTIFF` satellite images from a provider like *Planet*) on the fly, consider using a custom tile layer on a 3D SceneView instead.

### Import / Export
The georefrenced images are exported as tuples in the following format:
```js
[{extent: [...], href: '<base64 representation of image>'}]
```

### Background removal & PDF to Image

Usually, floor plan images have a background colour which is not transparent, be it white, beige, or multi-coloured. As a result, other buildings, roads in the basemap will be occluded if the image is directly placed on the map.

The minimal package only contains the `convert` module of **portable** version of ImageMagick, and the **portable** version of GhostScript for reading PDF files. The directory tree looks like this:
```
.
└───removebg
    │   removebg.bat
    │
    └───.magick
            convert.exe     (from ImageMagick)
            delegates.xml   (from ImageMagick)
            gsdll64.dll     (from GhostScript)
            gsdll64.lib     (from GhostScript)
            gswin64c.exe    (from GhostScript)
```
Both pieces of software are in their latest versions. They can be obtained here:
* [ImageMagick-7.1.0-portable-Q16-x64.zip](https://imagemagick.org/script/download.php#windows)
* [GhostscriptPortable_9.55.0.paf.exe](https://portableapps.com/apps/utilities/ghostscript_portable)

If you have a server, you can use `Flask` and `subprocess.check_output()` to open ImageMagick, or use `Node.js` and `child_process.execFileSync()` instead, or even compile ImageMagick to JavaScript using Emscripten.

<!--https://01.org/node/29971?langredirect=1-->

### Rotation

Rotation directly modifies the image stored in Base64.

### Issues in the original widget

1. The opacity slider is not displayed correctly and unusable after importing several images. It has been resolved since the new widget does not use an opacity slider anymore.
![img/b0001.png](img/b0001.png)

(Copyright Ka Wah Properties, Free Use only)
