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

VERT_RADIUS = 3
HOVERED_VERT_RADIUS = 4

VERTEX_HOVER_RADIUS = 15


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
    x, y = xy
    x1, x2 = x - r, x + r
    y1, y2 = y - r, y + r
    return [(x1, y1), (x2, y1), (x1, y2), (x2, y2)]


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

        # Draw vertices in the graph
        vertex_coords = []
        vertex_colors = []
        gl_indices = []
        for v in graph.vertices:
            l = len(vertex_coords)
            radius = HOVERED_VERT_RADIUS if v is nearest_thing else VERT_RADIUS
            color = HOVERED_VERT_COLOR if v is nearest_thing else VERT_COLOR
            new_vertices = gl_centered_rect_coords(v.loc, radius)
            vertex_coords += new_vertices
            vertex_colors += [color] * len(new_vertices)
            gl_indices += [l + x for x in [0, 1, 2, 3, 2, 1]]
        pyglet.graphics.draw_indexed(
            len(vertex_coords),
            pyglet.gl.GL_TRIANGLES,
            gl_indices,
            ('v2i', list(flatten(vertex_coords))),
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
            graph.add_vertex(x, y)
        update_nearest_thing()

    pyglet.app.run()


if __name__ == '__main__':
    main()
