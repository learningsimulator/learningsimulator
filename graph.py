# graph traversal algorithm derived from:
# https://www.baeldung.com/cs/simple-paths-between-two-vertices
# we added a "color" properties to edges to track the behavior that
# connects nodes

from collections import defaultdict

class Graph: 

    def __init__( self ): 
        # graph is stored as adjacency list: self.graph[x] is a list
        # of neighbors of x.
        self.graph = defaultdict( list )
        # the path we are working on: 
        self.currentPath = list()
        # all paths found so far:
        self.simplePaths = list()
        # whether a node has already been visited:
        self.visited = defaultdict( lambda: False )
        # properties associated with each edge
        self.properties = defaultdict( dict )
        
    def addEdge( self, source, destination, color, properties=None ): 
        # if not source in self.graph.keys():
        #     self.graph[ source ] = list()
        # if not destination in self.graph.keys():
        #     self.graph[ destination ] = list()
        if (destination,color) not in self.graph[ source ]:
            self.graph[ source ].append( (destination,color) )
        self.properties[ (source,destination,color) ] = properties
        # self.visited[ source      ] = False
        # self.visited[ destination ] = False
        
    def find_simple_paths_help( self, source_color, destination_color ):
        if self.visited[ source_color[0] ]:
            return

        self.visited[ source_color[0] ] = True
        self.currentPath.append( source_color )

        if source_color[0] == destination_color[0]:
            self.simplePaths.append( self.currentPath.copy() )
            self.visited[ source_color[0] ] = False
            self.currentPath.pop()
            return

        for neighbor in self.graph[ source_color[0] ]:
            self.find_simple_paths_help(
                neighbor,
                destination_color
            )

        self.currentPath.pop()
        self.visited[ source_color[0] ] = False
        
    def find_simple_paths( self, source, destination ):
        if len( self.graph.keys() ) < 2:
            return []
        # all nodes are initially marked unvisited:
        self.visited = defaultdict( lambda: False )
        self.currentPath = []
        self.simplePaths = []
        self.find_simple_paths_help( (source,None), (destination,None) )
        return self.simplePaths

    def expected_path_value( self, path ):
        probability = 1
        path_value = 0
        for i in range(1,len(path)):
            x = ( path[i-1][0], path[i][0], path[i][1] )
            properties = self.properties[ x ]
            net_value = properties['value'] - properties['cost']
            probability *= properties['probability']
            path_value += net_value * probability
        path_value /= len(path) - 1
        return path_value

