#!/usr/bin/env python
# encoding: utf-8
"""
Module for handling basic bowtie replacement on VIIRS granules.

Author: Nick Bearson, nickb@ssec.wisc.edu
Copyright (c) 2013 University of Wisconsin SSEC. All rights reserved.
"""


import numpy as np
from scipy import spatial

import logging
log = logging.getLogger(__name__)


MOD_RESOLUTION = 16   # Also functions as number of detectors
IMG_RESOLUTION = 32

MOD_TRIM_TABLE = [[1008, 2192],
                  [640 , 2560],
                  [0   , 3199],
                  [0   , 3199],
                  [0   , 3199],
                  [0   , 3199],
                  [0   , 3199],
                  [0   , 3199],
                  [0   , 3199],
                  [0   , 3199],
                  [0   , 3199],
                  [0   , 3199],
                  [0   , 3199],
                  [0   , 3199],
                  [640 , 2560],
                  [1008, 2192]]


IMG_TRIM_TABLE = [[2016, 4384],
                  [2016, 4384],
                  [1280, 5120],
                  [1280, 5120],
                  [0   , 6399],
                  [0   , 6399],
                  [0   , 6399],
                  [0   , 6399],
                  [0   , 6399],
                  [0   , 6399],
                  [0   , 6399],
                  [0   , 6399],
                  [0   , 6399],
                  [0   , 6399],
                  [0   , 6399],
                  [0   , 6399],
                  [0   , 6399],
                  [0   , 6399],
                  [0   , 6399],
                  [0   , 6399],
                  [0   , 6399],
                  [0   , 6399],
                  [0   , 6399],
                  [0   , 6399],
                  [0   , 6399],
                  [0   , 6399],
                  [0   , 6399],
                  [0   , 6399],
                  [1280, 5120],
                  [1280, 5120],
                  [2016, 4384],
                  [2016, 4384]]


class ViirsMender:
    """
    FIXME: doc
    """

    def __init__(self, lons, lats, res=MOD_RESOLUTION):
        """
    FIXME: doc
        """
        if res == MOD_RESOLUTION:
          self.TrimTable = MOD_TRIM_TABLE
          self.nDetectors = 16
          self.scanWidth = 3200
        elif res == IMG_RESOLUTION:
          self.TrimTable = IMG_TRIM_TABLE
          self.nDetectors = 32
          self.scanWidth = 6400
        else:
            raise RuntimeError, "res not recognized"

        rows, cols = lons.shape
        nscans = rows / self.nDetectors
        self.trimMask = self._createTrimArray(nscans)
        untrim_mask = np.invert(self.trimMask)

        xyz = self._ll2terra(lons, lats)

        bads = [a[self.trimMask] for a in xyz]
        goods = [a[untrim_mask] for a in xyz]

        log.info("Filling %s trimmed pixels from %s untrimmed pixels!" % (bads[0].shape, goods[0].shape))
      
        log.debug("Building the cKDTree...\n")
        paired_goods = np.dstack(goods)[0]
        paired_tree = spatial.cKDTree(paired_goods)
        paired_bads = np.dstack(bads)[0]

        log.debug("Querying the cKDTree...\n")
        q = paired_tree.query(paired_bads)
      
      
        log.debug("Query complete!\n")
      
        self.replaceDists = q[0]
        self.replaceLocs = q[1]


    def _ll2terra(self, lons, lats):
      """
        FIXME: doc
      """
      EARTH_RADIUS = 6378137  # meters
      rlats = np.deg2rad(lats)
      rlons = np.deg2rad(lons)
      x = EARTH_RADIUS * np.cos(rlats) * np.cos(rlons)
      y = EARTH_RADIUS * np.cos(rlats) * np.sin(rlons)
      z = EARTH_RADIUS * np.sin(rlats)
      return (x, y, z)


    def _createTrimArray(self, nscans=48, trimType=bool):
        """
            Creates an array with ndetectors*nscans pixel rows, with the trimmed
            pixels set to True.
        """
        trimScanArray = np.ones((self.nDetectors, self.scanWidth),dtype=trimType)
        for row in range(len(self.TrimTable)):
            trimScanArray[row,self.TrimTable[row][0]:self.TrimTable[row][1]] = False

        trimArray = np.ones((self.nDetectors*nscans, self.scanWidth),dtype=trimType)
        for scan in range(nscans):
            startRow = self.nDetectors * scan
            endRow = startRow + self.nDetectors
            trimArray[startRow:endRow,:] = trimScanArray

        return trimArray


    def mend(self, band):
        """
    FIXME: doc
        """
        untrim_mask = np.invert(self.trimMask)
        band[self.trimMask] = band[untrim_mask][self.replaceLocs]


