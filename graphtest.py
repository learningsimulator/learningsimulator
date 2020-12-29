import graph

g = graph.Graph()
g.addEdge( "s1", "s2", "b1", {'x':1.5} )
g.addEdge( "s1", "s1", "b2", {'x':2.2} )
g.addEdge( "s2", "s1", "b1", {'x':3.5} )
g.addEdge( "s2", "s1", "b2", {'x':10} )
g.addEdge( "s2", "s3", "b2", {'x':10} )

print( g.graph )

paths = g.find_simple_paths( "s1", "s3" )

for p in paths:
    print( p )
    print( g.path_sum_property( p, 'x' ) )
    print( g.path_product_property( p, 'x' ) )
