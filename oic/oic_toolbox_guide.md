# OIC Toolbox Guide

* [KML Start](#kml-start)
* [Riegl Start](#riegl-start)

## KML Start
It is assumed that there is a KML file with the following structure:
![KML Structure](img/oic_toolbox/kml_structure.png)

You have to use the [`kml_to_exif.pyt`](kml_to_exif.pyt) toolbox to propagate the EXIF metadata of images before uploading them to Internet storage.

In ArcGIS Pro, create a new **Scene** if you have not done it. 

1. In the **Insert** tab of ArcGIS Pro, click **Toolbox** > **Add Toolbox**.

![Step 1](img/oic_toolbox/step1.png)

2. Select **kml_to_exif.pyt**.

![Step 2](img/oic_toolbox/step2.png)

3. In the Geoprocessing panel, search *exif*.

![Step 3](img/oic_toolbox/step3.png)

4. In the toolbox tab, click **Browse...** under **KML File**.

![Step 4](img/oic_toolbox/step4.png)

## Riegl Start
...

[Continue the guide](.)