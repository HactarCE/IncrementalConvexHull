# IncrementalConvexHull
Incremental Convex Hull Visualization for CSC 591, Spring 2021

## Starting Resources
- Read our [documentation](https://hactarce.github.io/IncrementalConvexHull/api.html)
- [In-depth walkthrough](https://github.com/HactarCE/IncrementalConvexHull/blob/main/WALKTHROUGH.md) outlining how to use the GUI along with some interesting examples

## Development

We recommend working in a virtual environment to maintain consistency across developers' machines.

To set things up, run the following in the root project directory:

```
$ python -m venv --prompt IncConvexHull --upgrade-deps venv

$ source ./venv/bin/activate      # or venv\Scripts\activate.bat in Windows cmd
                                  # or venv\Scripts\Activate.ps1 in PowerShell

$ pip install -r requirements.txt

[Development happens here]

$ deactivate                      # When you're done working
```

If you ever add/change dependencies during development (e.g. running `pip install` or `pip upgrade` within the virtual environment), be sure to run `pip freeze > requirements.txt` and commit those changes to the repository.

## Incremental Convex Hull Concepts and Backgrounds
This interactive visualization tool will plot the points of a _convex polygon_ while incrementally growing the _convex hull_ as points are added. Additionally, this tool will maintain a valid _traingulation_ of the plotted polygon. The polygons are represented using a graph data structure with nodes and edges.


### Convex Polygons
The formal definition of convex polygon is a shape in which no interior angle is greater than 180 degrees. The simplest form of a convex polygon is a triangle. You can think of this visually as a shape with no "dents" in it, or edges that protrude inside the main cavity of the shape.

<img src="https://raw.githubusercontent.com/HactarCE/IncrementalConvexHull/main/docs/img/convex-concave-polygons.jpg" width="350" height=150>

### Triangulations
Every convex polygon can be broken down into smaller triangles, the simplest form of a convex polygon. This process of dividing a polygon into triangles is called triangulation. There are multiple ways the triangulate a shape. Our visualization supports multiple triangulations. Upon clicking an _internal_ edge in the polygon, the edge will then flip, producing another valid triangulation.

<img src="https://raw.githubusercontent.com/HactarCE/IncrementalConvexHull/main/docs/img/triangulation.png" width="500" height=150>

### Convex Hulls
A convex hull is the outtermost boundary in a set of points that encompasses all other points. This visualization tool only supports convex polygons with no colinear points. The following are properties of convex polygons: 

The following are properties of convex hulls:
- All points within a set are encompassed by the convex hull
- A tangent line can be drawn for each point on the convex hull such that all other points are on one side of the tangent line


<img src="https://raw.githubusercontent.com/HactarCE/IncrementalConvexHull/main/docs/img/convex_hull.png" width="200" height=150>
