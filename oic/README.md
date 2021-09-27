# Oriented Imagery Demos

## 360-degree Overlay

[![Overlay Widget (now w/ navigation and mini-map)](https://img.youtube.com/vi/-D5tzqwLU70/0.jpg)](https://www.youtube.com/watch?v=-D5tzqwLU70 "Overlay Widget (now w/ navigation and mini-map)")

The panoramic image rendered using the [Three.JS](https://threejs.org/) library and is overlayed onto the `SceneView` directly. Arrows are added using the `SVGLoader` into the `ThreeJS.Scene` for navigation. A mathematical formula is used to synchronise the zoom levels of the `ThreeJS.Scene` and the `SceneView` for zooming in/out.

### Instructions
To use tools like Measurement and Line of Sight in Overlay Mode, you need to add a layer with 3D buildings to the Scene beforehand.

For Hong Kong, you may find 3D buildings from governmental organisations (e.g. HKMS 2.0, GeodataStore). For Macau and cities in mainland China (e.g. Shanghai in the second demo below), you may find shared items on ArcGIS Online from other users, or obtain the data from [https://osmbuildings.org/](OSM-Buildings). Be cautious that the coverage of OSM-Buildings is limited, and the data may have large discrepancies.

[comment]: <> (getHeading prev, next)

A custom geoprocessing tool is made using [https://overpass-turbo.eu/](Overpass-Turbo) to convert OSM-Buildings into extruded features.

### Demos
* [Kowloon Bay/Kai Tak, Hong Kong](https://dord.mynetgear.com/oic)
* [Hongkou District, Shanghai](https://dord.mynetgear.com/oicsh)

### Future enhancements
Calculate Intersections, Historical Panel