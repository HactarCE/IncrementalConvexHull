from collections.abc import Iterable
import itertools
import numpy as np
import pyglet

from graph import Graph, Vertex
from point import dist


INSTRUCTIONS = """\
Click outside the graph to add a new vertex.
Click near an edge to flip it.
Click on a vertex to remove it.

Animation multiplier: {animation_multiplier:.2f}
[f] faster
[s] slower
"""

VERT_COLOR = (127, 127, 127)
HOVERED_VERT_COLOR = (255, 0, 0)
EDGE_COLOR = (95, 95, 95)
HOVERED_EDGE_COLOR = (63, 191, 63)


VERT_RADIUS = 3
HOVERED_VERT_RADIUS = 4
EDGE_RADIUS = 1
HOVERED_EDGE_RADIUS = 3

VERTEX_HOVER_RADIUS = 15
EDGE_HOVER_RADIUS = 15


def flatten(it):
    """Flatten nested iterators.

    Implementation based on https://stackoverflow.com/a/2158532/4958484.
    """
    for elem in it:
        if isinstance(elem, Iterable) and not isinstance(elem, (str, bytes)):
            yield from flatten(elem)
        else:
            yield elem


def gl_centered_rect_coords(xy, r):
    x, y = xy.astype(np.float32)
    x1, x2 = x - r, x + r
    y1, y2 = y - r, y + r
    return [(x1, y1), (x2, y1), (x1, y2), (x2, y2)]


def gl_edge_coords(a, b, r):
    fwd = (b - a).astype(np.float32)
    fwd *= r / np.linalg.norm(fwd)
    left = np.array([-fwd[1], fwd[0]])  # rotate `fwd` counterclockwise 90
    right = -left
    back = -fwd
    return [
        a + back + left,
        a + back + right,
        b + fwd + left,
        b + fwd + right,
    ]


def gl_quad_indices(vertex_count):
    for base in range(0, vertex_count, 4):
        yield from [base + i for i in [0, 1, 2, 3, 2, 1]]


def edge_dist(endpoint1, endpoint2, point):
    """Returns the distance from a point to a line segment.

    Immplementation based on
    https://en.wikipedia.org/wiki/Distance_from_a_point_to_a_line#Vector_formulation.
    """
    pass  # TODO


def main():
    # Program state
    graph = Graph()
    animation_multiplier = 1
    mouse_pos = np.array([0, 0])
    nearest_thing = None

    # UI elements
    window = pyglet.window.Window()
    instructions_label = pyglet.text.Label(
        "",
        x=10,
        y=window.height - 10,
        multiline=True,
        width=1000,
        anchor_x='left',
        anchor_y='top',
    )

    def update_nearest_thing():
        nonlocal nearest_thing

        nearest_vertex = None
        if graph.vertices:
            nearest_vertex = min(
                graph.vertices,
                key=lambda v: dist(mouse_pos, v.loc),
            )
            if dist(mouse_pos, nearest_vertex.loc) > VERTEX_HOVER_RADIUS:
                nearest_vertex = None

        nearest_edge = None  # TODO

        nearest_thing = nearest_vertex or nearest_edge

    @window.event
    def on_draw():
        window.clear()

        # Update text
        instructions_label.text = INSTRUCTIONS.format(
            animation_multiplier=animation_multiplier
        )
        instructions_label.draw()

        vertex_coords = []
        vertex_colors = []

        # Draw edges in the graph (so that they appear "below" vertices)
        for e in graph.edges():
            (v1, v2) = e
            radius = HOVERED_EDGE_RADIUS if e == nearest_thing else EDGE_RADIUS
            color = HOVERED_EDGE_COLOR if e == nearest_thing else EDGE_COLOR
            vertex_coords += gl_edge_coords(v1.loc, v2.loc, radius)
            vertex_colors += [color] * 4

        # Draw vertices in the graph
        for v in graph.vertices:
            radius = HOVERED_VERT_RADIUS if v is nearest_thing else VERT_RADIUS
            color = HOVERED_VERT_COLOR if v is nearest_thing else VERT_COLOR
            vertex_coords += gl_centered_rect_coords(v.loc, radius)
            vertex_colors += [color] * 4
        pyglet.graphics.draw_indexed(
            len(vertex_coords),
            pyglet.gl.GL_TRIANGLES,
            list(gl_quad_indices(len(vertex_coords))),
            ('v2f', list(flatten(vertex_coords))),
            ('c3B', list(flatten(vertex_colors))),
        )

    @window.event
    def on_key_press(symbol, modifiers):
        nonlocal animation_multiplier
        if symbol == pyglet.window.key.F and animation_multiplier > 1/4:
            animation_multiplier /= 5 ** (1/4)
        if symbol == pyglet.window.key.S and animation_multiplier < 4:
            animation_multiplier *= 5 ** (1/4)

    @window.event
    def on_mouse_motion(x, y, dx, dy):
        nonlocal mouse_pos
        mouse_pos = np.array([x, y])
        update_nearest_thing()

    @window.event
    def on_mouse_press(x, y, button, modifiers):
        if button != pyglet.window.mouse.LEFT:
            return
        if isinstance(nearest_thing, Vertex):
            graph.remove_vertex(nearest_thing)
        if nearest_thing is None:
            v1 = graph.add_vertex(x, y)
            for v2 in graph[:len(graph)-1]:
                graph.add_edge(v1, v2)
        update_nearest_thing()

    pyglet.app.run()


if __name__ == '__main__':
    main()
