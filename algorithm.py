from typing import List, Sequence, Tuple
from graph import Graph, Vertex


def flip_between(g: Graph, ai: int, bi: int):
    """Transform the given graph's triangulation such that an edge between a and b exists.

    ai and bi are the indices of the vertices in graph g to connect.
    """
    # When looking "across" the hull from a to b, the vertices in the right
    # slice are on the right-hand side from the perspective of a.
    right_slice: Sequence[Vertex] = g[ai+1:bi]
    left_slice: Sequence[Vertex] = g[bi+1:ai]

    cross_edges: List[Tuple[Vertex, Vertex]] = []

    for rv in right_slice:
        for lv in reversed(left_slice):
            if rv.nbrs.contains(lv):
                cross_edges.append((rv, lv))

    for c in cross_edges:
        g.flip_edge(*c)


def add_hull_vertex(g: Graph, z: Vertex):
    """Add vertex z to the hull represented by graph g.

    If z is already on the interior of the convex hull, no action is taken.
    Similarly, any vertices currently on the hull that become interior vertices
    due to the addition of z are removed.
    """
    # TODO: Terminate early if z is already in or on the hull
    # TODO: Calculate a and b using our old homework algorithm
    # From the perspective of z, the point a should be to its left, and b should
    # be to its right

    a = Vertex(0, 0)
    b = Vertex(0, 0)
    ai = g.index(a)
    bi = g.index(b)

    flip_between(g, ai, bi)

    for v in g[ai+1:bi]:
        g.remove_vertex(v)

    g.add_vertex(z)
    g.add_edge(a, z)
    g.add_edge(b, z)
