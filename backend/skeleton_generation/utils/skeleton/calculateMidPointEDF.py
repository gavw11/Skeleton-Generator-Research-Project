import numpy as np


def calculate_mid_point_edf(bma):
    temp = bma.copy()
    indices_of_constrained_ends = temp.find_constrained_ends()
    indice_pts_boundary = temp.index_of_bndry_points[indices_of_constrained_ends]
    num_indices_oce = len(indices_of_constrained_ends)

    for i in range(num_indices_oce):
        ind1, ind2, ind3 = indice_pts_boundary[i]

        if (ind2 - ind1) * (ind3 - ind2) == 1:
            pass
        else:
            ind = sorted([ind1, ind2, ind3])
            if ind[0] == 1:
                if ind[1] == 2:
                    ind1, ind2, ind3 = ind[2], ind[0], ind[1]
                else:
                    ind1, ind2, ind3 = ind[1], ind[2], ind[0]
            else:
                ind1, ind2, ind3 = ind

            indice_pts_boundary[i] = [ind1, ind2, ind3]

        pt1 = temp.boundary[ind1]
        pt2 = temp.boundary[ind2]
        pt3 = temp.boundary[ind3]
        mid_point = (pt1 + pt3) / 2

        temp.index_of_bndry_points[
            indices_of_constrained_ends[i]
        ] = indice_pts_boundary[i]
        temp.edge_points_array[indices_of_constrained_ends[i]] = mid_point
        temp.radii_array[indices_of_constrained_ends[i]] = np.linalg.norm(
            mid_point - pt1
        )
        temp.edf_array[indices_of_constrained_ends[i]] = np.linalg.norm(mid_point - pt2)

    bma.index_of_bndry_points[indices_of_constrained_ends] = temp.index_of_bndry_points[
        indices_of_constrained_ends
    ]
    bma.edge_points_array[indices_of_constrained_ends] = temp.edge_points_array[
        indices_of_constrained_ends
    ]
    bma.radii_array[indices_of_constrained_ends] = temp.radii_array[
        indices_of_constrained_ends
    ]
    bma.edf_array[indices_of_constrained_ends] = temp.edf_array[
        indices_of_constrained_ends
    ]

    smallest, index_of_smallest = np.min(temp.edf_array), np.argmin(temp.edf_array)
    end_loop = False

    while not end_loop:
        ind_s1 = temp.index_of_bndry_points[index_of_smallest, 0]
        ind_s3 = temp.index_of_bndry_points[index_of_smallest, 2]
        edge_point = temp.edge_points_array[index_of_smallest]
        assert edge_point == (temp.boundary[ind_s1] + temp.boundary[ind_s3]) / 2

        index_of_parent = np.where(temp.adjacency_matrix[index_of_smallest])[0]
        assert (
            len(index_of_parent) == 1
        ), f"Zero or more than one parent at index {index_of_smallest}. Make sure your graph is connected."

        temp = temp.remove_at_index(index_of_smallest)
        if index_of_smallest < index_of_parent:
            index_of_parent -= 1

        ind_of_gd_parent = np.where(temp.adjacency_matrix[index_of_parent])[0]
        if len(ind_of_gd_parent) == 1:
            ind_p = temp.index_of_bndry_points[index_of_parent]
            o_p1 = np.where(ind_p == ind_s1)[0]
            o_p3 = np.where(ind_p == ind_s3)[0]

            if len(o_p1) == 1 and len(o_p3) == 1:
                ind_p = np.delete(ind_p, [o_p1, o_p3])
                ind_p1 = ind_p

                ind_gd_pt = temp.index_of_bndry_points[ind_of_gd_parent]
                o_gp1 = np.where(ind_gd_pt == ind_p1)[0]

                assert len(o_gp1) == 1

                o_gp3 = np.concatenate(
                    (np.where(ind_gd_pt == ind_s1)[0], np.where(ind_gd_pt == ind_s3)[0])
                )
                assert len(o_gp3) == 1

                ind_p3 = ind_gd_pt[o_gp3]

                if ind_p3 == ind_s3:
                    ind_p2 = ind_s1
                elif ind_p3 == ind_s1:
                    ind_p2 = ind_s3
                else:
                    print("oups, should not be here")

                temp.index_of_bndry_points[index_of_parent] = [ind_p1, ind_p2, ind_p3]
            else:
                print(
                    "pas trouve les extremites du segment du triangle smallest dans le triangle parent"
                )

            temp.edge_points_array[index_of_parent] = (
                temp.boundary[ind_p1] + temp.boundary[ind_p3]
            ) / 2
            temp.edf_array[index_of_parent] = smallest + np.linalg.norm(
                edge_point - temp.edge_points_array[index_of_parent]
            )
            temp.radii_array[index_of_parent] = np.linalg.norm(
                temp.edge_points_array[index_of_parent] - temp.boundary[ind_p1]
            )

            locind = np.where(bma.points_array == temp.points_array[index_of_parent])[0]

            bma.index_of_bndry_points[locind] = temp.index_of_bndry_points[
                index_of_parent
            ]
            bma.edge_points_array[locind] = temp.edge_points_array[index_of_parent]
            bma.edf_array[locind] = temp.edf_array[index_of_parent]
            bma.radii_array[locind] = temp.radii_array[index_of_parent]

            smallest, index_of_smallest = np.min(temp.edf_array), np.argmin(
                temp.edf_array
            )
            if len(temp.points_array) == 1 or not temp.find_constrained_ends():
                end_loop = True
    bma.points_array = bma.edge_points_array
