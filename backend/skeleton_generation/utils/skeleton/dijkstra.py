import numpy as np

from utils.skeleton.sparse_to_csr import sparse_to_csr


def dijkstra(A, u):
    if isinstance(A, dict):
        rp = A["rp"]
        ci = A["ci"]
        ai = A["ai"]
        check = 0
    else:
        rp, ci, ai = sparse_to_csr(A)
        check = 1

    if check and np.any(ai) < 0:
        raise ValueError("Dijkstra's algorithm cannot handle negative edge weights.")

    n = len(rp) - 1
    d = np.inf * np.ones(n)
    T = np.zeros(n, dtype=int)
    L = np.zeros(n, dtype=int)
    pred = np.zeros(len(rp) - 1, dtype=int)
    n = 1
    T[n - 1] = u
    L[u] = n
    d[u] = 0

    while n > 0:
        v = T[0]
        ntop = T[n - 1]
        T[0] = ntop
        L[ntop] = 1
        n -= 1

        k = 1
        kt = ntop
        while True:
            i = 2 * k
            if i > n:
                break
            if i == n:
                it = T[i - 1]
            else:
                lc = T[i - 1]
                rc = T[i]
                it = lc
                if d[rc] < d[lc]:
                    i += 1
                    it = rc
            if d[kt] < d[it]:
                break
            else:
                T[k - 1] = it
                L[it] = k
                T[i - 1] = kt
                L[kt] = i
                k = i

        for ei in range(rp[v], rp[v + 1]):
            w = ci[ei - 1]
            ew = ai[ei - 1]
            if d[w] > d[v] + ew:
                d[w] = d[v] + ew
                pred[w] = v
                k = L[w]
                onlyup = 0
                if k == 0:
                    n += 1
                    T[n - 1] = w
                    L[w] = n
                    k = n
                    kt = w
                    onlyup = 1
                else:
                    kt = T[k - 1]

                while True and not onlyup:
                    i = 2 * k
                    if i > n:
                        break
                    if i == n:
                        it = T[i - 1]
                    else:
                        lc = T[i - 1]
                        rc = T[i]
                        it = lc
                        if d[rc] < d[lc]:
                            i += 1
                            it = rc
                    if d[kt] < d[it]:
                        break
                    else:
                        T[k - 1] = it
                        L[it] = k
                        T[i - 1] = kt
                        L[kt] = i
                        k = i

                j = k
                tj = T[j - 1]
                while j > 1:
                    j2 = j // 2
                    tj2 = T[j2 - 1]
                    if d[tj2] < d[tj]:
                        break
                    else:
                        T[j2 - 1] = tj
                        L[tj] = j2
                        T[j - 1] = tj2
                        L[tj2] = j
