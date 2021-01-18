"""
autor: Valentina Garrido
"""

from images import in_image_bounds
from scipy.sparse import csc_matrix
import numpy as np



class SparseData:
    """
    Simple object to store data of a sparse matrix
    """
    def __init__(self, shape: tuple):
        """
        Constructor

        :param shape: dimentions to use when converting this to sparse matrix
        """
        self.sparse_rows = []
        self.sparse_cols = []
        self.sparse_values = []
        self.shape = shape

    def add_entry(self, row: int, col: int, value: float):
        """
        Adds row-column-value triplet data to object

        :param row: row position
        :param col: column position
        :param value: value
        """
        self.sparse_rows.append(row)
        self.sparse_cols.append(col)
        self.sparse_values.append(value)

    def len_non_zero_entries(self) -> int:
        """
        Counts how many sparse data have been added so far
        :return: length of the sparse values
        """
        return len(self.sparse_values)

    def get_sparse_matrix(self):
        """
        Converts stored data to sparse matrix object
        :return: a csc_matrix corresponding to sparse data
        """
        return csc_matrix((self.sparse_values, (self.sparse_rows, self.sparse_cols)),
                   shape=(self.shape))



def var_coefficients(var_ind, var_dict, cb_indices, img_dims):
    coefs = [[1, 1], [1, 1]]
    coef_weight(var_ind, var_dict, cb_indices, img_dims, coefs, True, True)
    coef_weight(var_ind, var_dict, cb_indices,img_dims, coefs, True, False)
    coef_weight(var_ind, var_dict, cb_indices,img_dims, coefs, False, True)
    coef_weight(var_ind, var_dict, cb_indices,img_dims, coefs, False, False)
    return coefs


def coef_weight(var_ind, var_dict, cb_indices, img_dims, coefs, is_left_right, is_bigger):
    """
    Assigns the corresponding coefficient to a contiguous variable that will have in the matrix of the equation system.

    :param var_ind:
    :param var_dict:
    :param cb_indices:
    :param img_dims:
    :param coefs:
    :param is_left_right:
    :param is_bigger:
    :return:
    """
    contiguous_var = get_contiguous_var(var_ind, is_left_right, is_bigger)
    if not in_image_bounds(contiguous_var, img_dims):
        coefs[is_left_right][is_bigger] = 0
        coefs[is_left_right][not is_bigger] = 2 * coefs[is_left_right][not is_bigger]
    # third case: the contiguous variable is a border condition point. The coefficient gets marked with a -1
    elif contiguous_var in cb_indices:
        coefs[is_left_right][is_bigger] = -1 * coefs[is_left_right][is_bigger]
    elif not var_dict.get(contiguous_var):
        coefs[is_left_right][is_bigger] = 0


def get_contiguous_var(var_ind, is_left_right, is_bigger):
    """
    Gets the variable index that is either left, right, down or up of var_ind.
    To get left var index: is_left_right must be True and is_bigger False
    To get right var index: is_left right must be True and is_bigger True
    To get down var index: is_left_right must be False and is_bigger False
    To get up var index: is_left_right must be False and is_bigger True

    :return: the index of the contiguous variable
    """

    side_offset = is_left_right * (-1) ** (1+is_bigger)
    vertical_offset = (not is_left_right) * (-1) ** (1+is_bigger)

    contiguous_var = (var_ind[0] + side_offset, var_ind[1] + vertical_offset)
    return contiguous_var


def build_equation_system(variable_dict, n_vars, cb_indices, img_dims):
    sparse_data = SparseData((n_vars, n_vars))
    right_hand_side = np.zeros(n_vars)

    for var in variable_dict:
        diag_val = variable_dict[var]
        sparse_data.add_entry(diag_val, diag_val, -4) # value of the current u_ij is multiplied by -4

        # there are three cases: either a contiguous variable is out of bounds, in which case the stencil is reduced by
        # one point (they are not five anymore) and the opposite variable weights 2, or the variable is within the
        # bounds of the image, but outside the blooming range, in which case is weighed 0 and not added to the matrix
        # the third case happens when the contiguous variable is a border condition point

        coefs = var_coefficients(var, variable_dict, cb_indices, img_dims)
        for i in range(len(coefs)):
            c_list = coefs[i]
            for j in range(len(c_list)):
                c = c_list[j]
                if c < 0:
                    right_hand_side[diag_val] += c
                elif c > 0:
                    contiguous_var = get_contiguous_var(var, i, j)
                    sparse_data.add_entry(diag_val, variable_dict.get(contiguous_var), c)

    sparse_matrix = sparse_data.get_sparse_matrix()
    return sparse_matrix, right_hand_side