import numpy as np


def dist(p, q):
    """Returns the Euclidean distance between two points."""
    return (sum((p-q)**2))**0.5


def orient(p1, p2, p3):
    """Compute the orientation of three points.

    Returns +1 if the points are in counterclockwise order, -1 if the points are
    in clockwise order, or 0 if the points are colinear.
    """
    d = np.linalg.det([np.append(p, 1) for p in [p1, p2, p3]])
    if d > 0:
        return 1
    elif d < 0:
        return -1
    else:
        return 0
