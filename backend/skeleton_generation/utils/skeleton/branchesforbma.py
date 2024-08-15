from itertools import combinations

import numpy as np
from scipy.sparse.csgraph import shortest_path  # ZG

# there are many shortest paths - https://docs.scipy.org/doc/scipy/reference/generated/scipy.sparse.csgraph.shortest_path.html


def calculate_branches_for_bma(bma):
    n_points = len(bma.pointsArray)
    bma.branchNumber = np.zeros((n_points, n_points))
    adjacency_sum = np.array([sum(row) for row in bma.adjacencyMatrix])  # ZG

    # ZG
    bma.pointType = np.zeros(n_points)
    bma.pointType[adjacency_sum >= 3] = 3
    bma.pointType[adjacency_sum == 1] = 1
    bma.pointType[adjacency_sum == 2] = 0

    # ZG
    triple_adjacents_mask = bma.pointType == 3

    bma.adjacencyMatrix = np.array(bma.adjacencyMatrix)

    # ZG
    triple_adjacents = np.where(triple_adjacents_mask)[0]

    # ZG
    bma.pointType[triple_adjacents[bma.pointType[triple_adjacents] == 0]] = 2
    bma.pointType[triple_adjacents[bma.pointType[triple_adjacents] == 1]] = 4
    triplepoint = np.where(np.isin(bma.pointType, [3]))[0]
    singlepoint = np.where(np.isin(bma.pointType, [1]))[0]
    nubpoint = np.where(np.isin(bma.pointType, [2]))[0]

    nubcount = np.ones(len(nubpoint))
    branches = []

    # case 0: single branch (no triple points)
    if len(triplepoint) == 0:
        branchno = 1
        if len(singlepoint) > 0:  # ZG
            dist, pred = shortest_path(bma.adjacencyMatrix, singlepoint[0])
            predpath = pred
            bpath = [singlepoint[1]]
            u = singlepoint[1]
            while u != singlepoint[0]:
                u = predpath[u]
                bpath.append(u)
            branches.append(bpath)

    # case 1: single points adjacent to triple points

    # ZG
    adjacency_matrix_2d = np.atleast_2d(bma.adjacencyMatrix)
    startpt1, endpt1 = np.where(adjacency_matrix_2d[triplepoint, :][:, singlepoint])

    for branchno in range(len(startpt1)):
        branches.append(
            [triplepoint[startpt1[branchno]], singlepoint[endpt1[branchno]]]
        )  # ZG

    # case 2: triple points adjacent to triple points
    startpt2, endpt2 = np.where(
        adjacency_matrix_2d[triplepoint, :][:, triplepoint]
    )  # ZG
    ind = startpt2 < endpt2
    startpt2, endpt2 = startpt2[ind], endpt2[ind]
    startind = len(branches)
    for branchno in range(startind, len(startpt2) + startind):
        branches.append(
            [
                triplepoint[startpt2[branchno - startind]],
                triplepoint[endpt2[branchno - startind]],
            ]
        )

    # case 3: single points not adjacent to triple points
    predpath = {}
    dists = np.inf * np.ones((len(triplepoint), len(singlepoint)))

    for ll in range(len(singlepoint)):
        dist, pred = shortest_path(bma.adjacencyMatrix, singlepoint[ll])  # ZG
        dists[:, ll] = dist[triplepoint]
        predpath[ll] = pred

    badinds = np.where(np.any(np.isinf(dists), axis=0))[0]
    dists = np.delete(dists, badinds, axis=1)
    singlepoint = np.delete(singlepoint, badinds)
    predpath = {k: v for k, v in predpath.items() if k not in badinds}

    # ZG
    if dists.size > 0:
        _, endpts3 = np.min(dists, axis=0)
        branchstarts = triplepoint[endpts3]
        bpath = []
        startind = len(branches)

        for branchno in range(startind, len(endpts3) + startind):
            bpath = [branchstarts[branchno - startind]]
            u = branchstarts[branchno - startind]
            while u != singlepoint[branchno - startind]:
                u = predpath[branchno - startind][u]
                bpath.append(u)
            branches.append(bpath)
            nubcount[np.isin(nubpoint, bpath)] = 0
    else:
        endpts3 = []
        branches = []

    # case 4: triple point to triple point via multiple regular points
    predpath = {}
    nubpoint2 = nubpoint[nubcount.astype(bool)]
    longbranch = np.zeros(len(nubpoint2), dtype=int)
    tempadjacency = bma.adjacencyMatrix.copy()

    tempadjacency = np.atleast_2d(tempadjacency)  # ZG

    tempadjacency[
        np.ix_(np.where(bma.pointType == 3)[0], np.where(bma.pointType == 3)[0])
    ] = 0  # ZG

    # subcase a: triple, regular, triple branch
    for ll in range(len(nubpoint2)):
        if not np.any(tempadjacency[nubpoint2[ll], :]):
            longbranch[ll] = 0
            tripnbrs = np.where(bma.adjacencyMatrix[nubpoint2[ll], :])[0]
            branches.append([tripnbrs[0], nubpoint2[ll], tripnbrs[1]])
            nubcount[np.isin(nubpoint, branches[-1])] = 0
        else:
            longbranch[ll] = 1

    # subcase b: triple, multiple regulars, triple
    if np.any(longbranch):
        nubpoint2 = nubpoint[nubcount.astype(bool)]
        dists = np.inf * np.ones((len(nubpoint2), len(nubpoint2)))

        for ll in range(len(nubpoint2)):
            dist, pred = shortest_path(tempadjacency, nubpoint2[ll])
            dists[:, ll] = dist[nubpoint2]
            predpath[ll] = pred

        dists[dists == 0] = np.inf
        dists4, endpts4 = np.min(dists, axis=0)
        idx = np.where(np.arange(len(endpts4)) > endpts4)[0]
        branchstarts = nubpoint2[endpts4[idx]]
        branchends = nubpoint2[idx]
        bpath = []
        startind = len(branches)

        for branchno in range(startind, len(branchstarts) + startind):
            triplestart = triplepoint[
                np.isin(
                    triplepoint,
                    np.where(bma.adjacencyMatrix[branchends[branchno - startind], :]),
                )
            ]

            if len(triplestart) == 1:
                bpath = [
                    triplepoint[
                        np.isin(
                            triplepoint,
                            np.where(
                                bma.adjacencyMatrix[
                                    branchstarts[branchno - startind], :
                                ]
                            ),
                        )[0]
                    ],
                    branchstarts[branchno - startind],
                ]
                u = branchstarts[branchno - startind]
                while u != branchends[branchno - startind]:
                    u = predpath[idx[branchno - startind]][u]
                    bpath.append(u)
                bpath.append(
                    triplepoint[
                        np.isin(triplepoint, np.where(bma.adjacencyMatrix[u, :]))[0]
                    ]
                )
            elif len(triplestart) == 2:
                bpath = [
                    triplestart[0],
                    branchends[branchno - startind],
                    triplestart[1],
                ]

            branches.append(bpath)

    # Insert branch point order number into column with index = branchno
    for branchno in range(len(branches)):
        orderind = np.arange(1, len(branches[branchno]) + 1)
        bma.branchNumber[branches[branchno], branchno] = orderind

    # Remove extra columns from bma.branchNumber
    bma.branchNumber = bma.branchNumber[:, np.sum(bma.branchNumber, axis=0) != 0]

    # Create branch adjacency matrix
    bma.branchAdjacency = np.zeros(
        (bma.branchNumber.shape[1], bma.branchNumber.shape[1])
    )

    for ind in range(len(bma.pointsArray)):
        # ZG
        branchind = np.where(bma.branchNumber[ind, :])[0]

        if len(branchind) >= 2:
            adjind = list(combinations(branchind, 2))
            for ind2 in range(len(adjind)):
                bma.branchAdjacency[adjind[ind2][0], adjind[ind2][1]] = 1
                bma.branchAdjacency[adjind[ind2][1], adjind[ind2][0]] = 1
