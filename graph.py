from __future__ import annotations

import operator
from typing import List, Sequence, Union

import numpy as np
from itertools import permutations
import point


class Graph:
    def __init__(self):
        self.vertices: List[Vertex] = []

    def add_vertex(self, x, y):
        # Initialize vertex and insert neighbors
        new_vertex = Vertex(x, y)
        self.vertices.append(new_vertex)

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
        n1 = v1.get_next_nbr(v2)
        n2 = v2.get_next_nbr(v1)
        self.remove_edge(v1, v2)
        self.add_edge(n1, n2)

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
        size = len(self.nbrs)

        # Case 1: List has less than 2 elements
        if size == 0 or size == 1:
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
                        insert = compare - 1
                        self.nbrs.insert(insert, v)
                        break
                    else:
                        prev_orient = curr_orient
                        compare = compare + 1

    def remove_neighbor(self, v: Vertex):
        self.nbrs.remove(v)

    def get_next_nbr(self, v) -> Vertex:
        idx = self.nbrs.index(v)
        if (idx == len(self.nbrs - 1)):
            return self.nbrs[0]
        return self.nbrs[idx + 1]

    def __str__(self) -> str:
        return str(self.loc)
