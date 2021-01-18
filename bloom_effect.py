"""
autor: Valentina Garrido
Main game module
"""

import matplotlib.image as mpimg
import argparse
import matplotlib.pyplot as plt

from scipy.sparse import csc_matrix
import scipy.sparse.linalg
import copy

import os


from colors import color_int_to_float
from images import get_img_max_luminance, reinhard_image_mapping, clamp_image_colors, convert_to_float_img
from imgIndices import get_matching_pixel_indices, spy_inds, get_neighbor_pixel_indices_norm_1, simple_pixel_mapping
from imgLaplaceSolver import build_equation_system


parser = argparse.ArgumentParser()
parser.add_argument("image_filename", help="Path to image that will be transformed")
parser.add_argument("N", help="Controls how far the bloom is spread (in pixels)", type=int)
parser.add_argument("R", help="Red component of color that will be bloomed (from 0 to 255)", type=int)
parser.add_argument("G", help="Green component of color that will be bloomed (from 0 to 255)", type=int)
parser.add_argument("B", help="Blue component of color that will be bloomed (from 0 to 255)", type=int)
parser.add_argument("--reinhard", help="Tells the program to use Reinhard mapping to convert HDR colors to LDR. "
                                           "If flag is not present, simple color clamping is used instead",
                        action="store_true")
#parser.add_argument("-o", "--outfile", help="Name of the transformed image file. Defaults to [image_filename]_out, "
#                                            "where [image_filename] is the filename given as argument. Format is "
#                                            "always png.")

if __name__ == '__main__':
    args = parser.parse_args()

    in_filename = args.image_filename

    # os.path.split divides the filename in the head, which contains the parent folders of the file and tail, which
    # contains the filename with it's extension
    (dir, filename) = os.path.split(in_filename)

    # os.path.splittext divides once more the filename into its name without extension and the extension.
    # This will be useful for generating the out filename
    (short_name, extension) = os.path.splitext(filename)

    out_filename = os.path.join(dir,short_name+"_out"+extension)
    #print(out_filename)

    np_img = mpimg.imread(args.image_filename)
    np_img = convert_to_float_img(np_img)
    img_dims = (np_img.shape[0], np_img.shape[1])

    cb_color = color_int_to_float([args.R, args.G, args.B])
    #cb_color = np.array([color_int_to_float(comp) for comp in [args.R, args.G, args.B]])
    delta = 0.001

    # It's better to store an index ref to the CB pixel, as we suppose that, most of the times,
    # there will be less pixels to bloom than pixels in total
    cb_indices = get_matching_pixel_indices(np_img, cb_color, img_dims)

    # Uncomment this to see the which pixels matched with the given cb pixel color
    # spy_inds(cb_indices, img_dims)

    # getting the neighbor pixels that will be the variables of the Laplace equation
    variable_indices = get_neighbor_pixel_indices_norm_1(cb_indices, img_dims, args.N)
    variable_indices = list(variable_indices)

    # once again, to see the position of the neighbors, uncomment this line
    # spy_inds(variable_indices, img_dims)

    # Enumerating each unknown variable
    n_vars = len(variable_indices)
    var_dict = simple_pixel_mapping(variable_indices, n_vars, sort=True)

    # creating the equation system with sparse matrices
    sparse_matrix, right_hand_side = build_equation_system(var_dict, n_vars, cb_indices, img_dims)

    # solving for each color component
    sol_R = scipy.sparse.linalg.spsolve(sparse_matrix, cb_color[0] * right_hand_side)
    sol_G = scipy.sparse.linalg.spsolve(sparse_matrix, cb_color[1] * right_hand_side)
    sol_B = scipy.sparse.linalg.spsolve(sparse_matrix, cb_color[2] * right_hand_side)

    # now, we sum these onto a new image
    out_image = copy.deepcopy(np_img)
    for var in var_dict:
        ind = var_dict[var]
        added_R = sol_R[ind]
        added_G = sol_G[ind]
        added_B = sol_B[ind]
        out_image[var[0], var[1]][0] += added_R
        out_image[var[0], var[1]][1] += added_G
        out_image[var[0], var[1]][2] += added_B

    # convert HDR pixel values to LDR
    if args.reinhard:
        max_lum = get_img_max_luminance(out_image, img_dims)
        reinhard_image_mapping(out_image, img_dims, max_lum, cb_indices)

    else:
        clamp_image_colors(out_image, img_dims)

    # uncomment these lines to see the image plotted
    # fig = plt.figure(figsize=(15, 10))
    # plt.imshow(out_image)
    # plt.show()

    # Save the result in a image
    mpimg.imsave(out_filename, out_image)

