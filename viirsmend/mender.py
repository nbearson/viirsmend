#!/usr/bin/env python
# encoding: utf-8
"""
Author: Nick Bearson, nickb@ssec.wisc.edu
Copyright (c) 2013 University of Wisconsin SSEC. All rights reserved.
"""

import os
import re
import shutil
import glob
from optparse import OptionParser

import numpy as np
import h5py

import viirsmend as vm

import logging
log = logging.getLogger(__name__)


def _usage():
  return """usage: %prog [geolocation file]
  Script expects matching SDR files to be in the same directory, but will gracefully skip over any that don't exist.
"""

def _handle_args():
  parser = OptionParser(usage=_usage())
  parser.add_option('-v', '--verbose', dest='verbosity', action="count", default=0,
                    help='each occurrence increases verbosity 1 level through ERROR-WARNING-INFO-DEBUG')
  return parser

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

def replace_c(filename):
  dirname = os.path.dirname(filename)
  basename = os.path.basename(filename)
  identifier = "_".join(basename.split("_")[:5])
  globstr = dirname + "/" + identifier + "*" + "noaa_ops.h5"
  log.info("Globbing on: %s" % (globstr))
  fname = glob.glob(globstr)[0]
  return fname


def loopfiles(fgeo_name):

  geotag = os.path.basename(fgeo_name)[:5]
  if geotag == "GMTCO":
    bandtags = ViirsMTags
    res = vm.MOD_RESOLUTION
  elif geotag == "GITCO":
    bandtags = ViirsITags
    res = vm.IMG_RESOLUTION
  else:
    raise RuntimeError, "geo tag [%s] not recognized" % (geotag)

  fgeo = h5py.File(fgeo_name, 'r')
  lats = fgeo["%s/Latitude"  % ViirsGeoGroup[geotag]][:]
  lons = fgeo["%s/Longitude" % ViirsGeoGroup[geotag]][:]

  vmr = vm.ViirsMender(lons, lats, res)
  
  for sdrtag in bandtags:
    # making copy of file so we preserve the original 
    fsdr_name = fgeo_name.replace(geotag, sdrtag)
    # we'd be ok at this point, if the c#### section of the filename wasn't unique for every file
    try:
      fsdr_name = replace_c(fsdr_name)
    except:
      log.warn("replace_c couldn't find file to match %s" % (fsdr_name))
      continue # common except if file doesn't exist

    fsdr_mend_name = fsdr_name.replace(".h5", ".mended.h5")
    shutil.copyfile(fsdr_name, fsdr_mend_name)

    print "Creating: ", fsdr_mend_name
    fsdr = h5py.File(fsdr_mend_name, 'r+')
    for dtype in ["Radiance", "Reflectance", "BrightnessTemperature"]:
      log.info("Trying dtype: %s" % (dtype))
      try:
        sdsname = "%s/%s" % (ViirsBandGroup[sdrtag], dtype)
        data = fsdr[sdsname][:]
        vmr.mend(data)
        # replacing in-place with mended data
        fsdr[sdsname].write_direct(data)
#        fsdr[sdsname][:] = data
      except Exception, e:
        log.info("Exception encountered replacing data:\n %s" % (e))
        continue # expect lots of exceptions, being naive for now and trying every sds on every file 
    fsdr.close()


if __name__ == "__main__":

  parser = _handle_args()
  options, args = parser.parse_args() 

  levels = [logging.ERROR, logging.WARN, logging.INFO, logging.DEBUG]
  verbosity = min(options.verbosity, len(levels))
  log_format = '%(asctime)s %(funcName)s %(lineno)s %(levelname)s: %(message)s'
  logging.basicConfig(level = levels[options.verbosity], format=log_format)

  if not len(args) == 1:
    print "Invalid arguments!"
    parser.print_help()
    exit(1)

  geofile = args[0]
  loopfiles(geofile)
