#!/usr/bin/env python
# encoding: utf-8
"""
Author: Nick Bearson, nickb@ssec.wisc.edu
Copyright (c) 2013 University of Wisconsin SSEC. All rights reserved.
"""

import os
import re

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


def test(dir):
  geo = ""
  band = ""
  for f in os.listdir(dir):
    tag = f[:5]
    if tag in ViirsGeoGroup.keys():
      geo = dir + f
    elif tag in ViirsBandGroup.keys():
      band = dir + f
    else:
      continue

  geodate = re.search(r".*_npp_(d\d{8}_t\d{7})", geo).group(1)
  banddate = re.search(r".*_npp_(d\d{8}_t\d{7})", band).group(1)
  if geodate != banddate:
    raise RuntimeError, "   %s\n and \n    %s\n don't match!" % (geo, band)

  get_grid(geo, band)


def get_grid(geo, band):

  print geo
  print band

  fgeo = h5py.File(geo)
  fband = h5py.File(band)
  fout = h5py.File("outdata" + ".h5", 'w')

  geotag = os.path.basename(geo)[:5]
  bandtag = os.path.basename(band)[:5]

  lats = fgeo["%s/Latitude"  % ViirsGeoGroup[geotag]][:]
  lons = fgeo["%s/Longitude" % ViirsGeoGroup[geotag]][:]
  rads = fband["%s/Radiance" % ViirsBandGroup[bandtag]][:]
#  scale, offset = fband["%s/RadianceFactors" % ViirsBandGroup[bandtag]][:]
#  rads = (rads * scale) + offset

  vmr = vm.ViirsMender(lons, lats, vm.MOD_RESOLUTION)
  rads_fixed = np.copy(rads)
  vmr.mend(rads_fixed)

  test_plot(rads, "rads_orig")
  fout.create_dataset("rads", rads.shape, data=rads)

  test_plot(rads_fixed, "rads_fixed")
  fout.create_dataset("rads_fixed", rads_fixed.shape, data=rads_fixed)

  test_plot(vmr.trimMask, "trim_mask")

  ny, nx = lats.shape
  x = np.linspace(0, nx, nx)
  y = np.linspace(0, ny, ny)

  xv, yv = np.meshgrid(x, y)

  xvc = np.copy(xv)
  vmr.mend(xvc)
  xvd = xvc - xv
  test_plot(xvd, "xvd")
  fout.create_dataset("xvd", xvd.shape, data=xvd)

  yvc = np.copy(yv)
  vmr.mend(yvc)
  yvd = yvc - yv
  test_plot(yvd, "yvd")
  fout.create_dataset("yvd", xvd.shape, data=yvd)

  untrim_mask = np.invert(vmr.trimMask)

  indices = np.zeros(vmr.trimMask.shape)
  indices[vmr.trimMask] = vmr.replaceLocs
  test_plot(indices, "indices")

  dists = np.zeros(vmr.trimMask.shape)
  dists[vmr.trimMask] = vmr.replaceDists
  test_plot(dists, "dists")

  lats_fixed = np.copy(lats)
  vmr.mend(lats_fixed)
  test_plot(lats_fixed, "fixedlats")

  lons_fixed = np.copy(lons)
  vmr.mend(lons_fixed)
  test_plot(lons_fixed, "fixedlons")

  fout.close()


def test_plot(data, saveas):
  import matplotlib.pyplot as plt
  import matplotlib as mpl

  figsize = (np.array(data.shape)/100.0)[::-1]
#  figsize = (np.array(data.shape))[::-1]
  mpl.rcParams.update({'figure.figsize':figsize})

  fig = plt.figure(figsize=figsize)
  fig.set_size_inches(figsize)

#  plot = plt.imshow(data, vmin=0, vmax=1)
  plot = plt.imshow(data)
  plt.colorbar()
  plt.savefig(saveas + ".png")

  plt.clf()


if __name__ == "__main__":
  import logging
  LOG_LEVEL = logging.DEBUG
  LOG_FORMAT = '%(asctime)s %(funcName)s %(lineno)s %(levelname)s: %(message)s'
  logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)

  import sys
  dir = sys.argv[1]

  test(dir)
