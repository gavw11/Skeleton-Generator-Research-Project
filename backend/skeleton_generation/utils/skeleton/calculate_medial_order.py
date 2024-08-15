import numpy as np
from scipy.sparse import csr_matrix


def calculate_medial_order(medial_data):
    m2 = medial_data[:, 0]
    r2 = medial_data[:, 1]
    triin2 = np.column_stack(
        (
            medial_data[:, 2].real.astype(int),
            medial_data[:, 3].real.astype(int),
            medial_data[:, 4].real.astype(int),
        )
    )
    nt = triin2.shape[0]

    B1 = csr_matrix((np.ones(3 * nt), (np.repeat(np.arange(nt), 3), triin2.flatten())))
    B1_product = B1 @ B1.transpose()
    B1_dense = B1_product.toarray()  # Convert the sparse matrix to a dense array
    a1, b1 = np.where(B1_dense > 1)

    ind = a1 > b1
    a1 = a1[ind]
    b1 = b1[ind]

    mord = np.vstack((m2[a1], m2[b1]))
    return mord


print("#-1 runs")
