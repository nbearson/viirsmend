#!/usr/bin/env python
# encoding: utf-8
"""
Author: Nick Bearson, nickb@ssec.wisc.edu
Copyright (c) 2013 University of Wisconsin SSEC. All rights reserved.
"""

import os
import re
import shutil

import numpy as np
import h5py

import viirsmend as vm


ViirsGeoGroup = {}
ViirsGeoGroup['GMTCO'] = '/All_Data/VIIRS-MOD-GEO-TC_All'
ViirsGeoGroup['GITCO'] = '/All_Data/VIIRS-IMG-GEO-TC_All'
ViirsGeoGroup['GDNBO'] = '/All_Data/VIIRS-IMG-GEO-TC_All'


ViirsBandGroup = {}
ViirsBandGroup['SVDNB'] = '/All_Data/VIIRS-DNB-SDR_All'
ViirsBandGroup['SVI01'] = '/All_Data/VIIRS-I1-SDR_All'
ViirsBandGroup['SVI02'] = '/All_Data/VIIRS-I2-SDR_All'
ViirsBandGroup['SVI03'] = '/All_Data/VIIRS-I3-SDR_All'
ViirsBandGroup['SVI04'] = '/All_Data/VIIRS-I4-SDR_All'
ViirsBandGroup['SVI05'] = '/All_Data/VIIRS-I5-SDR_All'
ViirsBandGroup['SVM01'] = '/All_Data/VIIRS-M1-SDR_All'
ViirsBandGroup['SVM02'] = '/All_Data/VIIRS-M2-SDR_All'
ViirsBandGroup['SVM03'] = '/All_Data/VIIRS-M3-SDR_All'
ViirsBandGroup['SVM04'] = '/All_Data/VIIRS-M4-SDR_All'
ViirsBandGroup['SVM05'] = '/All_Data/VIIRS-M5-SDR_All'
ViirsBandGroup['SVM06'] = '/All_Data/VIIRS-M6-SDR_All'
ViirsBandGroup['SVM07'] = '/All_Data/VIIRS-M7-SDR_All'
ViirsBandGroup['SVM08'] = '/All_Data/VIIRS-M8-SDR_All'
ViirsBandGroup['SVM09'] = '/All_Data/VIIRS-M9-SDR_All'
ViirsBandGroup['SVM10'] = '/All_Data/VIIRS-M10-SDR_All'
ViirsBandGroup['SVM11'] = '/All_Data/VIIRS-M11-SDR_All'
ViirsBandGroup['SVM12'] = '/All_Data/VIIRS-M12-SDR_All'
ViirsBandGroup['SVM13'] = '/All_Data/VIIRS-M13-SDR_All'
ViirsBandGroup['SVM14'] = '/All_Data/VIIRS-M14-SDR_All'
ViirsBandGroup['SVM15'] = '/All_Data/VIIRS-M15-SDR_All'
ViirsBandGroup['SVM16'] = '/All_Data/VIIRS-M16-SDR_All'


ViirsITags = ['SVI01',
              'SVI02',
              'SVI03',
              'SVI04',
              'SVI05',]


ViirsMTags = ['SVM01',
              'SVM02',
              'SVM03',
              'SVM04',
              'SVM05',
              'SVM06',
              'SVM07',
              'SVM08',
              'SVM09',
              'SVM10',
              'SVM11',
              'SVM12',
              'SVM13',
              'SVM14',
              'SVM15',
              'SVM16',]



def loopfiles(fgeo_name):

  geotag = os.path.basename(fgeo_name)[:5]
  if geotag == "GMTCO":
    bandtags = ViirsMTags
    res = vm.MOD_RESOLUTION
  elif geotag == "GITCO":
    bandtags = ViirsITags
    res = vm.IMG_RESOLUTION
  else:
    raise RuntimeError, "geo tag [", geotag, "] not recognized"

  fgeo = h5py.File(fgeo_name, 'r')
  lats = fgeo["%s/Latitude"  % ViirsGeoGroup[geotag]][:]
  lons = fgeo["%s/Longitude" % ViirsGeoGroup[geotag]][:]

  vmr = vm.ViirsMender(lons, lats, res)
  
  for sdrtag in bandtags:
    # making copy of file so we preserve the original 
    fsdr_name = fgeo_name.replace(geotag, sdrtag) # TODO: this won't work, last few values (c....) aren't the same 
    fsdr_mend_name = fsdr_name.replace(".h5", ".mended.h5")
    shutil.copyfile(fsdr_name, fsdr_mend_name)

    print "Mending ", fsdr_mend_name
    fsdr = h5py.File(fsdr_mend_name, 'r+')
    for dtype in ["Radiance", "Reflectance", "BrightnessTemperature"]:
      print dtype
      try:
        sdsname = "%s/%s" % (ViirsBandGroup[bandtag], dtype) 
        data = fsdr[sdsname][:]
        vmr.mend(data)
        # replacing in-place with mended data
        fsdr[sdsname][:] = data
      except:
        continue # expect lots of exceptions, being naive and trying every sds on every file 
    fsdr.close()


if __name__ == "__main__":
  import logging
  LOG_LEVEL = logging.DEBUG
  LOG_FORMAT = '%(asctime)s %(funcName)s %(lineno)s %(levelname)s: %(message)s'
  logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)

  import sys
  geofile = sys.argv[1]

  loopfiles(geofile)
