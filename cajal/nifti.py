# coding=utf-8
#-------------------------------------------------------------------------------

#Author: Alexandre Manhaes Savio <alexsavio@gmail.com>
#Grupo de Inteligencia Computational <www.ehu.es/ccwintco>
#Universidad del Pais Vasco UPV/EHU
#
#2013, Alexandre Manhaes Savio
#Use this at your own risk!
#-------------------------------------------------------------------------------

import numpy as np
import nipy.core.image as niim
from nipy import save_image


def save_niigz(file_path, vol, affine=None, header=None):
    """Saves a volume into a Nifti (.nii.gz) file.

    Parameters
    ----------
    vol: Numpy 3D or 4D array
        Volume with the data to be saved.
    file_path: string
        Output file name path
    affine: 4x4 Numpy array
        Array with the affine transform of the file.
    header: nibabel.nifti1.Nifti1Header, optional
        Header for the file, optional but recommended.

    Note
    ----
        affine and header only work for numpy volumes.

    """
    if isinstance(vol, np.ndarray):
        log.debug('Saving numpy nifti file: ' + file_path)
        ni = nib.Nifti1Image(vol, affine, header)
        nib.save(ni, file_path)

    elif isinstance(vol, nib.Nifti1Image):
        log.debug('Saving nibabel nifti file: ' + file_path)
        nib.save(vol, file_path)

    elif isinstance(vol, niim.Image):
        log.debug('Saving nibabel nifti file: ' + file_path)
        save_image(vol, file_path)

