# Repository Demos

## Handling 3D Objects on the Fly
### Empirical results
Experiments have shown that using Blender to extract the coordinates and footprint of 3D models is at least three times faster than using Safe's FME alike.

### Suggestion
If we can bundle `Blender` and `ImageMagick`, both of them open-source software, we are able to fulfil the following requirements:
* Format conversion for most formats to most formats
* Thumbnail creation for most formats
* Coordinates and footprint extraction

To install the dependencies, enter the following in the command line:
```
pip3 install -r requirements.txt
```
