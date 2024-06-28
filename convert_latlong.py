"""
Function for converting 3D array of lat-long coordinates to projected coordinate system
"""

from osgeo import ogr
from osgeo import osr
from osgeo import gdal
import h5py as h5

gdal.UseExceptions()


def convert_latlong(lat:float,lon:float,wktIn:str,wktOut:str) -> tuple[float,float]:
        inSR = osr.SpatialReference()
        inSR.ImportFromWkt(wktIn)

        outSR = osr.SpatialReference()
        outSR.ImportFromWkt(wktOut)

        Point = ogr.Geometry(ogr.wkbPoint)
        Point.AddPoint(lon,lat)
        Point.AssignSpatialReference(inSR)
        Point.TransformTo(outSR)
        print(f"Transformation: Lat:{lat} Long:{lon}\n   --> X:{Point.GetX()} Y:{Point.GetY()}")

        return Point.GetX(),Point.GetY()


if __name__ == "__main__":
    with h5.File('Data/targeted.hdf5') as f:
        loc = f["Backplanes/LatLongElev"][:,:,:]

    #Formatted as (lat,long)
    pts = {
        "bl" : (loc[1,0,0],loc[0,0,0]),
        "tl" : (loc[1,-1,0],loc[0,-1,0]),
        "br" : (loc[1,0,-1],loc[0,0,-1]),
        "tr" : (loc[1,-1,-1],loc[0,-1,-1])
    }
    
    for key in pts.keys():
        print(key)
        convert_latlong(*pts[key],'C:/Lunar_Imagery_Data/MI_data/MI_MAP_03_N37E318N36E319SC.lbl')
