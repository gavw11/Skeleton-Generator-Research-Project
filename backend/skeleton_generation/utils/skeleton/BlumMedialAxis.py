import matplotlib.pyplot as plt  # ZG
import numpy as np

from skeleton_generation.utils.skeleton.branchesforbma import calculate_branches_for_bma
from skeleton_generation.utils.skeleton.calculate_medial_axis import calculate_medial_axis
from skeleton_generation.utils.skeleton.calculate_medial_order import calculate_medial_order
from skeleton_generation.utils.skeleton.calculateWEDF import calculate_wedf  # ZG
from scipy.ndimage import gaussian_filter1d

def gaussian_smoothing(boundary, sigma):
    return gaussian_filter1d(boundary, sigma=sigma)

def downsample(boundary, factor):
    return boundary[::factor]

class BlumMedialAxis:
    def __init__(self, init_boundary):
        if init_boundary is not None:
            smoothed_boundary = gaussian_smoothing(init_boundary, sigma=2)
            downsampled_boundary = downsample(smoothed_boundary, factor=5)
            boundary = downsampled_boundary
            self.boundary, self.medial_data = calculate_medial_axis(boundary)
            self.pointsArray = []  # Initialize pointsArray
            self.radiiArray = []  # Initialize radiiArray
            self.indexOfBndryPoints = []  # Initialize indexOfBndryPoints
            self.adjacencyMatrix = []  # Initialize adjacencyMatrix
            self.build_points(self.medial_data)
            # Initialize pointType attribute
            self.pointType = np.zeros(len(self.pointsArray))
            # self.branchNumber = None
            self.branchNumber = []  # ZG
            # Call branches_for_bma() method
            self.branches_for_bma()
            self.calculate_ET_and_ST()

    def prune(self, et_ratio, st_threshold):
        print("EDFArray:", self.EDFArray)   
        print("ShapeTubularity:", self.shapeTubularity)
        x_coords = np.real(self.boundary)
        y_coords = np.imag(self.boundary)

        area = 0.5 * np.abs(
            np.dot(x_coords, np.roll(y_coords, 1))
            - np.dot(y_coords, np.roll(x_coords, 1))
        )

        et_threshold = et_ratio * np.sqrt(area)
        print("ET Threshold:", et_threshold)

        indices_to_remove = [
            i
            for i, val in enumerate(self.EDFArray)
            if val < et_threshold or self.shapeTubularity[i] < st_threshold
        ]
        
        print("Indices to remove:", indices_to_remove)
        self.remove_at_index(indices_to_remove)
        print("Points after pruning:", self.pointsArray)


    def calculate_ET_and_ST(self):
        self.erosionThickness = [
            edf - radius for edf, radius in zip(self.EDFArray, self.radiiArray)
        ]
        self.shapeTubularity = [
            1 - radius / edf for radius, edf in zip(self.radiiArray, self.EDFArray)
        ]

    def get_length(self):
        return len(self.pointsArray)

    def remove_point(self, point):
        index = self.pointsArray.index(point)
        self.remove_at_index(index)

    def remove_at_index(self, indices):
        if not isinstance(indices, list):
            indices = [indices]

        for index in sorted(indices, reverse=True):
            point = self.pointsArray.pop(index)
            self.remove_from_medial_data(point)
            self.radiiArray.pop(index)
            self.EDFArray.pop(index)
            self.WEDFArray.pop(index)
            self.indexOfBndryPoints.pop(index)
            self.onMedialResidue.pop(index)
            self.erosionThickness.pop(index)
            self.shapeTubularity.pop(index)
            self.adjacencyMatrix.pop(index)
            for row in self.adjacencyMatrix:
                row.pop(index)
            self.pointType = np.delete(self.pointType, index)  # ZG
            self.branchNumber.pop(index)

    def build_points(self, medial_data):
        mord = self.medial_order(medial_data)
        for i in range(len(mord[0])):
            point_a = mord[0][i]
            point_b = mord[1][i]

            if point_a == point_b:
                index_a = self.find_or_add(medial_data, point_a)
            else:
                index_a = self.find_or_add(medial_data, point_a)
                index_b = self.find_or_add(medial_data, point_b)

        self.adjacency_matrix = [
            [False] * len(self.pointsArray) for _ in range(len(self.pointsArray))
        ]
        for i in range(len(mord[0])):
            index_m = self.pointsArray.index(mord[0][i])
            index_n = self.pointsArray.index(mord[1][i])

            self.adjacency_matrix[index_m][index_n] = True
            self.adjacency_matrix[index_n][index_m] = True

        inf = float("inf")
        self.onMedialResidue = [inf] * len(self.pointsArray)
        self.EDFArray = [inf] * len(self.pointsArray)
        self.WEDFArray = [inf] * len(self.pointsArray)
        self.erosionThickness = [inf] * len(self.pointsArray)
        self.shapeTubularity = [inf] * len(self.pointsArray)

    def find_or_add(self, medial_data, point):
        try:
            index = self.pointsArray.index(point)
        except ValueError:
            index = None

        index_in_md = [i for i, x in enumerate(medial_data[:, 0]) if x == point]

        dbp1 = 0
        dbp2 = 0

        if index is not None:
            bp1 = sorted(medial_data[index_in_md[0], 2:5])
            bp2 = sorted(self.indexOfBndryPoints[index])
            dbp1 = any([x != y for x, y in zip(bp1, bp2)])

            if len(index_in_md) >= 2:
                bp3 = sorted(medial_data[index_in_md[1], 2:5])
                dbp2 = any([x != y for x, y in zip(bp3, bp2)])

        if index is None or dbp1 or dbp2:
            self.pointsArray.append(point)
            self.radiiArray.append(medial_data[index_in_md[0], 1])

            if index is None or dbp1:
                self.indexOfBndryPoints.append(list(medial_data[index_in_md[0], 2:5]))
            else:
                self.indexOfBndryPoints.append(list(medial_data[index_in_md[1], 2:5]))

            index = len(self.pointsArray) - 1

        return index

    def branches_for_bma(self):
        return calculate_branches_for_bma(self)

    def plot_with_edges(self):
        figure1 = plt.figure()

        closed_boundary = np.concatenate((self.boundary, [self.boundary[0]]))
        plt.plot(
            np.real(closed_boundary),
            np.imag(closed_boundary),
            color="darkblue",
            linewidth=4.0,
        )

        # Plot self.pointsArray, separating real and imaginary parts
        plt.plot(np.real(self.pointsArray), np.imag(self.pointsArray), "r*", alpha=0)

        for i in range(len(self.pointsArray)):
            # Extract the real and imaginary parts for point i
            x = np.real(self.pointsArray[i])
            y = np.imag(self.pointsArray[i])
            for j in range(i + 1, len(self.pointsArray)):
                if self.adjacency_matrix[i][j]:
                    # Extract the real and imaginary parts for point j
                    x2 = np.real(self.pointsArray[j])
                    y2 = np.imag(self.pointsArray[j])
                    # Plot a line between point i and point j
                    plt.plot([x, x2], [y, y2], color="lightgreen")

        plt.axis("equal")
        return figure1

    def plot_with_edf(self):
        figure1 = plt.figure()
        l = len(self.pointsArray)
        mymin = min(self.EDFArray)
        mymax = max(self.EDFArray)

        for i in range(l):
            r = (self.EDFArray[i] - mymin) / (mymax - mymin)
            plt.gca().set_prop_cycle(None)
            plt.plot(
                np.real(self.pointsArray[i]),
                np.imag(self.pointsArray[i]),
                "-o",
                markeredgecolor="k",
                markerfacecolor=[r, 0, 1 - r],
                markersize=15,
            )
            for j in range(i + 1, len(self.pointsArray)):
                if self.adjacency_matrix[i][j]:
                    x = np.real(self.pointsArray[i])
                    y = np.imag(self.pointsArray[i])
                    x2 = np.real(self.pointsArray[j])
                    y2 = np.imag(self.pointsArray[j])
                    plt.plot([x, x2], [y, y2], "g-")

        plt.axis("equal")
        return figure1

    def plot_with_wedf(self):
        fig, ax = plt.subplots()
        calculate_wedf(self)  # ZG
        mymin = min(self.WEDFArray)
        mymax = max(self.WEDFArray)

        for i in range(len(self.pointsArray)):
            c1 = self.boundary[self.indexOfBndryPoints[i][0]]
            c2 = self.boundary[self.indexOfBndryPoints[i][1]]
            c3 = self.boundary[self.indexOfBndryPoints[i][2]]

            r = (self.WEDFArray[i] - mymin) / (mymax - mymin)
            ax.fill(
                [np.real(c1), np.real(c2), np.real(c3)],
                [np.imag(c1), np.imag(c2), np.imag(c3)],
                color=(r, 0, 1 - r),
                alpha=1,
            )

        for i in range(len(self.pointsArray)):
            for j in range(i + 1, len(self.pointsArray)):
                if self.adjacency_matrix[i][j]:
                    ax.plot(
                        [np.real(self.pointsArray[i]), np.real(self.pointsArray[j])],
                        [np.imag(self.pointsArray[i]), np.imag(self.pointsArray[j])],
                        "g-",
                    )
        plt.axis("equal")
        plt.show()

    def find_constrained_ends(self):
        return [i for i, row in enumerate(self.adjacency_matrix) if sum(row) == 1]

    @staticmethod
    def medial_axis(boundary):
        z, medial_data = calculate_medial_axis(boundary)
        return z, medial_data

    @staticmethod
    def medial_order(medial_data):
        mord = calculate_medial_order(medial_data)
        i2 = np.where(mord[0, :] - mord[1, :] == 0)[0]
        if i2.size > 0:
            for kk in range(len(i2)):
                index_in_md = np.where(medial_data[:, 0] == mord[0, i2[kk]])[0]
                bp1 = np.sort(medial_data[index_in_md[0], 2:5])
                bp2 = np.sort(medial_data[index_in_md[1], 2:5])
                dbp = np.any(bp1 != bp2)
                if not dbp:
                    mord = np.delete(mord, i2, axis=1)
        return mord

    def remove_from_medial_data(self, point):
        self.medial_data = self.medial_data[
            ~np.isin(self.medial_data[:, 0], point)
        ]  # ZG

