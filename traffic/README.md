# Traffic Demos

## 1. Car count using the YOLOv3 library from `arcgis.learn`

[![Live Traffic View Using Object Detection & GeoEvent Server](https://img.youtube.com/vi/dG4d191XsqU/0.jpg)](https://www.youtube.com/watch?v=dG4d191XsqU "Live Traffic View Using Object Detection & GeoEvent Server")

The Python tool leverages the open-source YOLOv3 convolutional neural network (CNN) library bundled in the `arcgis.learn` Python library. The neural network is designed for fast object detection.

### Instructions
For the detection to be useful, some work needs to be done beforehand. First, draw the polygons for each traffic lane, and the tool will turn them into pixel coordinates.

|![Fig. 1](img/define_polygons.png)  |![Fig. 2](img/define_polygons2.png) |
|![Fig. 3](img/define_polygons3.png) |![Fig. 4](img/define_polygons4.png) |

For each recognition, the Python tool tests whether the centres of the bounding box is inside each polygon, and updates the Feature Layer according to the camera code detected and vehicle position (traffic lane).

### Future enhancements

Stream output video to a HTML page

## 2. TomTom Traffic Data

See `cron.py`.

### Instructions

Gather the 3D models you want to use, normally one model should have more than one material, which is suboptimal since loading the textures degrade the performance. Therefore, it is required to **UV unwrap** of each model and **texture bake** it into a small texture (e.g. 256 px * 256 px). For lights, use **combined bake** instead of texture bake. Export all models into GLTB which is the only supported format.

### Future enhancements

Handle speeds of finer sections

### Common Questions

* How is the data historical traffic data collected?

The TomTom Traffic API is queried every half minute. The collected data is then grouped by road segment, date of week and the 10-minute time frame, in order to obtain the average speeds.

* Which time period is the historical traffic data collected?

We are at an early stage. We have been collecting data from TomTom since mid-August.
Where is the historical traffic data stored?
The data is hosted on ArcGIS Online as a Table Service.

* What is the algorithm in a nutshell?

There is a single **for-loop** to render the graphics that updates every 1 / frame-per-rate seconds. The displacement distances of each frame are calculated by the formulae: S = D / T; Dsegment = { [S * (1/60/60)] * 1000 } metres; Dframe = (Dsegment / fps) metres.

* How did you obatain the mesh model?

The mesh model is mostly customly made. A portion of the model is taken from the Lands Department.