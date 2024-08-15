import numpy as np
from scipy.spatial import Delaunay


def nanoboys(XY0, sigma, Dt, Stop):
    XY = XY0.copy()
    j, m = XY.shape
    if np.all(XY[:, 0] == XY[:, m - 1]):
        XY = XY[:, :-1]
        m -= 1

    hop = 0.05
    mm = len(np.arange(-5, 5, hop))

    for run in range(Stop):
        for _ in range(20):
            XYe = np.column_stack((XY[:, m - 1], XY, XY[:, 0]))
            dXY = XYe[:, 1 : (m + 1)] - XYe[:, 0:m]
            mXY = (XYe[:, 0:m] + XYe[:, 2 : (m + 2)]) / 2

            Flow = mXY - XY
            h = np.sqrt(np.sum(Flow**2, axis=0) + np.finfo(float).eps)
            hh = np.row_stack((h, h))

            Nose = Flow / hh
            L = np.sqrt(np.sum(dXY**2, axis=0))
            Coke = np.sum(dXY[:, 1 : (m + 1)] * dXY[:, 0:m], axis=0) / (
                L[1 : (m + 1)] * L[0:m]
            )
            curv = (1 - Coke) / h

            WL = sigma * curv
            WLWL = np.row_stack((WL, WL))

            XY = XY + Dt / hh * WLWL * mXY
            XY = XY / (1 + Dt / hh * WLWL)

    return XY


def medial_axis(z):
    if np.sum((z.real - np.roll(z.real, -1)) * (z.imag + np.roll(z.imag, -1))) > 0:
        z = np.flipud(z)

    tri = np.sort(np.asarray(Delaunay(z.real, z.imag)).T, axis=1)

    u = z[tri[:, 0]]
    v = z[tri[:, 1]]
    w = z[tri[:, 2]]

    dot = (u - w) * np.conj(v - w)
    m = (u + v + 1j * (u - v) * dot.real / dot.imag) / 2
    r = np.abs(u - m)
    inside = dot.imag > 0

    triin = tri[inside, :]
    m = m[inside]
    r = r[inside]

    medial_data = np.column_stack((m, r, triin))
    return z, medial_data
