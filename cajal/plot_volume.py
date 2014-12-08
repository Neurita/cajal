#!/usr/bin/env python

import os.path as op
import logging
from boyle.utils.filenames import get_extension

log = logging.getLogger(__name__)


def open_volume_file(filepath):
    """Open a volumetric file using the tools following the file extension.

    Parameters
    ----------
    filepath: str
        Path to a volume file

    Returns
    -------
    volume_data: np.ndarray
        Volume data

    pixdim: 1xN np.ndarray
        Vector with the description of the voxels physical size (usually in mm) for each volume dimension.

    Raises
    ------
    IOError
        In case the file is not found.
    """
    def open_nifti_file(filepath):
        from boyle.nifti.read import get_nii_data, get_nii_info
        vol_data = get_nii_data(filepath)
        hdr_data = get_nii_info(filepath)
        pixdim = hdr_data.pixdim
        return vol_data, pixdim

    def open_mhd_file(filepath):
        from boyle.mhd import load_raw_data_with_mhd
        vol_data, hdr_data = load_raw_data_with_mhd(filepath)
        pixdim = hdr_data['ElementSpacing']
        return vol_data, pixdim

    if not op.exists(filepath):
        raise IOError('Could not find file {}.'.format(filepath))

    ext = get_extension(filepath)
    if 'nii' in ext:
        try:
            return open_nifti_file(filepath)
        except:
            log.exception('Could not read {}.'.format(filepath))
            raise

    if 'mhd' in ext:
        try:
            return open_mhd_file(filepath)
        except:
            log.exception('Could not read {}.'.format(filepath))
            raise


class VolumeContainer(object):
    """This class is a container of 3D volumetric data with a few members to store metadata."""

    def __init__(self, vol_data, pixdim=None):
        self._voldata = vol_data
        self._pixdim = pixdim
        self._filepath = None

    @classmethod
    def from_file(cls, filepath):
        try:
            obj = cls(*open_volume_file(filepath))
            obj._filepath = filepath
            return obj
        except:
            log.exception('Could not open file {}.'.format(filepath))
            raise

    @property
    def shape(self):
        return self._voldata.shape

    @property
    def ndims(self):
        return self._voldata.ndim

    @property
    def pixdim(self):
        return self._pixdim

    def take_slice(self, slice_idx, axis=0):
        """Get one slice of the volume given its index and axis"""
        try:
            return self._voldata.take(slice_idx, axis=axis, mode='raise')
        except:
            log.exception('Could not get slice {} in axis {} from {}.'.format(slice_idx, axis, self._filepath))
            raise


class PlotVolume(VolumeContainer):
    """This class is a volume container with added information for visualization"""

    _cmap = None
    _opacity = 1
    _is_visible = True
    _axis = 0
    _slice = 0

    def __init__(self):
        self._cmap = None
        # self.type enum(gray, stats, fibers...)
        self._is_visible = True
        self._opacity = 1
        # self.

    def switch_visible(self):
        self.is_visible = not self.is_visible

    @property
    def is_visible(self):
        return self._is_visible

    @is_visible.setter
    def is_visible(self, value):
        if not isinstance(value, bool):
            raise ValueError('is_visible must be a boolean')
        self._is_visible = value

    def is_compatible(self, other):
        """Return True if self passes the compatibility check with other,
        False otherwise.

        Parameters
        ----------
        other: PlotVolume
            The other PlotVolume to compare with.
        """
        try:
            self.check_compatibility_with(other)
            return True
        except Exception as exc:
            return False

    def check_compatibility_with(self, other):
        """Check if self and other have the same shape, dimensionality and pixdim.
        Raise exception if any of these comparisons fail.

        Parameters
        ----------
        other: PlotVolume
            The other PlotVolume to compare with.

        Raises
        ------
        ValueError
            If ndim, shape or pixdim are different in self and other.
        """
        if self.ndims != other.ndims:
            raise ValueError('Number of dimensions {} and {} mismatch.'.format(self.ndims, other.ndims))
        if self.shape != other.shape:
            raise ValueError('Shapes {} and {} mismatch.'.format(self.shape, other.shape))
        if self.pixdim != other.pixdim:
            raise ValueError('Pixel dimensions {} and {} mismatch.'.format(self.pixdim, other.pixdim))

#
#
# class SlicyMainWindow(QtGui.QWidget):
#
#     def __init__(self, parent=None):
#         super(SlicyMainWindow, self).__init__(parent)
#         self.parent = parent
#         # set some general properties of the window
#         self.setWindowTitle("Slicy")
#         self.setMinimumSize(600, 400)
#
#         # Create sliceview Widget
#         self.sliceview = SliceView(self)
#
#         # layout GUI
#         vbox = QtGui.QVBoxLayout()
#         vbox.addWidget(self.sliceview)
#         self.setLayout(vbox)
#
#
# class SliceView(QtGui.QWidget):
#     """  This is the custom widget that does the slice drawing"""
#
#     def __init__(self, parent=None):
#         super(SliceView, self).__init__(parent)
#         self.parent = parent
#         self.pixmap = None
#
#     def paintEvent(self, event):
#         """ This should return immediately duh
#             Draw the pixmap the worker threads have been working on.
#         """
#         qp = QtGui.QPainter()
#         qp.begin(self)
#         if self.pixmap!=None:
#             qp.drawPixmap(0, 0, self.pixmap)
#         qp.end()
#
#     def restartRox(self):
#         """ This method restarts the iterative refinement of the slice image
#         It should be called whenever the slice-defining parameters change,
#         and whenever the size of the slice view widget changes.
#         should return immediately.
#         """
#         self.roxtimer = QtCore.QTimer(self)
#         self.connect(self.roxtimer, Qt.SIGNAL("timeout()"), self.addDetail);
#
#         # init some variables needed by the iterative refinement
#         self.timetopaint = time()
#         self.numdp = 0
#
#         # start the code!
#         self.roxtimer.start(0)
#
#     def addDetail(self):
#         """ This method does all the work
#         It takes the dimensional mapping and the slope, and requests data from the data service that
#         indicate what color to draw tiny rectangles on self.pixmap
#
#         Right now it just does 20 new data points eah time it's called, but a better strategy would
#         be to start with at least one and just work until 10ms has passed.
#         """
#         w = self.size().width()
#         h = self.size().height()
#
#         qp = QtGui.QPainter()
#         qp.begin(self.pixmap)
#         qp.setRenderHint(qp.Antialiasing,True)
#
#         # investigate new data points
#         stopworking = time()+0.01
#         while time() < stopworking:
#
#             locX = random()
#             locY = random()
#
#             # set up the hypothetical data point, and fill in the values we know
#             # (the two that are mapping to the x and y coordinates of this view
#             dat = [None]*self.sourceDimensionality
#             dat[self.dim[0]] = locX * self.slope[self.dim[0]]
#             dat[self.dim[1]] = locY * self.slope[self.dim[1]]
#             # ask the data service to fill in values for the three dimensions
#             # that correspond to red green an blue
#             dat = self.dataService.resolve(dat,self.dim[-3:])
#             # now use the retreived information to decide on the color
#             rgb = [dat[self.dim[k]] / self.slope[self.dim[k]] * 255 for k in [2,3,4]]
#             color = QtGui.QColor(*rgb)
#             # increment number of data points for following calculation
#             self.numdp += 1
#             # size of the box we will draw around this data point is equal to the area of the
#             # widget divided by the number of total data points already drawn including this one.
#             sqside = (float(w*h)/self.numdp)**0.5
#
#             # termination condition, once the size of the squares drawn is 0.25px, stop
#             if sqside < 0.25:
#                 self.roxtimer.stop()
#                 self.repaint()
#
#             # draw
#             qp.setPen(color)
#             qp.setBrush(color)
#             qp.drawRect(QtCore.QRectF(locX*w-sqside*0.5, locY*h-sqside*0.5, sqside, sqside))
#
#
#         qp.end()
#
#         if self.timetopaint <= time():
#             self.timetopaint = time() + 0.03
#             self.repaint()
#
#     def resizeEvent(self, event):
#         self.pixmap = QtGui.QPixmap(event.size().width(), event.size().height())
#         self.restartRox()
#
#
#
# app = Qt.QApplication(sys.argv)
# app.setApplicationName("High Dimensional Slice Viewer")
# widget = HDSV_Main()
# widget.show()
# app.exec_()
