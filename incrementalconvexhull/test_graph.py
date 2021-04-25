import unittest
from . import graph


class PolygonTest(unittest.TestCase):
    def test_add_vertex(self):
        pass

    def test_remove_vertex(self):
        pass

    def test_find_convex_nbrs(self):
        pass

    def test_vertex_pairs(self):
        g = graph.Graph()
        v0 = g.add_vertex(0, 0)
        v1 = g.add_vertex(0, 1)
        v2 = g.add_vertex(1, 0)
        v3 = g.add_vertex(1, 1)
        should_return = [(v0, v2), (v2, v3), (v3, v1), (v1, v0)]
        for pair in g.vertex_pairs():
            should_return.remove(pair)
        self.assertEqual(0, len(should_return))
