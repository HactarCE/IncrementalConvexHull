from __future__ import annotations
import itertools

import operator
from typing import Iterable, List, Sequence, TypeVar, Union

import numpy as np
import point


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
        """
        # Initialize vertex and insert neighbors
        new_vertex = Vertex(x, y)
        # TODO: Remove vertices that are no longer in the graph
        self.vertices.append(new_vertex)
        return new_vertex

    def hull_contains(self, x, y):
        """Return whether an XY position is inside the convex hull of the
        vertices of the graph.
        """
        new_point = np.array([x, y])
        desired_orient = None
        for v1, v2 in pairwise(self.vertices):
            this_orient = point.orient(v1.loc, v2.loc, new_point)
            if desired_orient is None:
                desired_orient = this_orient
            if this_orient != desired_orient:
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
        size = len(self.vertices)

        if size == 0 or 1:
            raise ValueError("There must be a minimum of 2 points must be in the graph")
        elif size == 2:
            return self.vertices[0], self.vertices[1]
        else:
            anchor = self.vertices[0]
            prev_orient = point.orient(anchor, v, self.vertices[1])
            idx = 2
            vertex1, vertex2 = None, None

            while idx < size:
                curr_orient = point.orient(anchor, v, self.vertices[idx])

                # Vertex 1 marks 1st change in orientation
                if vertex1 is None and curr_orient == (prev_orient * -1):
                    vertex1 = self.vertices[(idx - 1)]
                elif vertex2 is None and curr_orient == (prev_orient * -1):
                    vertex2 = self.vertices[(idx - 1)]

                idx += 1

                if vertex1 is not None and vertex2 is not None:
                    return vertex1, vertex2


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
        else:
            anchor = self.nbrs[0]  # Anchor point
            compare = 1  # Index that will iterate thru nbrs, looking for orientation change

            # Get starting orientations
            prev_orient = point.orient(anchor, v, self.nbrs[compare])

            while compare <= size:
                # Reach end of nbrs with one orientation, append to end
                if compare == size:
                    self.nbrs.append(v)
                    break
                else:
                    curr_orient = point.orient(anchor, v, self.nbrs[compare])
                    if prev_orient == (-1 * curr_orient):
                        self.nbrs.insert(compare, v)
                        break
                    else:
                        prev_orient = curr_orient
                        compare += 1

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


T = TypeVar('T')


def pairwise(iterable: Iterable[T]):
    a, b = itertools.tee(iterable)
    next(b, None)
    return zip(a, b)
