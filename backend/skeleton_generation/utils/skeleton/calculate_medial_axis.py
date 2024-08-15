import numpy as np
from scipy.spatial import Delaunay


def calculate_medial_axis(z):
    if (
        np.sum(
            (np.real(z) - np.roll(np.real(z), -1))
            * (np.imag(z) + np.roll(np.imag(z), -1))
        )
        > 0
    ):
        z = np.flipud(z)

    points = np.column_stack((np.real(z), np.imag(z)))
    delaunay = Delaunay(points)
    tri = np.sort(delaunay.simplices, axis=1)

    u = z[tri[:, 0]]
    v = z[tri[:, 1]]
    w = z[tri[:, 2]]

    dot = (u - w) * np.conj(v - w)
    m = (u + v + 1j * (u - v) * np.real(dot) / np.imag(dot)) / 2
    r = np.abs(u - m)
    inside = np.imag(dot) > 0

    triin = tri[inside]
    m = m[inside]
    r = r[inside]

    medial_data = np.column_stack((m, r, triin))
    return z, medial_data


print("#0 runs")
