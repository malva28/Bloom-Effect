"""
autor: Valentina Garrido
"""

from colors import *
import numpy as np


def get_image_pixel_num(image_dims):
    return image_dims[0]*image_dims[1]


def in_image_bounds(pixel_index, image_dims):
    """
    Checks that pixel index is inside de dimensions of an image

    :param pixel_index: a tuple representing the row-column indices of a pixel
    :param image_dims: a tuple representing the number of rows and number of columns of an image
    :return: whether the pixel is in the image or not
    """
    if 0 <= pixel_index[0] and pixel_index[0] < image_dims[0]:
        if 0 <= pixel_index[1] and pixel_index[1] < image_dims[1]:
            return True
    return False


def get_img_max_luminance(img_mtrx, img_dims) -> float:
    """
    Scans through the whole image data looking for the max luminance value found in the image pixels
    :param img_mtrx: matrix with pixel data representing the image
    :param img_dims: a tuple representing the number of rows and number of columns of an image
    :return: the value of the max luminance found
    """
    max_lum = 0.
    for i in range(img_dims[0]):
        for j in range(img_dims[1]):
            current_color = img_mtrx[i][j][0:3]
            lum = rgb_luminance(current_color)
            if lum > max_lum:
                max_lum = lum
    return max_lum


def reinhard_image_mapping(img_mtrx, img_dims, max_lum, excluded_pixels = set()):
    """
    Applies Reinhard Mapping to all pixels of an image, except for those given in excluded_pixels.
    @see colors.reinhard_mapping

    :param img_mtrx: matrix with pixel data representing the image
    :param img_dims: a tuple representing the number of rows and number of columns of an image
    :param max_lum: max luminance to perform the mapping
    :param excluded_pixels: an iterable containing the indices of the pixels to exclude from mapping
    :return:
    """
    _hdr_to_ldr_image(img_mtrx, img_dims, reinhard_mapping, excluded_pixels, max_lum)


def clamp_image_colors(img_mtrx, img_dims, excluded_pixels=set()):
    """
    Applies simple clamping to all pixels of an image, except for those in excluded_pixels
    @see colors.clamp_color

    :param img_mtrx: matrix with pixel data representing the image
    :param img_dims: a tuple representing the number of rows and number of columns of an image
    :param excluded_pixels: an iterable containing the indices of the pixels to exclude from mapping
    :return:
    """
    _hdr_to_ldr_image(img_mtrx, img_dims, clamp_color, excluded_pixels)


def _hdr_to_ldr_image(img_mtrx, img_dims, mapping_function, excluded_pixels, *additional_args):
    """
    Maps pixels from an image in (possibly) hdr to ldr, except for those in excluded_pixels, using a
    mapping_function to convert individual pixels
    """
    for i in range(img_dims[0]):
        for j in range(img_dims[1]):
            if (i, j) not in excluded_pixels:
                current_color = img_mtrx[i][j][0:3]
                if len(additional_args) > 0:
                    new_mapped = mapping_function(current_color, *additional_args)
                else:
                    new_mapped = mapping_function(current_color)
                img_mtrx[i][j][0:3] = new_mapped


def convert_to_float_img(img_mtrx):
    """
    Since the library matplotlib.images handles most of the cases to transform image data
    to RGB (or RGBA) data, we only have to worry for the final output of the matrix, if its
    8-bit unsigned integer (uint8) or float.
    If it's integer, it gets converted to float. If it's float, the image is left as it is.

    :param img_mtrx: matrix with pixel data representing the image
    :return: image matrix of type float in range [0,1]
    """
    if img_mtrx.dtype == np.uint8:
        converted_img = img_mtrx.astype(np.float64)
        return converted_img/255
    else:
        return img_mtrx

