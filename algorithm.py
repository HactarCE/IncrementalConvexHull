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
