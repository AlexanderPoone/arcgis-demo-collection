# OSM Toolbox Guide

In ArcGIS Pro, create a new **Scene**. 

1. In the **Insert** tab of ArcGIS Pro, click **Toolbox** > **Add Toolbox**.

![Step 1](img/step1.png)

2. Select **osm_building_to_feature_lyr.pyt**.

![Step 2](img/step2.png)

3. In the Geoprocessing panel, search **osm**.

![Step 3](img/step3.png)

4. Enter the **Extent min longitude (xmin)**, **Extent max longitude (xmax)**, **Extent min latitude (ymin)** and **Extent max latitude (ymax)**. These data can be found at the bottom of the scene.

![Step 4](img/step4.png)

5. In the toolbox tab, click **Browse...** under **Output Features**.

![Step 5](img/step5.png)

6. Navigate to **Database**, and double click on the current geodatabase.

![Step 6](img/step6.png)

7. Name the output layer, and click **Save**.

![Step 7](img/step7.png)

8. After the execution succeeded, in the **Share** tab, click **Web Scene**.

![Step 8](img/step8.png)

9. After sharing succeeded, click **Manage the shared layer**. A browser window will open.