import pywikibot
import argparse
import wikitextparser as wtp
import pydot
import graphviz
import sys
from IPython.display import Image
from PIL import Image

#Documentation for the py wiki bot can we found here
# https://doc.wikimedia.org/pywikibot/stable/

# Generate a custom wikipedia node class that will be used for traversing through the graph 


#Need to make a custom class object that serves as the wikipedia article as a node in a graph that I can use for traversal! 
class WikiNode: 
    '''Custom class object that serves as a wikipedia node for graph traversal!'''
    def __init__(self, page): 
        #A pywikibot page instance of the object
        #self.site = site
        #Wikipedia page object
        self.page = page
        #Creates an interable link object, you can not access 
        self.title = self.page.title(with_ns = False)
        #A specific index but you can iterate over it 
        self.links = self.page.linkedPages(total = 20)
        #Contains all of the content in a string that can be used
        self.content = self._getContent()
        #The Heuristic value that guides how close two objects are
        #There are various types of heuristics we can call
        self.heuristic = None
        #A list of all wiki node objects that are linked to the current one
        self.neighbors = []

        

    def _getContent(self): 
        '''Function that returns the content of a page and fills it in'''
        text = self.page.get()
        return wtp.parse(text).plain_text()

    def generateNeighbors(self): 
        '''Function that generates all of the neighbors for a node as Wikinode objects
        Is called outside of instantiation as to only call when needed and not overload data'''
        for link_page in self.links: 
            try:
                neighbor_node = WikiNode(link_page)
                self.neighbors.append(neighbor_node)
                #Titles 
                print(neighbor_node.page)
            except: 
                print("Did Not have an article")

    def hasNeighbors(self): 
        '''Helper function that returns a boolean on if or if not the function has neighbors'''
        if self.neighbors: 
            return True
        else: 
            return False



def traverse(current_node, graph):
    '''traverses through the graph and sets the nodes up'''
    #If I am getting weird issues with cycles and multiple links,
    # I might need a dictionary to keep track of everything

    #Also for the future, maybe it set it up so that the size of the node changes based on the number of edges

    #How to get rid of this weird double linking that is going on.
   
    # Set up the graph node
    graph_node = pydot.Node(str(current_node.title), shape="circle")
    graph.add_node(graph_node)

    # If this node has a neighbors list that is populated
    if current_node.neighbors:
        for neighbor in current_node.neighbors:
            # Create an edge from the current node to its neighbor
            edge = pydot.Edge(str(current_node.title), str(neighbor.title), color="blue")
            graph.add_edge(edge)
            # Recursively traverse the neighbor
            traverse(neighbor, graph)
            print("hi there")

    
    
    #Teh current node is a wikinode object

    #For each node, set its proper edges and values
    graph_node = pydot.Node(str(current_node.title), shape = "circle")
    graph.add_node(graph_node)
    
    #If this node has a neighbors list that is populated
    if current_node.neighbors: 
        for neighbor in current_node.neighbors: 
            edge = pydot.Edge(str(current_node.title), str(neighbor.title), color = "blue")
            graph.add_edge(edge)


def printTree(start_node): 
    '''Visualizes the graph for a wikipedia serarch'''
    '''The start node node is passed in as a paramaeter'''
    #Iteratively go through the binary search tree and get all of the nodes printing at each line
    #https://pypi.org/project/pydot/
    graph = pydot.Dot("my_graph", graph_type="graph", bgcolor = "white") 
    #Need to do a search that goes through and generates a plot
    
    #Function that goes through the graph and generates it 
    traverse(start_node, graph)
    #Visualize the output
    graph.write_png("graph.png")
    img = Image.open("graph.png")
    img.show()


#TO-DO: 
#Work on the visualization of the nodes and the grpah down. 

def main(args): 
    #Value to be based in when loading in pages, only uses the english verision of wikipedia
    site = pywikibot.Site("en", "wikipedia")

    #Create an object for the start title. 
    start_page = pywikibot.Page(site,args.startTitle)
    start_node = WikiNode(start_page)
    #Create an object for the endTitle 
    end_page = pywikibot.Page(site,args.endTitle)
    end_node = WikiNode(end_page)

    #print(start_node.content)
    start_node.generateNeighbors()
    start_node.neighbors[19].generateNeighbors()
    printTree(start_node)

    #FOr the visualization of the graph, we a


    #a way to pull a page to look at 
    #test_page = "116 John Street"
    #page = pywikibot.Page(site, test_page)
    #text = page.get()
   
   # print(text)
    # #pulls all the links of a page
    # links = page.linkedPages()

    # link_titles = []
    # for link in links: 
    #     #Removing the NS just gives us the name!
    #     link_titles.append((link.title(with_ns = False)))
    
    # print(link_titles)

    
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Enter two wikipedia article titles to start and stop from! This will then find the shortest path")
    parser.add_argument("startTitle",
                        help='The title of the wikipedia page we are starting from')
    parser.add_argument("endTitle",
                        help='The title of the wikipedia page we want to end at')
    args = parser.parse_args()
    main(args)





