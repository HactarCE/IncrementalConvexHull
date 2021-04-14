from __future__ import annotations

import operator
from typing import List, Sequence, Union

import numpy as np


class Graph:
    def __init__(self):
        self.vertices: List[Vertex] = []

    def add_vertex(self, x, y):
        # TODO: this should be in CCW order
        self.vertices.append(Vertex(x, y))

    def __getitem__(self, i) -> Union[Vertex, Sequence[Vertex, None, None]]:
        """Retrieve the vertex (or slice of vertices) specified by the circular index i.

        Code inspired by https://stackoverflow.com/a/47606550/2977638
        """
        if isinstance(i, slice):
            # Recursive call. But x is no longer a slice object, so the
            # recursion bottoms out.
            return [self[x] for x in self._rangeify(i)]

        index = operator.index(i)
        try:
            return self.vertices[index % len(self.vertices)]
        except ZeroDivisionError:
            raise IndexError('list index out of range')

    def _rangeify(self, slice):
        start, stop, step = slice.start, slice.stop, slice.step
        if start is None:
            start = 0
        if stop is None:
            stop = len(self.vertices)
        if step is None:
            step = 1
        return range(start, stop, step)

    def index(self, v: Vertex):
        return self.vertices.index(v)

    def add_edge(self, v1: Vertex, v2: Vertex):
        v1.add_neighbor(v2)
        v2.add_neighbor(v1)

    def flip_edge(self, v1: Vertex, v2: Vertex):
        # TODO: Return an exception if cannot flip
        #   either because the edge is on the hull
        #   or because the quadrilateral is concave
        pass  # TODO

    def remove_vertex(self, v1: Vertex):
        # Remove v1 from associated neighbors
        for node in v1.nbrs:
            node.nbrs.remove(v1)

        # Remove v1 from graph
        self.vertices.remove(v1)

    def remove_edge(self, v1: Vertex, v2: Vertex):
        # Remove V1 from V2 nbrs
        v1.remove_neighbor(v2)

        # Remove V2 from V1 neighbors
        v2.remove_neighbor(v1)


class Vertex:
    def __init__(self, x, y):
        self.loc = np.array([x, y])
        self.nbrs: List[Vertex] = []

    def add_neighbor(self, v: Vertex):
        # TODO: this should be in CCW order
        self.nbrs.append(v)

    def remove_neighbor(self, v: Vertex):
        # TODO: We don't need to reorder, right?
        self.nbrs.remove(v)
