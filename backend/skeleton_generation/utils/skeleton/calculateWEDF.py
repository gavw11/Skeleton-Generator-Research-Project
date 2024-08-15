import copy

import numpy as np


def calculate_wedf(bma):
    def myDet(c1, c2):
        return np.linalg.det(
            np.array([[np.real(c1), np.imag(c1)], [np.real(c2), np.imag(c2)]])
        )

    def tri_area(c1, c2, c3):
        return abs(myDet(c3 - c1, c2 - c1)) / 2

    temp = copy.deepcopy(bma)
    temp.WEDFArray = np.inf * np.ones(len(temp.pointsArray))
    bma.WEDFArray = np.inf * np.ones(len(temp.pointsArray))

    indices_of_constrained_ends = temp.find_constrained_ends()

    indice_pts_boundary = temp.indexOfBndryPoints[indices_of_constrained_ends]
    num_indices_oce = len(indices_of_constrained_ends)

    for i in range(num_indices_oce):
        pt1 = temp.boundary[indice_pts_boundary[i, 0]]
        pt2 = temp.boundary[indice_pts_boundary[i, 1]]
        pt3 = temp.boundary[indice_pts_boundary[i, 2]]
        temp.WEDFArray[indices_of_constrained_ends[i]] = tri_area(pt1, pt2, pt3)

    bma.WEDFArray[indices_of_constrained_ends] = temp.WEDFArray[
        indices_of_constrained_ends
    ]

    smallest = np.min(temp.WEDFArray)
    index_of_smallest = np.argmin(temp.WEDFArray)

    end_loop = False

    while not end_loop:
        index_of_parent = np.where(temp.adjacencyMatrix[index_of_smallest])[0][0]
        assert (
            index_of_parent.shape[0] == 1
        ), f"Zero or more than one parent at index {index_of_smallest}. Make sure your graph is connected."

        temp = temp.remove_at_index(index_of_smallest)

        if index_of_smallest < index_of_parent:
            index_of_parent -= 1

        if len(np.where(temp.adjacencyMatrix[index_of_parent])[0]) == 1:
            pt1 = temp.boundary[temp.indexOfBndryPoints[index_of_parent, 0]]
            pt2 = temp.boundary[temp.indexOfBndryPoints[index_of_parent, 1]]
            pt3 = temp.boundary[temp.indexOfBndryPoints[index_of_parent, 2]]

            if temp.point_type[index_of_parent] != 3:
                temp.WEDFArray[index_of_parent] = smallest + tri_area(pt1, pt2, pt3)
            else:
                nubinds = np.where(
                    bma.adjacencyMatrix[
                        np.where(
                            np.isin(bma.pointsArray, temp.pointsArray[index_of_parent])
                        )
                    ]
                )[0]
                nubinds = nubinds[np.isinf(bma.WEDFArray[nubinds]) == False]
                nub_vals = np.sum(bma.WEDFArray[nubinds])
                temp.WEDFArray[index_of_parent] = tri_area(pt1, pt2, pt3) + nub_vals

            bma.WEDFArray[
                bma.pointsArray == temp.pointsArray[index_of_parent]
            ] = temp.WEDFArray[index_of_parent]

        smallest = np.min(temp.WEDFArray)
        index_of_smallest = np.argmin(temp.WEDFArray)

        if len(temp.pointsArray) == 1 or not temp.find_constrained_ends():
            bma.onMedialResidue = np.zeros(len(bma.pointsArray), dtype=bool)
            bma.onMedialResidue = np.isin(bma.pointsArray, temp.pointsArray)
            end_loop = True

    return bma
