import numpy as np


def calculate_midedf(bma):
    temp = bma.copy()
    indices_of_constrained_ends = temp.find_constrained_ends()
    indice_pts_boundary = temp.index_of_bndry_points[indices_of_constrained_ends]

    for i, (ind1, ind2, ind3) in enumerate(indice_pts_boundary):
        if (ind2 - ind1) * (ind3 - ind2) != 1:
            ind = sorted([ind1, ind2, ind3])
            if ind[0] == 1:
                myl = len(temp.boundary)
                assert ind[2] == myl - 1
                if ind[1] == 2:
                    ind1, ind2, ind3 = ind[2], ind[0], ind[1]
                else:
                    assert ind[1] == myl - 2
                    ind1, ind2, ind3 = ind[1], ind[2], ind[0]
            else:
                ind1, ind2, ind3 = ind
            indice_pts_boundary[i] = [ind1, ind2, ind3]

        pt1, pt2, pt3 = temp.boundary[ind1], temp.boundary[ind2], temp.boundary[ind3]
        mid_point = (pt1 + pt3) / 2
        temp.index_of_bndry_points[
            indices_of_constrained_ends[i]
        ] = indice_pts_boundary[i]
        temp.edge_points_array[indices_of_constrained_ends[i]] = mid_point
        temp.mid_length_array[indices_of_constrained_ends[i]] = np.linalg.norm(
            mid_point - pt1
        )
        temp.midedf_array[indices_of_constrained_ends[i]] = np.linalg.norm(
            mid_point - pt2
        )

    bma.index_of_bndry_points[indices_of_constrained_ends] = temp.index_of_bndry_points[
        indices_of_constrained_ends
    ]
    bma.edge_points_array[indices_of_constrained_ends] = temp.edge_points_array[
        indices_of_constrained_ends
    ]
    bma.mid_length_array[indices_of_constrained_ends] = temp.mid_length_array[
        indices_of_constrained_ends
    ]
    bma.midedf_array[indices_of_constrained_ends] = temp.midedf_array[
        indices_of_constrained_ends
    ]

    smallest, index_of_smallest = temp.midedf_array.min(), temp.midedf_array.argmin()
    end_loop = False

    while not end_loop:
        ind_s1, ind_s3 = temp.index_of_bndry_points[index_of_smallest, [0, 2]]
        edge_point = temp.edge_points_array[index_of_smallest]
        assert edge_point == (temp.boundary[ind_s1] + temp.boundary[ind_s3]) / 2

        index_of_parent = np.nonzero(temp.adjacency_matrix[index_of_smallest])[0]
        assert len(index_of_parent) == 1
        temp = temp.remove_at_index(index_of_smallest)

        if index_of_smallest < index_of_parent:
            index_of_parent -= 1

        ind_of_gd_parent = np.nonzero(temp.adjacency_matrix[index_of_parent])[0]

        if len(ind_of_gd_parent) == 1:
            # ... continue the rest of the code from the original function ...
            pass

        smallest, index_of_smallest = (
            temp.midedf_array.min(),
            temp.midedf_array.argmin(),
        )

        if len(temp.points_array) == 1 or len(temp.find_constrained_ends()) == 0:
            end_loop = True

    return bma
