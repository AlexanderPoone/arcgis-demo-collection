##################################
#
#   Output: JSON file
#   cx_freeze
#
##################################

# Accept upload

<button type="button" id="btn_import" class="btn btn-primary btn-lg">Import image</button>
<input id="hdnInputImport" type="file" style="display:none;" accept=".tif, .tiff, .geotif, .geotiff" />
<button type="button" id="btn_load" class="btn btn-primary btn-lg">Load saves</button>
<input id="hdnInputLoad" type="file" style="display:none;" accept=".json" />



# Generate all possible pairs
for levels in range(a, b):
    for x in range(c, d):
        for y in range(e, f):
            # I just need GDALWRAP !
            run(f'warp.exe -co NUM_THREADS=ALL_CPUS --config GDAL_CACHEMAX 5000 -te {xmin} {ymin} {xmax} {ymax} -te_srs EPSG:3857 -ts {width} {height} -of GTiff "{tiffPath}" "{bpath}" -overwrite -srcalpha -dstalpha')







# Delete file afterwards




# GeoTIFF Tiling
# Preload the large GeoTIFF
@app.route('/warpextent', methods = ['GET'])
def warp():
    global starvision

    info = check_output('"C:/Image_Mgmt_Workflows/OptimizeRasters/GDAL/bin/gdalinfo.exe" "C:/Users/esrismd/Desktop/SVMap.tif"')

    xmin, ymin = [float(x) for x in findall(r'(?<=Lower Left  \(  ).*?(?=\))',info.decode('utf-8'))[0].split(',  ')]
    xmax, ymax = [float(x) for x in findall(r'(?<=Upper Right  \(  ).*?(?=\))',info.decode('utf-8'))[0].split(',  ')]
    
    return [xmin,xmax,ymin,ymax]
    #create layer on clientside

# Release memory
@app.route('/warp', methods = ['GET'])
def warp2():
    # C:\Image_Mgmt_Workflows\OrientedImagery\Dependents\OptimizeRasters\GDAL\bin

    try:
        import os
        os.environ['GDAL_DATA'] = 'C:/Image_Mgmt_Workflows/OptimizeRasters/GDAL/data'
        
        my_env = os.environ.copy()
        my_env["GDAL_DATA"] = 'C:/Image_Mgmt_Workflows/OptimizeRasters/GDAL/data'

        global starvision

        level=request.args.get('level')
        row=request.args.get('row')
        col=request.args.get('col')
        xmin=request.args.get('xmin')
        xmax=request.args.get('xmax')
        ymin=request.args.get('ymin')
        ymax=request.args.get('ymax')
        width=request.args.get('width')
        height=request.args.get('height')

        #chdir(f'D:\Projects\warp')
        #chdir('C:/Image_Mgmt_Workflows/OptimizeRasters/GDAL/data')

        bpath = f"D:/Projects/warp_out/{level}_{row}_{col}_{width}.tif"
        if not exists(bpath) or not exists(bpath.replace('tif','png')):
            run(f'"C:/Image_Mgmt_Workflows/OptimizeRasters/GDAL/bin/gdalwarp.exe" -co NUM_THREADS=ALL_CPUS --config GDAL_CACHEMAX 5000 -te {xmin} {ymin} {xmax} {ymax} -te_srs EPSG:3857 -ts {width} {height} -of GTiff "D:/Projects/warp/SVMap.tif" "{bpath}" -overwrite -srcalpha -dstalpha')     #, stdin=DEVNULL, stderr=DEVNULL).decode(encoding='utf-8')

            im = Image.open(bpath)
            im.save(bpath.replace('tif','png'))
            try:
                remove(bpath)
            except:
                pass
            
        #return f'"C:/Image_Mgmt_Workflows/OptimizeRasters/GDAL/bin/gdalwarp.exe" -te {xmin} {ymin} {xmax} {ymax} -te_srs EPSG:3857 -ts {width} {height} -of BMP "C:/Users/esrismd/Desktop/SVMap.tif" "D:/Projects/warp/warp.bmp" -overwrite -srcalpha'            #f'"C:/Image_Mgmt_Workflows/OptimizeRasters/GDAL/bin/gdalwarp.exe" -te {xmin} {ymin} {xmax} {ymax} -te_srs EPSG:3857 -ts {width} {height} -of BMP "C:/Users/esrismd/Desktop/SVMap.tif" "D:/Projects/warp/warp.bmp" -overwrite -srcalpha'
        #searchText = check_output(f"\"C:/Program Files/ArcGIS/Pro/bin/Python/envs/my-env/python.exe\" -c \"from osgeo import gdal,osr;x=osr.SpatialReference();x.SetFromUserInput('EPSG:4326');wo = gdal.WarpOptions(format='BMP', outputBounds=({xmin},{ymin},{xmax},{ymax}), outputBoundsSRS=x, targetAlignedPixels=False, width={width}, height={height}, multithread=True,srcAlpha=True);gdal.Warp('tmp.bmp', 'C:/Users/esrismd/Desktop/SVMap.tif', options=wo);\"", stdin=DEVNULL, stderr=DEVNULL).decode(encoding='utf-8')


        return send_file(bpath.replace('tif','png'), mimetype="image/png")
        '''
        if exists(bpath):
            return send_file(bpath, mimetype="image/bmp")
        else:
            return ''
        '''
    except Exception as e:
        return str(e)
        #return f"\"C:/Program Files/ArcGIS/Pro/bin/Python/envs/my-env/python.exe\" -c \"from osgeo import gdal,osr;x=osr.SpatialReference();x.SetFromUserInput('EPSG:4326');wo = gdal.WarpOptions(format='BMP', outputBounds=({xmin},{ymin},{xmax},{ymax}), outputBoundsSRS=x, targetAlignedPixels=False, width={width}, height={height}, multithread=True,srcAlpha=True);gdal.Warp('tmp.bmp', 'C:/Users/esrismd/Desktop/SVMap.tif', options=wo);\""
