import unittest
from . import graph


class PolygonTest(unittest.TestCase):
    def test_add_vertex(self):
        g = graph.Graph()

        # Add three vertices in *gasp* clockwise order! Oh no!
        g.add_vertex(-0.5, -0.5)
        g.add_vertex(0, 2)
        g.add_vertex(2, 0)

        self.assertEqual(3, len(g.vertices))

        first_vertex = g.vertices[0]
        second_vertex = g.vertices[1]
        if (first_vertex.loc[0] == -0.5):
            self.assertEqual(2, second_vertex.loc[0])
        elif (first_vertex.loc[0] == 0):
            self.assertEqual(-0.5, second_vertex.loc[0])
        elif (first_vertex.loc[0] == 2):
            self.assertEqual(0, second_vertex.loc[0])
        else:
            self.fail("First vertex had unrecognized x coordinate")

        # These vertices are on or inside the current hull. Don't add them!
        g.add_vertex(0, 0)
        g.add_vertex(1, 1)
        self.assertEqual(3, len(g.vertices))

        # Add a fourth valid vertex and check our neighbors.
        # We shouldn't have needed to do any flips.
        g.add_vertex(1.5, 1.5)
        self.assertEqual(4, len(g.vertices))

        x_axis_vertex = next(v for v in g.vertices if v.loc[1] == 0)
        y_axis_vertex = next(v for v in g.vertices if v.loc[0] == 0)
        neg_vertex = next(v for v in g.vertices if v.loc[0] < 0)
        fourth_vertex = next(v for v in g.vertices if v.loc[0] == 1.5)

        self.assertEqual(3, len(x_axis_vertex.nbrs))
        self.assertEqual(3, len(y_axis_vertex.nbrs))
        self.assertEqual(2, len(neg_vertex.nbrs))
        self.assertEqual(2, len(fourth_vertex.nbrs))

        # Add a vertex that should cause a flip!
        g.add_vertex(3, -1)
        self.assertEqual(4, len(g.vertices))

    def test_remove_vertex(self):
        pass

    def test_find_convex_nbrs(self):
        # define points
        a = graph.Vertex(-5, 0)
        b = graph.Vertex(5, 0)
        c = graph.Vertex(0, 5)
        d = graph.Vertex(0, -1)

        # no points; should raise an exception
        g = graph.Graph()
        self.assertRaises(
            ValueError,
            lambda: g.find_convex_nbrs(graph.Vertex(0, 5)),
        )

        # one point; should raise an exception
        g.vertices.append(a)
        self.assertRaises(
            ValueError,
            lambda: g.find_convex_nbrs(graph.Vertex(0, 5)),
        )

        # two points with test point below;
        # should return the points in order
        g.vertices.append(b)
        assert (a, b) == g.find_convex_nbrs(graph.Vertex(0, -5))
        # two points with test point above;
        # should return the points in opposite order
        # print(a, b)
        # x, y = g.find_convex_nbrs(graph.Vertex(0, 5))
        # print('really', x, y)
        assert (b, a) == g.find_convex_nbrs(graph.Vertex(0, 5))

        # add a third point above the first two
        g.vertices.append(c)
        # test interior
        assert (None, None) == g.find_convex_nbrs(graph.Vertex(0, 2))
        # test each possible edge
        assert (a, b) == g.find_convex_nbrs(graph.Vertex(0, -5))
        assert (b, c) == g.find_convex_nbrs(graph.Vertex(5, 5))
        assert (c, a) == g.find_convex_nbrs(graph.Vertex(-5, 5))
        assert (b, a) == g.find_convex_nbrs(graph.Vertex(0, 10))
        assert (c, b) == g.find_convex_nbrs(graph.Vertex(-7, -1))
        assert (a, c) == g.find_convex_nbrs(graph.Vertex(7, -1))

        # add a fourth point slightly below the first two
        g.vertices.insert(1, d)
        # test interior
        assert (None, None) == g.find_convex_nbrs(graph.Vertex(0, 0))
        # test adjacent pairs
        assert (a, d) == g.find_convex_nbrs(graph.Vertex(-5, -1))
        assert (d, b) == g.find_convex_nbrs(graph.Vertex(5, -1))
        assert (b, c) == g.find_convex_nbrs(graph.Vertex(5, 5))
        assert (c, a) == g.find_convex_nbrs(graph.Vertex(-5, 5))
        # test opposite pairs
        assert (a, b) == g.find_convex_nbrs(graph.Vertex(0, -2))
        assert (b, a) == g.find_convex_nbrs(graph.Vertex(0, 6))
        assert (c, d) == g.find_convex_nbrs(graph.Vertex(-6, 0))
        assert (d, c) == g.find_convex_nbrs(graph.Vertex(6, 0))
        # test reversed adjacent pairs
        assert (a, c) == g.find_convex_nbrs(graph.Vertex(11, -4))
        assert (c, b) == g.find_convex_nbrs(graph.Vertex(-11, -4))
        #      (b, d) is impossible with these points
        #      (d, a) is impossible with these points

    def test_vertex_pairs(self):
        g = graph.Graph()
        v0 = g.add_vertex(0, 0)
        v1 = g.add_vertex(0, 1)
        v2 = g.add_vertex(1, 0)
        v3 = g.add_vertex(1, 1)
        should_return = [(v0, v2), (v2, v3), (v3, v1), (v1, v0)]
        last_index = -1
        count = 0
        for pair in g.vertex_pairs():
            count += 1
            this_index = should_return.index(pair)
            if last_index != -1:
                self.assertEqual((last_index + 1) %
                                 len(should_return), this_index)
            last_index = this_index
        self.assertEqual(count, len(should_return))
