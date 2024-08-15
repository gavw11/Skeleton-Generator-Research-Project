from itertools import combinations
from typing import List

import numpy as np


def branchnew(mord, medial_data):
    if mord.shape[0] > 2:
        mord = mord.T

    regnodes = []
    trinodes = []
    branches = []

    i2 = np.where(mord[0] - mord[1] == 0)
    mord = np.delete(mord, i2, axis=1)
    mord2 = mord.copy()

    for k in range(mord2.shape[1]):
        dd = np.where(np.sum(np.abs(mord - mord2[:, k][:, None]), axis=0) == 0)
        if len(dd[0]) >= 2:
            mord = np.delete(mord, dd[0][1:], axis=1)

        dd = np.where(
            np.sum(np.abs(np.flipud(mord) - mord2[:, k][:, None]), axis=0) == 0
        )
        if len(dd[0]) >= 2:
            mord = np.delete(mord, dd[0][1:], axis=1)

    unique_list = np.unique(mord)

    for c1 in range(unique_list.shape[0]):
        i1, i2 = np.where(mord == unique_list[c1])

        if len(i1) >= 3:
            for c2 in range(len(i1)):
                if i1[c2] == 2:
                    mord2 = np.flipud(mord[:, i2[c2]])
                else:
                    mord2 = mord[:, i2[c2]]

                trinodes.append(mord2)
        else:
            for c3 in range(len(i1)):
                regnodes.append(mord[:, i2[c3]])

    trinodes = np.array(trinodes).T
    regnodes = np.array(regnodes).T

    for count in range(trinodes.shape[1]):
        i1, i2 = np.where(regnodes == trinodes[0, count])
        regnodes = np.delete(regnodes, i2, axis=1)

    regnodes2 = regnodes.copy()

    for k in range(regnodes.shape[1]):
        dd = np.where(np.sum(np.abs(regnodes - regnodes2[:, k][:, None]), axis=0) == 0)
        if len(dd[0]) >= 2:
            regnodes = np.delete(regnodes, dd[0][1:], axis=1)

    branchnubs = trinodes.copy()

    branches_list = []

    for d1 in range(trinodes.shape[1]):
        if trinodes[0, d1] != 0 or trinodes[1, d1] != 0:
            current = trinodes[:, d1][:, np.newaxis]
            j1, j2 = np.where(regnodes == current[-1, 0])

            while len(j1) != 0:
                if j1[0] == 0:
                    current = np.vstack([current, regnodes[1, j2]])
                else:
                    current = np.vstack([current, regnodes[0, j2]])

                regnodes = np.delete(regnodes, j2, axis=1)
                j1, j2 = np.where(regnodes == current[-1, 0])

            ii1, ii2 = np.where(trinodes == current[-1, 0])

            if len(ii1):
                current = np.vstack([current, trinodes[1, ii2[0]], trinodes[0, ii2[0]]])
                trinodes[:, ii2[0]] = [0, 0]

            if len(current) >= 2:
                branches_list.append(current.T)

    ranches_list = [branch for branch in branches_list if len(branch)]

    # remove any duplicate branches of length 2 from branchnubs
    dups = []
    normnubs = np.sum(branchnubs * branchnubs, 0)
    _, ii = np.unique(normnubs, return_index=True)
    duprows = np.setdiff1d(np.arange(normnubs.shape[0]), ii)

    for dupind in range(len(duprows)):
        duptest = branchnubs - np.flip(branchnubs[:, duprows[dupind]][:, np.newaxis], 0)
        duptestnorm = np.sum(duptest * duptest, 0)
        if 0 in duptestnorm:
            dups.append(duprows[dupind])

    if len(dups):
        branchnubs = np.delete(branchnubs, dups, axis=1)


def processbranches(
    branches: List[np.ndarray],
    branchnubs: np.ndarray,
    medialdata: np.ndarray,
    eps1: float,
    eps2: float,
    eps3: float,
):
    tanglenubs = np.abs(
        np.arctan(
            np.imag(branchnubs[0, :] - branchnubs[1, :])
            / np.real(branchnubs[0, :] - branchnubs[1, :])
        )
    )
    branchradii = np.zeros(branchnubs.shape)

    (numind1,) = np.where(np.isin(medialdata[:, 0], branchnubs[0, :]))
    entry = 0
    for j in range(len(numind1)):
        (tempind,) = np.where(np.isin(branchnubs[0, :], medialdata[numind1[j], 0]))
        branchradii[0, entry : entry + len(tempind)] = medialdata[numind1[j], 1]
        entry += len(tempind)

    (numind2,) = np.where(np.isin(medialdata[:, 0], branchnubs[1, :]))
    entry = 0
    for j in range(len(numind2)):
        (tempind,) = np.where(np.isin(branchnubs[1, :], medialdata[numind2[j], 0]))
        branchradii[1, entry : entry + len(tempind)] = medialdata[numind2[j], 1]
        entry += len(tempind)

    branchpointlist = np.unique(branchnubs[0, :])
    ind2join = []
    nubdiff = []

    for j in range(len(branchpointlist)):
        _, ind2 = np.where(branchnubs[0, :] == branchpointlist[j])
        nubpairs = np.array(list(combinations(ind2, 2)))
        testind = []

        for k in range(nubpairs.shape[0]):
            nubdiff_k = (
                np.abs(tanglenubs[nubpairs[k, 0]] - tanglenubs[nubpairs[k, 1]]) - np.pi
            )
            radiidiff_k = np.abs(
                branchradii[1, nubpairs[k, 0]] - branchradii[1, nubpairs[k, 1]]
            )

            if nubdiff_k < eps3 and radiidiff_k < eps2:
                testind.append(k)

        if len(testind) > 0:
            (i1,) = np.where(
                np.array([radiidiff_k for k in testind])
                == np.min([radiidiff_k for k in testind])
            )
            ind2join.append(nubpairs[testind[i1[0]]])

    branchnubnum = np.zeros(len(branchnubs[0]))
    for branchno in range(len(branches)):
        currentbranch = branches[branchno]
        branchnubnum[np.isin(branchnubs[1, :], currentbranch)] = branchno

    branchjoin = []

    if len(ind2join):
        ind2join = np.array(ind2join).T
        branchjoin = np.vstack(
            [branchnubnum[ind2join[0, :]], branchnubnum[ind2join[1, :]]]
        )
        branchjoin = branchjoin[:, np.argsort(branchjoin[0, :])]

    if branchjoin.size > 0:
        for j in range(branchjoin.shape[1] - 1, -1, -1):
            branches[int(branchjoin[0, j])] = np.unique(
                np.concatenate(
                    [branches[int(branchjoin[0, j])], branches[int(branchjoin[1, j])]]
                )
            )
            branches[int(branchjoin[1, j])] = []

    branches = [branch for branch in branches if len(branch) > 0]

    count = 0
    newbranch = []

    for branchno in range(len(branches)):
        if len(branches[branchno]) >= 3:
            branchr = medialdata[np.isin(medialdata[:, 0], branches[branchno]), 1]
            dv = np.abs(np.diff(np.unique(branches[branchno])))

            (newind,) = np.where(
                np.abs(-2 * branchr + np.roll(branchr, 1) + np.roll(branchr, -1) / dv)
                > eps1
            )
            newind = newind[~np.isin(newind, [0, len(branchr) - 1])]

            if len(newind) < 0.34 * len(branches[branchno]):
                for newbr in range(len(newind)):
                    count += 1
                    newbranch.append(branches[branchno][newind[newbr] :])
                    branches[branchno] = branches[branchno][: newind[newbr] + 1]

    processedbranches = branches + newbranch
