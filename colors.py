"""
autor: Valentina Garrido
"""

import numpy as np
from withinEps import within_eps


def color_component_int_to_float(rgb_component: int) -> float:
    """
    Converts a color component from integer to float

    :param rgb_component: a color component given in int range [0, 255]
    :return:  a color component in float range of [0,1]
    """
    return rgb_component / 255.0


def color_int_to_float(color) -> np.ndarray:
    """
    Converts a color array from integer to float

    :param color: an array containing color data in range [0, 255]
    :return: a numpy array with color data in range [0,1]
    """
    return np.array([color_component_int_to_float(comp) for comp in color])

def within_eps_colors(c1: np.ndarray, c2: np.ndarray, delta: float) -> bool:
    """
    Returns wether two colors are close enough to be considered the same.

    :param c1: a color to be compared
    :param c2: a color to be compared
    :param delta: tolerance of the operation. Less means more precision
    :return: True if the absolute value of all components is less than delta, False otherwise
    """
    num_of_components = len(c1)  # for now, only RGB is considered
    truth_array = [within_eps(c1[i], c2[i], delta) for i in
                   range(num_of_components)]  # evaluating for each RGB component
    total_true = sum(truth_array)  # each time the condition holds, it sums 1
    if total_true == len(truth_array):  # every component must be close to be true
        return True
    else:
        return False


def clamp_color(hdr_color: np.ndarray) -> np.ndarray:
    """
    Clamps a color component to 1.0 if it exceeds 1.0

    :param hdr_color: a color that's (possibly) in high dynamic range (hdr)
    :return: a clamped color in low dynamic range (ldr)
    """
    # This code uses Python list compressions. Inefficient
    # return np.array([1.0 if hdr_color[i] > 1.0 else hdr_color[i] for i in range(len(hdr_color))])

    # This one uses cool properties of numpy
    hdr_color[hdr_color > 1.0] = 1.0
    return hdr_color


def rgb_luminance(color: np.ndarray):
    """
    Returns a value representing the luminance of a color.
    See https://en.wikipedia.org/wiki/Relative_luminance

    :param color: a color
    :return: a float representing luminance
    """
    lum_coef = np.array([0.2126, 0.7152, 0.0722])
    return np.dot(color, lum_coef)


def change_luminance(old_color: np.ndarray, new_lum: float) -> np.ndarray:
    """
    Changes luminance of color to new_lum by a simple proportion relation
    If the old luminance is near zero, the color is not transformed and simply returned

    :param old_color: a color
    :param new_lum: the float value of the new luminance
    :return: the color with the new luminance
    """
    old_lum = rgb_luminance(old_color)
    if within_eps(old_lum, 0., 0.001):
        return old_color
    else:
        new_color = old_color * (new_lum / old_lum)
        return new_color


def reinhard_mapping(hdr_color: np.ndarray, max_lum: float) -> np.ndarray:
    """
    Maps a color in (possibly) high dynamic range to low dynamic range using Reinhard Mapping
    a value of max luminance is needed to convert to ldr relative to that value
    More info on Reinhard Mapping: https://64.github.io/tonemapping/

    :param hdr_color: color to be transformed
    :param max_lum: max luminance to perform the mapping
    :return: resulting color in ldr
    """
    old_lum = rgb_luminance(hdr_color)
    factor = old_lum * (1+(old_lum / max_lum**2))
    new_lum = factor/(1+old_lum)
    mapped_color = change_luminance(hdr_color, new_lum)
    ldr_color = clamp_color(mapped_color) # in case there are decimal reminders from last operations
    return ldr_color
