import numpy as np


class Graph:
    def __init__(self):
        self.vertices = []

    def add_vertex(self, x, y):
        # TODO: this should be in CCW order
        self.vertices.append(Vertex(x, y))

    def __getitem__(self, i):
        # TODO: support slices that wrap around
        return self.vertices[i % len(self.vertices)]

    def add_edge(self, v1, v2):
        v1.add_neighbor(v2)
        v2.add_neighbor(v1)

    def flip_edge(self, v1, v2):
        # Return an exception if cannot flip
        #   either because the edge is on the hull
        #   or because the quadrilateral is concave
        pass  # TODO

    def remove_vertex(self, v1):
        # Remove v1 from associated neighbors
        for node in v1.nbrs:
            node.nbrs.remove(v1)

        # Remove v1 from graph
        self.vertices.remove(v1)

    def remove_edge(self, v1, v2):
        # Remove V1 from V2 nbrs
        v1.remove_neighbor(v2)

        # Remove V2 from V1 neighbors
        v2.remove_neighbor(v1)


class Vertex:
    def __init__(self, x, y):
        self.loc = np.array([x, y])
        self.nbrs = []

    def add_neighbor(self, v):
        # TODO: this should be in CCW order
        self.nbrs.append(v)

    def remove_neighbor(self, v):
        # TODO: We don't need to reorder, right?
        self.nbrs.remove(v)
