import numpy as np


def dist(p, q):
    return (sum((p-q)**2))**0.5


def orient(*points):
    """Compute the orientation of three points."""
    d = np.linalg.det([np.append(p, 1) for p in points])
    if d > 0:
        return 1
    elif d < 0:
        return -1
    else:
        return 0
