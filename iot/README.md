# Internet of Things Demos

## Sensors Dashboard

[https://demo2.hkgisportal.com/sensors2/](https://demo2.hkgisportal.com/sensors2/)

This is a clone of the [Coolmaps NYC Work Orders](https://coolmaps.esri.com/NYC/NYCHA/dashboard/) app, with the residential block changed to the newly-built eResidence in To Kwa Wan, Kowloon, Hong Kong. A GeoEvent Server installation is required.

The geoprocessing tool **Polygon Neighbours** is used to find neighbouring units of selected flats.

## Sensor Readings

To change the readings of sensors (for demonstration only), run `python `[**outside_controller.py**](outside_controller.py). No remote desktop is needed.

### Future Enhancements
Some data wrangling is needed. Hopefully we may release a ModelBuilder to automate data preprocessing.