import pywikibot
import argparse
import wikitextparser as wtp
import traverse
import networkx as nx
import matplotlib.pyplot as plt
import sys
#import the heuristics file
import heuristics
from IPython.display import Image
from PIL import Image
#import plotly library for graphing
import plotly.graph_objects as pgo


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

'''
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
    '''

def visualize_graph(start_node, path=None, max_nodes=None):
    #visualize PyGraphviz graph using networkx
    graph = nx.DiGraph()
    #call recursive function that adds all the nodes to the graph
    add_to_graph(start_node, graph)

    #if the max nodes is specified and not 0, then limit the number of nodes and create a subgraph
    if max_nodes and max_nodes > 0:
        #extract a subgraph, as the whole graph is too big
        #select only the first max nodes, which currently is 100
        #make sure the graph nodes are turned into a list before slicing it into a subgraph
        subgraph = graph.subgraph(list(graph.nodes())[:max_nodes])
    #otherwise
    else:
        #if the max nodes is not specified or an invalid number, then use the entire graph
        subgraph = graph

    '''
    #initialize positions for all nodes
    position = {}
    '''

    #get the nodes in the math path and use spring layout for them
    #try spring layout
    #change k so that the distance between nodes is more spread out
    #change scale so that the graph is zoomed out
    position = nx.spring_layout(subgraph, k=10, iterations = 1000)

    '''
    #assign the positions of the paths first
    position.update(path_position)

    
    #for each node in the path, tightly cluster its neighbors around it
    #for each node in the path
    for node in path:
        #gather its neighbors
        neighbors = list(subgraph.neighbors(node))

        #if there are neighbors, use circular layout to create neighbor cluster around path node
        neighbor_position = nx.circular_layout(subgraph.subgraph(neighbors), scale=1.5)
        for neighbor, position in neighbor_position.items():
            neighbor_position[neighbor] = position + position[node]
        
        #update overall position dictionary with new neighbor positions
        position.update(neighbor_position)
    '''

    #create Plotly lists for the x and y coords of the edges in the path
    edge_x_path = []
    edge_y_path = []
    #create Plotly lists for the x and y coords of the edges not in the path
    edge_x_not_path = []
    edge_y_not_path = []

    #iterate through the edges in the subgraph
    for edge in subgraph.edges():
        #get the x and y coords of the starting node (where the edge beings)
        x0, y0 = position[edge[0]]
        #get the x and y coords of the ending node (where the edge ends)
        x1, y1 = position[edge[1]]
        #if both nodes of the edge are in the path
        if path and edge[0] in path and edge[1] in path:
            #append x coords of the start node and end node to the edge x list
            edge_x_path.append(x0)
            edge_x_path.append(x1)
            #create a space to separate the y coords
            edge_x_path.append(None)
            #append y coords of the start and end node to the edge y list
            edge_y_path.append(y0)
            edge_y_path.append(y1)
            #create a space for the next edge
            edge_y_path.append(None)
        #if the edge isn't in the path
        else:
            #append x coords of the start node and end node to the edge x list
            edge_x_not_path.append(x0)
            edge_x_not_path.append(x1)
            #create a space to separate the y coords
            edge_x_not_path.append(None)
            #append y coords of the start and end node to the edge y list
            edge_y_not_path.append(y0)
            edge_y_not_path.append(y1)
            #create a space for the next edge
            edge_y_not_path.append(None)
        
    #use Plotly's scatter to represent edges as lines
    #edges in path
    path_edges = pgo.Scatter(x=edge_x_path, y=edge_y_path, #x and y are coords for edges in path
                             line=dict(width=5, color='lightgreen'), #make thickness larger and color light green
                             hoverinfo='none', mode='lines') #mode is lines and no hovering text over edges
    #edges not in path
    non_path_edges = pgo.Scatter(x=edge_x_not_path, y=edge_y_not_path,#x and y are coords for edges not in path
                                 line=dict(width=0.5, color='gray'), #make thickness smaller and color gray
                                 hoverinfo='none', mode='lines') #mode is lines and no hovering text over edges

    #create Plotly lists for x and y node coords, the text of the node, the color of the node, and the size of the node
    node_x = []
    node_y = []
    node_text = []
    node_colors = []
    node_sizes = []
    #iterate through the nodes in the subgraph
    for node in subgraph.nodes():
        #get the x and y coords of the current node
        x, y = position[node]
        #append x coord to the node x list
        node_x.append(x)
        #append y coord to the node y list
        node_y.append(y)
        #add the node's title to the to node text list
        node_text.append(node)
        #add the node's color to the node colors list (light blue if not in path, light green if it is in path)
        node_colors.append('lightgreen' if path and node in path else 'lightblue')
        #add a degree factor that will make nodes larger if there are more degrees/edges
        #if there is only one degree
        if subgraph.degree(node) == 1:
            #then the degree factor is 0.25
            degree_factor = 0.25
        #otherwise
        else:
            #set the degree factor based on the number of degrees/edges
            degree_factor = 1-(1/(subgraph.degree(node)))
        #change size of nodes based on degree (how many edges are connected to the node), with larger sizes for nodes in the path
        node_sizes.append(75 if node in path else 50 * degree_factor)

    #use Ploty's scatter to represent nodes as points
    nodes = pgo.Scatter(x=node_x, y=node_y, #x and y are coords of node
                        mode='markers', hoverinfo='text', # mode is for markers (nodes), text should show when node is hovered over
                        marker=dict(color=node_colors, size=node_sizes), # use node colors list for the marker's (node) color and set a smaller size
                        text=node_text) # use node text list for text

    #create a graph with the nodes info, edges info, and networkx layout info
    figure = pgo.Figure(data=[path_edges,non_path_edges, nodes], #take in data of the edge (line) and node (marker) objects
                        layout=pgo.Layout(title='<br>Wikipedia Traversal Visualization', #add title, use <br> for spacing between title and plot
                        titlefont_size=16, showlegend=False, hovermode='closest', #set title size, don't show color legend, data will show for whatever is the closest when hovered over
                        margin=dict(b=0, l=0, r=0, t=50), #set top space to 50 for title versus plot space
                        xaxis=dict(showgrid=False, zeroline=False), #remove x and y axis grid lines and zero lines
                        yaxis=dict(showgrid=False, zeroline=False),
                        dragmode='zoom')) #enable zooming interaction so you can see closer
    
    #show the figure
    figure.show()

    '''
    #create a list of node colors
    node_colors = []
    #add colors depending on if its in the path or not
    for node in subgraph.nodes():
        #if the node is in the path and there is a path
        if path and node in path:
            #then add the color of the node to the list
            node_colors.append('red')
        #if the node isn't in the path
        else:
            #make remaining nodes light blue
            node_colors.append('lightblue')

    #find the positionings of the graph using a neato layout to show structure of graph
    position = graphviz_layout(graph, prog='neato')
    #make sure the figure is large
    plt.figure(figsize=(15,10))
    #draw the graph using networkx (added some customizations)
    nx.draw(subgraph, position, with_labels=True, node_color=node_colors, node_size=1000, font_size=9, edge_color='gray')
    #add a title to the plot
    plt.title("Wikipedia Traversal Graph (PyGraphviz)")
    #show the plot
    plt.show()
    '''

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

    #take in a string of heuristic names separated by commas
    heuristics_order = args.heuristics.split(',')
    #take in a string of heuristic steps separated by commas and create an integer list
    heuristic_steps = [int(step) for step in args.steps.split(',')]

    #collect a list of chosen heuristics with their steps
    heuristics_with_steps = []

    #for the names and steps of the combined tuple of lists (heuristic corresponding to the steps)
    for name, steps in zip(heuristics_order, heuristic_steps):
        #if the name inputted in is greedy
        if name == "greedy":
            #then append the heuristic greedy links function and greedy steps tuple into the list
            heuristics_with_steps.append((heuristics.greedy_links, steps))
        #if the name inputted in is tfidf
        elif name == "tfidf":
            #then append the heuristic tfidf links function and tfidf steps tuple into the list
            heuristics_with_steps.append((heuristics.tfidf, steps))
        #if the name inputted in is embeddings
        elif name == "embeddings":
            #then append the heuristic embeddings links function and embeddings steps tuple into the list
            heuristics_with_steps.append((heuristics.word_embeddings, steps))
        #if the name is invalid
        else:
            #then create an invalid print statement and return
            print(f"Invalid heuristic name: {name}")
            return
        
    '''
    #Heuristic function that will be passed into the search algorithm
    heuristic = None

    if(args.heuristic == "tfidf"): 
        heuristic = heuristics.tfidf
    elif(args.heuristic == "embeddings"): 
        heuristic = heuristics.word_embeddings
    elif(args.heuristic == "greedy"):
        heuristic = heuristics.greedy_links
    else: 
        print("Invalid heuristic, the options are: tfidf or embeddings")
        return
    '''
    
    #A* traversal with selected heuristics and step limits
    nodes_visited = traverse.astar(start_node, end_node, heuristics_with_steps)
    print(nodes_visited)

    # tfidf = heuristics.tfidf(start_node, end_node)
    # print("tfidf score: " + str(tfidf))

    # word_embeddings = heuristics.word_embeddings(start_node, end_node)
    # print("word embeddings score: " + str(word_embeddings))

    #Call the a star search here!
    # print(start_node.content)
    # start_node.generateNeighbors()
    # start_node.neighbors[19].generateNeighbors()
    # start_node.neighbors[19].neighbors[30].generateNeighbors()

    #Visualize the graph using the path and the start node
    visualize_graph(start_node, nodes_visited, max_nodes=None)
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Enter two wikipedia article titles to start and stop from! This will then find the shortest path")
    parser.add_argument("startTitle",
                        help='The title of the wikipedia page we are starting from')
    parser.add_argument("endTitle",
                        help='The title of the wikipedia page we want to end at')
    parser.add_argument("--heuristics", required=True,
                        help='comma separated list of heuristics in order')
    parser.add_argument("--steps", required=True, 
                        help='comma separated list of steps for each heuristic')
    args = parser.parse_args()
    main(args)





