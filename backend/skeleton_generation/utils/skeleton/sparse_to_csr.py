import numpy as np


def sparse_to_csr(A, *args):
    retc = (nargout := len(args)) > 1
    reta = nargout > 2

    if len(args) > 0:
        if len(args) > 3:
            ncol = args[3]

        nzi = A
        nzj = args[0]

        if reta and len(args) > 1:
            nzv = args[1]

        if len(args) < 3:
            n = max(nzi)
        else:
            n = args[2]

        nz = len(A)

        if len(nzi) != len(nzj):
            raise ValueError(
                f"length of nzi ({nz}) not equal to length of nzj ({len(nzj)})"
            )

        if reta and len(args) < 2:
            raise ValueError("no value array passed for triplet input, see usage")

        if not np.isscalar(n):
            raise ValueError(
                "the 4th input to sparse_to_csr with triple input was not a scalar"
            )

        if len(args) < 4:
            ncol = max(nzj)
        elif not np.isscalar(ncol):
            raise ValueError(
                "the 5th input to sparse_to_csr with triple input was not a scalar"
            )
    else:
        n = A.shape[0]
        nz = A.nnz
        ncol = A.shape[1]
        retc = nargout > 1
        reta = nargout > 2

        if reta:
            nzi, nzj, nzv = A.nonzero()
        else:
            nzi, nzj = A.nonzero()

    if retc:
        ci = np.zeros(nz, dtype=int)
    if reta:
        ai = np.zeros(nz)

    rp = np.zeros(n + 1, dtype=int)

    for i in range(nz):
        rp[nzi[i] + 1] += 1

    rp = np.cumsum(rp)

    if not retc and not reta:
        rp += 1
        return rp

    for i in range(nz):
        if reta:
            ai[rp[nzi[i]] + 1] = nzv[i]

        ci[rp[nzi[i]] + 1] = nzj[i]
        rp[nzi[i]] += 1

    for i in range(n - 1, -1, -1):
        rp[i + 1] = rp[i]

    rp[0] = 0
    rp += 1

    if nargout > 1:
        return rp, ci, ai, ncol
    else:
        return rp
