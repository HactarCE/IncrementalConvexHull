# IncrementalConvexHull
Incremental convex hull visualization for CSC 591

## Planning and Starting Resources
- Helpful [visualization tool](https://www.cs.usfca.edu/~galles/visualization/Algorithms.html) for tree rotations and data structures review

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

## Incremental Convex Hull Overview
A convex hull is the outtermost boundary in a set of points that encompasses all other points. This visualization tool only supports convex polygons with no colinear points. The following are properties of convex polygons:
- 
The following are properties of convex hulls:
- All points within a set are encompassed by the convex hull
- A tangent line can be drawn for each point on the convex hull such that all other points are on one side of the tangent line
- 
