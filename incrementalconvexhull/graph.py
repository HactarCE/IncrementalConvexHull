from __future__ import annotations

import operator
from typing import List, Sequence, Tuple, Union

import numpy as np

from . import point


class Graph:
    """Undirected convex graph of 2D Euclidean points.
    Points are stored in a list in counterclockwise sorted order. Edges are
    stored using an adjacency list on each vertex.
    """

    def __init__(self):
        """Construct a graph with no vertices."""
        self.vertices: List[Vertex] = []

    def add_vertex(self, x, y):
        """Add a vertex at an XY position to the graph and return the new
        `Vertex`.
        If the point is already on the interior of the convex hull, no action is taken.
        Similarly, any vertices currently on the hull that become interior vertices
        due to the addition of z are removed.
        """
        z = Vertex(x, y)
        a, b = None, None

        if len(self) < 2:
            # 2 or fewer vertices are always in ccw order
            self.vertices.append(z)
        else:
            # Don't do anything if the point to add is already within the convex hull.
            if self.hull_contains(x, y):
                return

            # From the perspective of z, the point a should be to its left, and b should
            # be to its right
            # TODO: handle None, None (if z is on interior)
            b, a = self.find_convex_nbrs(z)
            ai = self.index(a)
            bi = self.index(b)

            self.flip_between(ai, bi)

            for v in self[ai+1:bi]:
                self.remove_vertex(v)

            # Keep vertices in ccw order
            self.vertices.insert(self.index(b), z)

        if a is not None:
            self.add_edge(a, z)
            if b is not None and a is not b:
                self.add_edge(b, z)

        return z

    def hull_contains(self, x, y):
        """Return whether an XY position is inside the convex hull of the
        vertices of the graph.
        """
        if (len(self.vertices) < 3):
            return False
        new_point = np.array([x, y])
        for v1, v2 in self.vertex_pairs():
            if point.orient(v1.loc, v2.loc, new_point) < 0:
                return False
        return True

    def __len__(self) -> int:
        """Return the number of vertices in the graph."""
        return len(self.vertices)

    def __getitem__(self, i) -> Union[Vertex, Sequence[Vertex, None, None]]:
        """Retrieve the vertex (or slice of vertices) specified by the circular
        index `i`.
        Implementation partially based on
        https://stackoverflow.com/a/47606550/2977638.
        """
        if isinstance(i, slice):
            # Recursive call. But x is no longer a slice object, so the
            # recursion bottoms out.
            return [self[x] for x in self._rangeify(i)]

        index = operator.index(i)
        try:
            return self.vertices[index % len(self)]
        except ZeroDivisionError:
            raise IndexError('list index out of range')

    def _rangeify(self, slice):
        """See https://stackoverflow.com/a/47606550/2977638."""
        start, stop, step = slice.start, slice.stop, slice.step
        if start is None:
            start = 0
        if stop is None:
            stop = len(self)
        if step is None:
            step = 1
        return range(start, stop, step)

    def index(self, v: Vertex):
        """Return the index of the vertex"""
        return self.vertices.index(v)

    def add_edge(self, v1: Vertex, v2: Vertex):
        """Add an edge between two vertices in the graph."""
        v1.add_neighbor(v2)
        v2.add_neighbor(v1)

    def edges(self):
        """Return a generator over all edges in the graph."""
        visited = set()
        for v in self.vertices:
            visited.add(v)
            for nbr in v.nbrs:
                if nbr not in visited:
                    yield (v, nbr)

    def flip_edge(self, v1: Vertex, v2: Vertex):
        """Flip an edge between two vertices in graph.

        An edge is flipped by creating a new edge crossing the other diagonal of
        the quadrilateral formed by the triangles on either side of the original
        edge.

        Raises a `ValueError` if the edge cannot be flipped for any of the
        following reasons:

        - Either vertex is not in the graph.
        - The edge is not in the graph.
        - The edge is on the convex hull of the graph.
        - The quadrilateral formed by the triangles on either side of the edge
          is concave.
        """
        # TODO: Return an exception if cannot flip
        #   either because the edge is on the hull
        #   or because the quadrilateral is concave
        n1 = v1.get_next_nbr(v2)
        n2 = v2.get_next_nbr(v1)
        self.remove_edge(v1, v2)
        self.add_edge(n1, n2)

    def remove_vertex(self, v1: Vertex):
        """Remove a vertex and all its edges from the graph."""
        # Remove v1 from associated neighbors
        for node in v1.nbrs:
            node.nbrs.remove(v1)

        # Remove v1 from graph
        self.vertices.remove(v1)

    def remove_edge(self, v1: Vertex, v2: Vertex):
        """Remove the edge between two vertictes from the graph."""
        # Remove V1 from V2 nbrs
        v1.remove_neighbor(v2)

        # Remove V2 from V1 neighbors
        v2.remove_neighbor(v1)

    def find_convex_nbrs(self, v: Vertex):
        """Find neighbors of the newly inserted point in the existing graph"""
        size = len(self.vertices)

        if size < 2:
            raise ValueError(
                "There must be a minimum of 2 points must be in the graph"
            )
        else:
            a, b = None, None
            prev_orient = point.orient(self.vertices[-1].loc, self.vertices[0].loc, v.loc)

            for v1, v2 in self.vertex_pairs():
                curr_orient = point.orient(v1.loc, v2.loc, v.loc)

                # Set A before B
                if prev_orient == -1 and curr_orient == 1:
                    a = v1
                if prev_orient == 1 and curr_orient == -1:
                    b = v1

                if a is not None and b is not None:
                    return a, b

                prev_orient = curr_orient

        return None, None

    def vertex_pairs(self):
        """Return a generator over all pairs of adjacent points on the convex
        hull.
        """
        for i in range(len(self)):
            yield (self[i], self[i+1])

    def flip_between(self, ai: int, bi: int):
        """Transform the given graph's triangulation such that an edge between a and b exists.
        ai and bi are the indices of the vertices in graph g to connect.
        """
        # When looking "across" the hull from a to b, the vertices in the right
        # slice are on the right-hand side from the perspective of a.
        right_slice: Sequence[Vertex] = self[ai+1:bi]
        left_slice: Sequence[Vertex] = self[bi+1:ai]

        cross_edges: List[Tuple[Vertex, Vertex]] = []

        for rv in right_slice:
            for lv in reversed(left_slice):
                if rv.nbrs.contains(lv):
                    cross_edges.append((rv, lv))

        for c in cross_edges:
            self.flip_edge(*c)


class Vertex:
    """Vertex in an undirected graph of 2D Euclidean points.
    Each vertex contains a list of neighboring vertices for which there is a
    connecting edge. The list of vertices is sorted counterclockwise by angle,
    however the starting index is arbitrary.
    """

    def __init__(self, x, y):
        """Create a vertex with an XY location and empty neighbors list."""
        self.loc = np.array([x, y])
        self.nbrs: List[Vertex] = []

    def add_neighbor(self, v: Vertex):
        """Add another vertex as a neighbor to this one."""
        size = len(self.nbrs)

        # Case 1: List has less than 2 elements
        if size < 2:
            self.nbrs.append(v)

        # Case 2: Search through nbrs to find correct location
        prev_orient, curr_orient = 0, 0
        for v1, v2 in self.nbr_pairs():
            curr_orient = point.orient(v1.loc, v2.loc, v.loc)
            if curr_orient == (prev_orient * -1):
                idx = self.nbrs.index(v2) + 1
                self.nbrs.insert(idx, v)
                break
            else:
                prev_orient = curr_orient

    def remove_neighbor(self, v: Vertex):
        """Remove another vertex as a neighbor of this one.
        This does NOT remove this vertex as a neighbor of the other one.
        """
        self.nbrs.remove(v)

    def get_next_nbr(self, v) -> Vertex:
        """Returns the next neighboring vertex in counterclockwise order."""
        idx = self.nbrs.index(v)
        if (idx == len(self.nbrs - 1)):
            return self.nbrs[0]
        return self.nbrs[idx + 1]

    def __str__(self) -> str:
        return str(self.loc)

    def nbr_pairs(self):
        """Return a generator over all pairs of adjacent points on the list of neighbors.
        """
        n = len(self.nbrs)
        for i in range(n):
            yield (self.nbrs[i], self.nbrs[(i+1) % n])
