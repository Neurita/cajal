# -*- coding: utf-8 -*-

import logging
import numpy as np

from .plot_volume import PlotVolume

log = logging.getLogger(__name__)


class PlotVolumeStack(object):
    """A stack of PlotVolumes for overlapping volume slice plots"""

    vols = []
    cut_point = np.zeros(3)
    vol_type = PlotVolume

    def __init__(self):
        self.cut_points = np.zeros(3, dtype=int)

    def add_volume(self, plot_volume):
        """Add one PlotVolume to the plot stack

        Parameters
        ----------
        plot_volume: slicy.plot_volume.PlotVolume
        """
        # check if volume has same metadata as other volumes in self
        if self.vols:
            try:
                plot_volume.check_compatibility_with(self.vols[0])
            except:
                raise
        else:
            self.vols.append(plot_volume)

    def add_from_file(self, filepath):
        """Add one volume to the plot stack from the file path.

        Parameters
        ----------
        filepath: str
            Path to a volume file
        """
        self.add_volume(self.vol_type.from_file(filepath))