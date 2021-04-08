# Algorithm Notes & Pseudocode

## Adding a Vertex to Known Endpoints

**Input**:

* $G$: Graph data structure
* $z$: Point to add
* $a$: Existing hull point on z's "left"
* $b$: Existing hull point on z's "right"

**Output**: $G$ will have $z$ added to it, and all vertices (with edges) between $a$ and $b$ will be removed.

**Algorithm**:

```
# Let G.vertices be specified in CCW order.
# Allow for circular access of lists.
R <- [G.vertices from a to b]
L <- [G.vertices from b to a]

# List of tuples: cross edges specified by endpoint
C <- []

# Start with r's closest to a
for r in R:
    # Start with l's closest to a
    for l in reverse(L):
        if r.adj.contains(l):
            C.push( (r, l) )

for c in C:
    # getNextAdj searches for the argument in adj,
    # then returns the next vertex in adj, CCW order.
    x' <- c.x.getNextAdj(c.y)
    y' <- c.y.getNextAdj(c.x)
    G.deleteEdge(x, y)
    G.insertEdge(x', y')

# deleteVertex also deletes all adjacency list refs.
# At this point, all of those edges are supposed to
# be removed from the triangulation.
for r in R:
    G.deleteVertex(r)

G.insertVertex(z)
G.insertEdge(a, z)
G.insertEdge(b, z)
```
