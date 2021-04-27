from __future__ import annotations

import operator
from typing import List, Sequence, Union

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

        Params:
            x (flaot): x coordinate of vertex
            y (float): y coordinate of vertex

        Returns:
            None
        """
        z = Vertex(x, y)

        if len(self) < 2:
            # 2 or fewer vertices are always in ccw order
            self.vertices.append(z)
            if len(self) == 2:
                # Add edge between both vertices
                self.add_edge(*self.vertices)
        else:
            # Don't do anything if the point to add is already within the convex hull.
            if self.hull_contains(x, y):
                return

            # From the perspective of z, the point a should be to its left, and b should
            # be to its right
            # TODO: handle None, None (if z is on interior)
            a, b = self.find_convex_nbrs(z)

            self.flip_between(a, b)

            ai = self.index(a)
            bi = self.index(b)
            for v in self[ai+1:bi]:
                self.remove_vertex(v)

            # Keep vertices in ccw order
            self.vertices.insert(self.index(b), z)

            self.add_edge(a, z)
            self.add_edge(b, z)

        return z

    def hull_contains(self, x, y):
        """Return whether an XY position is inside the convex hull of the
        vertices of the graph.

        Params:
            x (float): position x coordinate
            y (float): position y coordinate

        Returns:
            True if point is contained within the hull.
            False if the point is on the convex hull boundary or outside of the hull.
        """
        if (len(self.vertices) < 3):
            return False
        new_point = np.array([x, y])
        for v1, v2 in self.vertex_pairs():
            if point.orient(v1.loc, v2.loc, new_point) < 0:
                return False
        return True

    def __len__(self) -> int:
        """Return the number of vertices in the graph.

        Params:
            None

        Returns:
            Number of verticies in the graph (int)
        """
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
        if len(self) > 0:
            while stop < start:
                stop += len(self)
        return range(start, stop, step)

    def index(self, v: Vertex):
        """Return the index of the vertex

        Params:
            v (Vertex): Vertex to index

        Returns:
            Index of vertex in graph vertex list (int)
        """
        return self.vertices.index(v)

    def add_edge(self, v1: Vertex, v2: Vertex):
        """Add an edge between two vertices in the graph.

        Params:
            v1 (Vertex): Vertex at one endpoint of the graph

            v2 (Vertex): Vertex at opposite end of edge

        Returns:
            None
            Raise ValueError if a duplicate edge is being added to graph
        """
        # Check for a duplicate edge before adding
        if v2 in v1.nbrs:
            raise ValueError("Edge already exists between Verticies.")

        v1.add_neighbor(v2)
        v2.add_neighbor(v1)

    def edges(self):
        """Return a generator over all edges in the graph.

        Params:
            None

        Returns:
            Generator of all edges in the graph represented as (current vertex (Vertex), neighbors list (List)
        """
        visited = set()
        for v in self.vertices:
            visited.add(v)
            for nbr in v.nbrs:
                if nbr not in visited:
                    yield (v, nbr)

    def can_flip(self, v1: Vertex, v2: Vertex):
        """Returns whether an edge in the graph can be flipped. See flip_edge().
        """
        try:
            self.check_can_flip(v1, v2)
            return True
        except ValueError:
            return False

    def check_can_flip(self, v1: Vertex, v2: Vertex):
        """Returns a ValueError if an edge in the graph cannot be flipped. See flip_edge().

        Params:
            v1 (Vertex):
            v2 (Vertex):

        Returns:
            True if an edge can be flipped between the 2 verticies
            False if the edge cannot be flipped between the 2 veritices
        """
        try:
            i1 = self.vertices.index(v1)
            i2 = self.vertices.index(v2)
        except ValueError:
            raise ValueError("vertex not in graph")

        diff = abs(i1 - i2)
        if diff == 1 or diff == len(self) - 1:
            raise ValueError("edge is on convex hull")

        if v1 in v2.nbrs:
            return  # Edge exists and can be flipped!
        else:
            raise ValueError("edge does not exist")

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

        Note that the quadrilateral formed by the triangles on either side of
        the edge is never concave because the vertices of the graph form a
        convex polygon.

        Params:
            v1 (Vertex):
            v2 (Vertex):

        Returns:
            None
        """
        self.check_can_flip(v1, v2)
        n1 = v1.get_next_nbr(v2)
        n2 = v2.get_next_nbr(v1)
        self.remove_edge(v1, v2)
        self.add_edge(n1, n2)

    def remove_vertex(self, v1: Vertex):
        """Remove a vertex and all its edges from the graph.

        Params:
            v1 (Vertex): Vertex to be removed from the graph

        Returns:
            None
        """
        # Remove v1 from associated neighbors
        for node in v1.nbrs:
            node.nbrs.remove(v1)

        # Remove v1 from graph
        self.vertices.remove(v1)

    def remove_edge(self, v1: Vertex, v2: Vertex):
        """Remove the edge between two vertictes from the graph.

        Params:
            v1 (Vertex): Vertex at the end of edge to be removed
            v2 (Vertex): Vertex at the opposing end of the edge to be removed

        Returns:
            None
        """
        # Remove V1 from V2 nbrs
        v1.remove_neighbor(v2)

        # Remove V2 from V1 neighbors
        v2.remove_neighbor(v1)

    def find_convex_nbrs(self, v: Vertex):
        """Find neighbors of the newly inserted point in the existing graph

        Params:
            v (Vertex): Vertex to be inserted into the graph

        Returns:
            None
            Raise ValueError if there are less than 2 points in the graph
        """
        size = len(self.vertices)

        if size < 2:
            raise ValueError(
                "There must be a minimum of 2 points must be in the graph"
            )
        else:
            a, b = None, None
            prev_orient = point.orient(
                self.vertices[-1].loc,
                self.vertices[0].loc,
                v.loc,
            )

            for v1, v2 in self.vertex_pairs():
                curr_orient = point.orient(v1.loc, v2.loc, v.loc)

                # Set A before B
                if prev_orient == 1 and curr_orient == -1:
                    a = v1
                if prev_orient == -1 and curr_orient == 1:
                    b = v1

                if a is not None and b is not None:
                    return a, b

                prev_orient = curr_orient

        return None, None

    def vertex_pairs(self):
        """Return a generator over all pairs of adjacent points on the convex
        hull.

        Params:
            None

        Returns:
            Generator of all pairs of adjacent points in the form (Vertex, Vertex)
        """
        for i in range(len(self)):
            yield (self[i], self[i+1])

    def flip_between(self, a: Vertex, b: Vertex):
        """Transform the given graph's triangulation such that an edge between a and b exists.

        Params:
            a (Vertex):
            b (Vertex):

        Returns:
            None
        """
        for c in self.get_cross_edges(a, b):
            self.flip_edge(*c)

    def get_cross_edges(self, a: Vertex, b: Vertex):
        """Compute the edges in the graph that cross the line through the specified vertices.

        Params:
            a (Vertex):
            b (Vertex):

        Returns:
            None
        """
        # When looking "across" the hull from a to b, the vertices in the right
        # slice are on the right-hand side from the perspective of a.
        ai = self.index(a)
        bi = self.index(b)
        right_slice: Sequence[Vertex] = self[ai+1:bi]
        left_slice: Sequence[Vertex] = self[bi+1:ai]

        for rv in right_slice:
            for lv in reversed(left_slice):
                if lv in rv.nbrs:
                    yield (rv, lv)


class Vertex:
    """Vertex in an undirected graph of 2D Euclidean points.
    Each vertex contains a list of neighboring vertices for which there is a
    connecting edge. The list of vertices is sorted counterclockwise by angle,
    however the starting index is arbitrary.
    """

    def __init__(self, x, y):
        """Create a vertex with an XY location and empty neighbors list.

        Params:
            x (float):
            y (float):
        """
        self.loc = np.array([x, y])
        self.nbrs: List[Vertex] = []

    def add_neighbor(self, v: Vertex):
        """Add another vertex as a neighbor to this one.

        Params:
            v (Vertex): Adds the vertex to the list of neighbors in the current vertex

        Returns:
            None
        """
        size = len(self.nbrs)

        # List has less than 2 elements
        if size < 2:
            self.nbrs.append(v)

        # Search through nbrs to find correct location
        else:
            # Between last and first point - will not appear in adjacent pairs list
            if point.orient(self.nbrs[-1].loc, v.loc, self.nbrs[0].loc) == 1:
                if (point.orient(self.nbrs[-2].loc, self.nbrs[-1].loc, v.loc)) == 1:
                    if (point.orient(v.loc, self.nbrs[0].loc, self.nbrs[1].loc)) == 1:
                        self.nbrs.insert(0, v)

            # Iterate through adjacent pairs of verticies
            for v1, v2 in self.nbr_pairs():
                # If v1, v, v2 is CCW
                if point.orient(v1.loc, v.loc, v2.loc) == 1:
                    # Save position of v2 for special case indexing
                    idx = self.nbrs.index(v2)

                    # Special Case Indexing if v1 = n-2 and v2 = n-1
                    if idx == size - 1:
                        if point.orient(self.nbrs[(idx - 2)].loc, v1.loc, v.loc) == 1:
                            # if v, v2, v2+ 1 is CCW
                            if point.orient(v.loc, v2.loc, self.nbrs[0].loc) == 1:
                                self.nbrs.insert(idx, v)

                    # No special indexing needed
                    else:
                        if point.orient(self.nbrs[(idx - 2)].loc, v1.loc, v.loc) == 1:
                            # if v, v2, v2+ 1 is CCW
                            if point.orient(v.loc, v2.loc, self.nbrs[(idx + 1)].loc) == 1:
                                self.nbrs.insert(idx, v)

    def remove_neighbor(self, v: Vertex):
        """Remove another vertex as a neighbor of this one.
        This does NOT remove this vertex as a neighbor of the other one.

        Params:
            v (Vertex): Vertex to be removed from list of neighbors

        Returns:
            None
        """
        self.nbrs.remove(v)

    def get_next_nbr(self, v) -> Vertex:
        """Returns the next neighboring vertex in counterclockwise order.
        """
        idx = self.nbrs.index(v)
        if idx == len(self.nbrs) - 1:
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
