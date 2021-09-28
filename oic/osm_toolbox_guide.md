# OSM-Buildings Toolbox Guide

In ArcGIS Pro, create a new **Scene**. 

1. In the **Insert** tab of ArcGIS Pro, click **Toolbox** > **Add Toolbox**.

![Step 1](img/step1.png)

2. Select **osm_building_to_feature_lyr.pyt**.

![Step 2](img/step2.png)

3. In the Geoprocessing panel, search *osm*.

![Step 3](img/step3.png)

4. Enter the **Extent min longitude (xmin)**, **Extent max longitude (xmax)**, **Extent min latitude (ymin)** and **Extent max latitude (ymax)**. These data can be found at the bottom of the scene.

![Step 4](img/step4.png)

5. In the toolbox tab, click **Browse...** under **Output Features**.

![Step 5](img/step5.png)

6. Navigate to **Database**, and double click on the current geodatabase.

![Step 6](img/step6.png)

7. Name the output layer, and click **Save**.

![Step 7](img/step7.png)

8. After the execution succeeded, in the **Contents Tab**, right click on the output feature layer, then click on **Properties**.

![Step 8](img/step8.png)

9. On the left, click on **Elevation**, and choose **On the ground** from the drop-down menu.

![Step 9](img/step9.png)

10. Left click on the output feature layer.

![Step 10](img/step10.png)

11. In the **Appearance** tab, click **Type** and select **Base Height**. For **Field**, choose **height** from the drop-down menu.

![Step 11](img/step11.png)

12. In the **Contents Tab**, right click on **Scene**, then click on **Properties**.

![Step 12](img/step12.png)

13. On the left, click on **Coordinates System**, search *3857*, and select **WGS 1984 Web Mercator (auxiliary sphere)**.

![Step 13](img/step13.png)

14. After the execution succeeded, in the **Share** tab, click **Web Scene**.

![Step 14](img/step14.png)

15. Make sure the scene contains no unwanted items. Fill in the details, and click **Share**.

![Step 15](img/step15.png)

16. After sharing succeeded, click **Manage the shared layer**. A browser window will open.

![Step 16](img/step16.png)

17. On the Scene Viewer page, click the button next to uploaded layer, then click **Layer Properties**.

![Step 17](img/step17.png)

18. Change the colour and transparency of the blocks.

![Step 18](img/step18.png)

19. Customise the layer as below:

![Step 19](img/step19.png)