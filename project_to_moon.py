"""
Script for creating projected envi files from arrays
"""

import numpy as np
from osgeo import gdal
from osgeo import osr
import tkinter as tk
from tkinter import filedialog
import h5py as h5
from pathlib import Path
import os

from convert_latlong import convert_latlong

gdal.UseExceptions()


def get_geotransform(file_path : Path, wktIn : str, wktOut : str) -> tuple[float,float,float,float,float,float]:
    

    with h5.File(file_path) as f:
        loc = f["Backplanes/LatLongElev"][:,:,:]

    pts = {
        "bl" : (loc[1,0,0],loc[0,0,0]),
        "tl" : (loc[1,-1,0],loc[0,-1,0]),
        "br" : (loc[1,0,-1],loc[0,0,-1]),
        "tr" : (loc[1,-1,-1],loc[0,-1,-1])
    }

    pts_xy = {}
    for key in pts.keys():
        print(key)
        x,y = convert_latlong(*pts[key],wktIn,wktOut)
        pts_xy[key] = (x,y)
    
    def eucdistance(x1,y1,x2,y2):
        return np.sqrt((y2-y1)**2+(x2-x1)**2)

    xres = eucdistance(*pts_xy["bl"],*pts_xy["br"]) / loc.shape[2]
    yres = eucdistance(*pts_xy["bl"],*pts_xy["tl"]) / loc.shape[1]

    return (pts_xy["tl"][0] - (xres/2.),xres,0,pts_xy["tl"][1] - (yres/2.),0,-yres)


def convert(file_path : Path, save_dir : Path) -> None:


    with h5.File(file_path) as f:
        data = f["VectorDatasets/SmoothSpectra_GNDTRU"][:,:,:]
        wavelengths = f.attrs["smooth_wavelengths"]
    
    print(f"Dataset with dimensions {data.shape} has been loaded.")

    gcs = 'GEOGCS["GCS_MOON",DATUM["D_MOON",SPHEROID["MOON",1737400,0]],PRIMEM["Reference_Meridian",0],UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]]]'

    projcs = 'PROJCS["SIMPLE_CYLINDRICAL MOON",GEOGCS["GCS_MOON",DATUM["D_MOON",SPHEROID["MOON",1737400,0]],PRIMEM["Reference_Meridian",0],UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]]],PROJECTION["Equirectangular"],PARAMETER["standard_parallel_1",0],PARAMETER["central_meridian",0],PARAMETER["false_easting",0],PARAMETER["false_northing",0],UNIT["metre",1,AUTHORITY["EPSG","9001"]],AXIS["Easting",EAST],AXIS["Northing",NORTH]]'

    gtrans = get_geotransform(file_path,gcs,projcs)

    save_path = Path(save_dir,file_path.stem,).with_suffix('.img')

    sref = osr.SpatialReference()
    sref.ImportFromWkt(projcs)

    with gdal.GetDriverByName('ENVI').Create(save_path,data.shape[2],data.shape[1],data.shape[0]) as ds:
        ds.WriteArray(data[:,::-1,:])
        ds.SetSpatialRef(sref)
        ds.SetGeoTransform(gtrans)

        for i in range(1,data.shape[0]+1,1):
            rb = ds.GetRasterBand(i)
            rb.SetDescription(f"{wavelengths[i-1]}")
    
    with open(Path(save_path.parents[0],save_path.stem).with_suffix('.hdr'),"a") as f:
        f.write('wavelength units = um\n')
        f.write(f'wavelength = {{{",".join(wavelengths.astype(str))}}}')

    return None

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()

    file_path = "./Data/targeted/targeted.hdf5"#filedialog.askopenfilename(initialdir="./Data/")

    save_dir = "./Data/"#filedialog.askdirectory(initialdir="./Data/")


    convert(Path(file_path),Path(save_dir))
