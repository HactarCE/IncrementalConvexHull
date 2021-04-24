from collections.abc import Iterable
import pyglet
import itertools

from graph import Graph


INSTRUCTIONS = """\
Left click on an edge to flip it.
Left click outside the graph to add a new vertex.
Right click on a vertex to remove it.

Animation multiplier: {animation_multiplier:.2f}
[f] faster
[s] slower
"""


def flatten(it):
    """Flatten nested iterators.

    Implementation based on https://stackoverflow.com/a/2158532/4958484.
    """
    for elem in it:
        if isinstance(elem, Iterable) and not isinstance(elem, (str, bytes)):
            yield from flatten(elem)
        else:
            yield elem


def point_gl_tri_coords(xy):
    RADIUS = 2
    x, y = xy
    x1, x2 = x - RADIUS, x + RADIUS
    y1, y2 = y - RADIUS, y + RADIUS
    return [(x1, y1), (x2, y1), (x1, y2), (x2, y2)]


def main():
    # Program state
    graph = Graph()
    animation_multiplier = 1
    nearest_vertex = None
    nearest_edge = None

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
            gl_indices += [l + x for x in [0, 1, 2, 3, 2, 1]]
            new_vertices = point_gl_tri_coords(v.loc)
            vertex_coords += new_vertices
            vertex_colors += [(255, 0, 255)] * len(new_vertices)
        gl_quads = [point_gl_tri_coords(v.loc) for v in graph.vertices]
        gl_coords = list(itertools.chain(*gl_quads))
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
        pass

    @window.event
    def on_mouse_press(x, y, button, modifiers):
        if button != pyglet.window.mouse.LEFT:
            return
        graph.add_vertex(x, y)

    pyglet.app.run()


if __name__ == '__main__':
    main()
