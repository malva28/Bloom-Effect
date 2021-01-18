"""
autor: Valentina Garrido
"""

from colors import within_eps_colors
from images import in_image_bounds, get_image_pixel_num
import numpy as np
import matplotlib.pyplot as plt


def diamond_mask(n: int) -> np.ndarray:
    """
    Returns the pixel offsets that will be applied to each pixel position to get
    their neighbors, distance norm 1.

    :param n: lenght of distance between the center and a corner of the diamond
    :return: array with the diamond shaped offsets
    """
    mask_size = 2*n*(n+1)
    mask = np.zeros((mask_size, 2), dtype=int)
    l = 0
    for i in range(-n, n + 1):
        k = n - abs(i)
        for j in range(-k, k + 1):
            if (i,j) != (0,0):
                mask[l,:] = (i, j)
                l += 1
    return mask


def create_empty_image_index_matrix(img_dims: tuple) -> np.ndarray:
    """
    Creates an empty array for holding pixel indices. It is first initialized with
    the max size it can have (the total pixels in the image) and filled with NaNs
    It is expected that the unused indices get cropped later

    :param img_dims: a tuple representing the number of rows and number of columns of an image
    :return: an array for holding indices
    """
    max_pix = get_image_pixel_num(img_dims)
    img_index_array = np.zeros((max_pix, 2), dtype=int)
    img_index_array.fill(np.nan)
    return img_index_array


def get_matching_pixel_indices(img_mtrx: np.ndarray, color_to_match: np.ndarray, img_dims: tuple) -> set:
    """
    Returns the set of pixel indices whose colors match the given color_to_match

    :param img_mtrx: matrix with image pixel data
    :param color_to_match: array representing the color
    :param img_dims: a tuple representing the number of rows and number of columns of an image
    :return: set of matching indices
    """
    delta = 0.001

    # the in operator for numpy arrays seems to be broken, so store cb pixels to check later their presence its better
    # to use a set, which performs the in operator in O(1)
    matching_indices = set()
    for i in range(img_dims[0]):
        for j in range(img_dims[1]):
            current_color = img_mtrx[i][j][0:3]
            if within_eps_colors(current_color, color_to_match, delta):
                matching_indices.add((i, j))
                # cb_indices.append((i, j)) # these indices are stored in row order
    return matching_indices


def get_neighbor_pixel_indices_norm_1(pixel_indices: set, img_dims: tuple, radius_n: int) -> set:
    """
    Returns a set of the pixels at most at radius_n pixels of distance (norm 1) from the pixels in pixel_indices

    :param pixel_indices: set of pixels to get the neighbors from
    :param img_dims: a tuple representing the number of rows and number of columns of an image
    :param radius_n: radius (norm 1) of the diamond that contains neighbors
    :return: set with neighbor indices
    """
    norm_1_mask = diamond_mask(radius_n)

    # neighbor_indices = []
    neighbor_indices = set()
    for pix_ind in pixel_indices:
        for t in norm_1_mask:
            neighbor_ind = (pix_ind[0] + t[0], pix_ind[1] + t[1])
            if in_image_bounds(neighbor_ind, img_dims):
                if neighbor_ind not in neighbor_indices and neighbor_ind not in pixel_indices:
                    # neighbor_indices.append(neighbor_ind)
                    neighbor_indices.add(neighbor_ind)
    return neighbor_indices


def simple_pixel_mapping(pixel_indices: list, len_pixels: int, sort=True):
    """
    Returns a dictionary assigning an integer to identify each pixel index in
    pixel_indices. If sort is enabled, it sorts the indices by row, then by column

    :param pixel_indices: a list containing the pixel indices
    :param len_pixels: int representing the lenght of the list
    :param sort: whether to sort or not
    :return: a dictionary mapping each index tuple to an integer
    """
    if sort:
        pixel_indices.sort()

    # Enumerating each unknown variable
    neighbor_dict = {}
    for i in range(len_pixels):
        neighbor_dict[pixel_indices[i]] = i
    return neighbor_dict


def spy_inds(ind_iterable, img_dims):
    """
    Plots the pixels in ind_iterable

    :param ind_iterable:
    :param img_dims:
    :return:
    """
    mtrx = np.zeros(img_dims)
    for ind in ind_iterable:
        mtrx[ind[0], ind[1]] = 1
    plt.spy(mtrx)
    plt.show()