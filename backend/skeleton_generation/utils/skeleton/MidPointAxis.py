import matplotlib.pyplot as plt
import numpy as np
from calculate_medial_axis import calculate_medial_axis
from calculate_medial_order import calculate_medial_order
from scipy.spatial import ConvexHull

from skeleton_generation.utils.skeleton.BlumMedialAxis import BlumMedialAxis


class MidPointAxis:
    def __init__(self, boundary=None):
        self.boundary = boundary
        self.pointsArray = []
        self.radiiArray = []
        self.edgePointsArray = []
        self.EDFArray = []
        self.WEDFArray = []
        self.indexOfBndryPoints = []
        self.onMedialResidue = []
        self.adjacencyMatrix = []
        self.erosionThickness = []
        self.shapeTubularity = []
        self.pointType = []
        self.branchNumber = []
        self.branchAdjacency = []

        if boundary is not None:
            self.boundary, self.medialData = BlumMedialAxis.medial_axis(boundary)
            self.build_points(self.medialData)
            self.branchesforbma()
            self.calculate_WEDF()
            self.calculate_MidPointEDF()
            self.calculate_ETandST()

    def prune(self, et_ratio, st_threshold):
        area = np.polyarea(np.real(self.boundary), np.imag(self.boundary))
        et_threshold = et_ratio * np.sqrt(area)
        indices_to_remove = np.where(
            (self.EDFArray < et_threshold) | (self.EDFArray < st_threshold)
        )
        self.remove_at_index(indices_to_remove)

    def calculate_ETandST(self):
        self.erosionThickness = self.EDFArray - self.radiiArray
        self.shapeTubularity = 1 - self.radiiArray / self.EDFArray

    def get_length(self):
        return len(self.pointsArray)

    def remove_point(self, point):
        index = self.pointsArray.index(point)
        self.remove_at_index(index)

    def remove_at_index(self, index):
        point = self.pointsArray[index]
        self.remove_from_medial_data(point)
        del self.pointsArray[index]
        del self.edgePointsArray[index]
        del self.radiiArray[index]
        del self.EDFArray[index]
        del self.WEDFArray[index]
        del self.indexOfBndryPoints[index]
        del self.onMedialResidue[index]
        del self.erosionThickness[index]
        del self.shapeTubularity[index]
        self.adjacencyMatrix = np.delete(self.adjacencyMatrix, index, axis=0)
        self.adjacencyMatrix = np.delete(self.adjacencyMatrix, index, axis=1)
        del self.pointType[index]
        del self.branchNumber[index]

    def build_points(self, medial_data):
        mord = BlumMedialAxis.medial_order(medial_data)

        for i in range(len(mord)):
            point_a = mord[0, i]
            point_b = mord[1, i]
            index_a, self = self.find_or_add(medial_data, point_a)
            index_b, self = self.find_or_add(medial_data, point_b)

        self.adjacencyMatrix = np.zeros(
            (len(self.pointsArray), len(self.pointsArray)), dtype=bool
        )

        for i in range(len(mord)):
            index_m = self.pointsArray.index(mord[0, i])
            index_n = self.pointsArray.index(mord[1, i])
            self.adjacencyMatrix[index_m, index_n] = True
            self.adjacencyMatrix[index_n, index_m] = True

        self.edgePointsArray = np.zeros(len(self.pointsArray))
        self.onMedialResidue = np.full(len(self.pointsArray), np.inf)
        self.EDFArray = np.full(len(self.pointsArray), np.inf)
        self.WEDFArray = np.full(len(self.pointsArray), np.inf)
        self.erosionThickness = np.full(len(self.pointsArray), np.inf)
        self.shapeTubularity = np.full(len(self.pointsArray), np.inf)

    def find_or_add(self, medial_data, point):
        try:
            index = self.pointsArray.index(point)
        except ValueError:
            index_in_md = np.where(medial_data[:, 0] == point)[0]
            self.pointsArray.append(point)
            self.radiiArray.append(medial_data[index_in_md[0], 1])
            self.indexOfBndryPoints.append(medial_data[index_in_md[0], 2:5])
            index = len(self.pointsArray) - 1

        return index, self

    def plot_with_edges(self):
        fig, ax = plt.subplots()
        ax.plot(np.real(self.pointsArray), np.imag(self.pointsArray), "r*")
        for i, j in zip(*np.where(self.adjacencyMatrix)):
            if i < j:
                plt.plot(
                    [np.real(self.pointsArray[i]), np.real(self.pointsArray[j])],
                    [np.imag(self.pointsArray[i]), np.imag(self.pointsArray[j])],
                    "b-",
                )
        ax.axis("equal")
        plt.show()

    def plot_with_EDF(self):
        fig, ax = plt.subplots()
        l = len(self.pointsArray)
        mymin = np.min(self.EDFArray)
        mymax = np.max(self.EDFArray)
        for i in range(l):
            c1 = self.boundary[self.indexOfBndryPoints[i, 0]]
            c2 = self.boundary[self.indexOfBndryPoints[i, 1]]
            c3 = self.boundary[self.indexOfBndryPoints[i, 2]]
            ax.add_patch(
                plt.Polygon(
                    np.column_stack(
                        (
                            [np.real(c1), np.real(c2), np.real(c3)],
                            [np.imag(c1), np.imag(c2), np.imag(c3)],
                        )
                    ),
                    fill=False,
                    edgecolor="k",
                )
            )
            r = (self.EDFArray[i] - mymin) / (mymax - mymin)
            ax.plot(
                np.real(self.pointsArray[i]),
                np.imag(self.pointsArray[i]),
                "s",
                markeredgecolor="k",
                markerfacecolor=(r, 0, 1 - r),
                markersize=15,
            )
        self.plot_with_edges()
        ax.axis("equal")
        plt.show()

    def plot_with_WEDF(self):
        fig, ax = plt.subplots()
        l = len(self.pointsArray)
        mymin = np.min(self.WEDFArray)
        mymax = np.max(self.WEDFArray)
        for i in range(l):
            c1 = self.boundary[self.indexOfBndryPoints[i, 0]]
            c2 = self.boundary[self.indexOfBndryPoints[i, 1]]
            c3 = self.boundary[self.indexOfBndryPoints[i, 2]]
            r = (self.WEDFArray[i] - mymin) / (mymax - mymin)
            ax.add_patch(
                plt.Polygon(
                    np.column_stack(
                        (
                            [np.real(c1), np.real(c2), np.real(c3)],
                            [np.imag(c1), np.imag(c2), np.imag(c3)],
                        )
                    ),
                    fill=True,
                    facecolor=(r, 0, 1 - r),
                )
            )
        self.plot_with_edges()
        ax.axis("equal")
        plt.show()

    def find_constrained_ends(self):
        return np.where(np.sum(self.adjacencyMatrix, axis=1) == 1)

    @staticmethod
    def calculate_boundary(strawberry_pic):
        I1, I2, I3 = KMeansBerry(strawberry_pic)
        isolated_strawberry = GetBerries(I1, I2, I3)
        single_strawberry = SeparateBerries(isolated_strawberry)
        boundary = BorderBiggestArea(single_strawberry)
        boundary = sortpointsnew(boundary)
        boundary = boundary[:, 1]
        return boundary

    @staticmethod
    def calculate_conv_hull(strawberry_pic):
        I1, I2, I3 = KMeansBerry(strawberry_pic)
        isolated_strawberry = GetBerries(I1, I2, I3)
        single_strawberry = SeparateBerries(isolated_strawberry)
        boundary = BorderBiggestArea(single_strawberry)
        k = ConvexHull(np.column_stack((boundary.real, boundary.imag)))
        boundary = boundary[k.vertices]
        boundary = np.delete(boundary, 0)
        return boundary

    @staticmethod
    def medial_axis(boundary):
        z, medial_data = calculate_medial_axis(boundary)
        return z, medial_data

    @staticmethod
    def medial_order(medial_data):
        mord = calculate_medial_order(medial_data)
        i2 = np.where(mord[0, :] - mord[1, :] == 0)
        mord = np.delete(mord, i2, axis=1)
        mord2 = mord.copy()
        for k in range(mord2.shape[1]):
            dd = np.where(np.sum(mord - mord2[:, k][:, np.newaxis], axis=0) == 0)
            if dd[0].size >= 2:
                mord = np.delete(mord, dd[0][1:], axis=1)
        return mord

    def remove_from_medial_data(self, bma, point):
        bma.medial_data = bma.medial_data[np.where(bma.medial_data[:, 0] != point)]
