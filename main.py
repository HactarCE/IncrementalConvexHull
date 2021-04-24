import pyglet


INSTRUCTIONS = """\
Left click on an edge to flip it.
Left click outside the graph to add a new vertex.
Right click on a vertex to remove it.

Animation speed: {animation_speed:.2f}
[f] faster
[s] slower
"""

animation_speed = 1


def main():
    window = pyglet.window.Window()
    label = pyglet.text.Label(
        INSTRUCTIONS.format(animation_speed=animation_speed),
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
        label.draw()

    pyglet.app.run()


if __name__ == '__main__':
    main()
