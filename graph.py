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
        pass  # TODO

    def flip_edge(self, v1, v2):
        # Return an exception if cannot flip
        #   either because the edge is on the hull
        #   or because the quadrilateral is concave
        pass  # TODO


class Vertex:
    def __init__(self, x, y):
        self.loc = np.array([x, y])
        self.nbrs = []

    def add_neighbor(self, v):
        # TODO: this should be in CCW order
        self.nbrs.append(v)

    def remove_neighbor(self, v):
        self.nbrs.remove(v)
