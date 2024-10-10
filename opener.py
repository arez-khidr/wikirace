import pywikibot
import argparse
import wikitextparser as wtp
import pydot
import graphviz
import traverse
import networkx as nx
import matplotlib.pyplot as plt
import sys
#import the heuristics file
import heuristics
from IPython.display import Image
from PIL import Image

#Documentation for the py wiki bot can we found here
# https://doc.wikimedia.org/pywikibot/stable/

# Generate a custom wikipedia node class that will be used for traversing through the graph 

#Need to make a custom class object that serves as the wikipedia article as a node in a graph that I can use for traversal! 
class WikiNode: 
    '''Custom class object that serves as a wikipedia node for graph traversal!'''
    def __init__(self, page, parent): 
        #A pywikibot page instance of the object
        #self.site = site
        #Wikipedia page object
        self.page = page
        #Creates an interable link object, you can not access 
        self.title = self.page.title(with_ns = False)
        #A specific index but you can iterate over it 
        self.links = self.page.linkedPages(total=300)
        #Contains all of the content in a string that can be used
        self.content = self._getContent()
        #A list of all wiki node objects that are linked to the current one
        self.neighbors = []
        #Cost is not as important here but is used along with steps for hte a star algorithm
        self.cost = 0
        self.steps = 0
        #Parent needs to be stored for the retracing!  
        self.parent = parent
    

    def _getContent(self): 
        '''Function that returns the content of a page and fills it in'''
        text = self.page.get()
        return wtp.parse(text).plain_text()

    def generateNeighbors(self): 
        '''Function that generates all of the neighbors for a node as Wikinode objects
        Is called outside of instantiation as to only call when needed and not overload data'''
        for link_page in self.links: 
            try:
                neighbor_node = WikiNode(link_page, parent = self)
                self.neighbors.append(neighbor_node)
                #Titles 
                #print(neighbor_node.title)
            except: 
                pass
        
        print("All neighbors have been generated!")
                #print("Did Not have an article")

    def hasNeighbors(self): 
        '''Helper function that returns a boolean on if or if not the function has neighbors'''
        if self.neighbors: 
            return True
        else: 
            return False
    
    #Function that is used by the minHeap to be able to compare and heapify
    def __lt__(self, other): 
        return self.cost < other.cost

def add_to_graph(current_node, graph):
    if current_node.neighbors:
        for neighbor in current_node.neighbors:
            graph.add_edge(current_node.title, neighbor.title)
            add_to_graph(neighbor,graph)

def visualize_graph(start_node):
    graph = nx.Graph()
    #call recursive function that adds all the nodes to the graph
    add_to_graph(start_node,graph)
    nx.write_gexf(graph, "wiki.gexf")

    #get the degress of all the nodes
    degrees = dict(graph.degree)

    #Change the k value to increase the space between the nodes
    pos = nx.spring_layout(graph, k = 0.1, iterations = 1000) 
    nx.draw(graph, pos, nodelist = degrees.keys(),
             with_labels=True, 
             node_size=[v * 100 for v in degrees.values()], 
             font_size=10, 
             node_color='skyblue', 
             edge_color='gray')
    plt.show()

#TO-DO: 
#Work on the visualization of the nodes and the grpah down. 

def main(args): 
    #Value to be based in when loading in pages, only uses the english verision of wikipedia
    site = pywikibot.Site("en", "wikipedia")

    #Create an object for the start title. 
    start_page = pywikibot.Page(site,args.startTitle)
    start_node = WikiNode(start_page, None)
    #Create an object for the endTitle 
    end_page = pywikibot.Page(site,args.endTitle)
    end_node = WikiNode(end_page, None)

    #Heuristic function that will be passed into the search algorithm
    heuristic = None

    if(args.heuristic == "tfidf"): 
        heuristic = heuristics.tfidf
    elif(args.heuristic == "embeddings"): 
        heuristic = heuristics.word_embeddings
    else: 
        print("Invalid heuristic, the options are: tfidf or embeddings")
        return
    
    nodes_visted = traverse.astar(start_node, end_node, heuristic)
    print(nodes_visted)


    # tfidf = heuristics.tfidf(start_node, end_node)
    # print("tfidf score: " + str(tfidf))

    # word_embeddings = heuristics.word_embeddings(start_node, end_node)
    # print("word embeddings score: " + str(word_embeddings))

    

    #Call the a star search here!
    # print(start_node.content)
    # start_node.generateNeighbors()
    # start_node.neighbors[19].generateNeighbors()
    # start_node.neighbors[19].neighbors[30].generateNeighbors()

    #Visualize the graph from teh start node
    visualize_graph(start_node)
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Enter two wikipedia article titles to start and stop from! This will then find the shortest path")
    parser.add_argument("startTitle",
                        help='The title of the wikipedia page we are starting from')
    parser.add_argument("endTitle",
                        help='The title of the wikipedia page we want to end at')
    parser.add_argument("heuristic",
                        help='The Heuristic that we want to test all the nodes on')
    args = parser.parse_args()
    main(args)





