import opener
from heapq import *
'''File that creates the functions for graph traversals'''

#Retraces the node to generate the path of nodes! 
def retrace(node): 
    #retrances back a current node and creates a list of the path needed to be taken
    #Current node should be the wikinode object of the end node! 
    #Be sure that once traversal is finished we assign it the proper stuff
    node_list = []
    current_node = node
    node_list.append(current_node.title)
    
    while current_node.parent is not None: 
        node_list.append(current_node.parent.title)
        current_node = current_node.parent

    #reverse the order of the list 
    node_list.reverse()

    #return the list of all the moves!
    
    return node_list

def astar(start_node, target_node, heuristic):
    '''a star traversal algorithm for going through the graph
    The heuristic here is set by one that is passed in!'''
    #Heuristic is the method that we are passing in!

    #Let the open list be an empty priotity q of nodes
    openList = []
    #let closed list equal an empty colelction of nodes
    closedList = {}

    #put the start node on the openlist and the closed list 
    #We are going to have titles be the indicator of the nodes we want
    start_title = start_node.title
    goal_title = target_node.title

    nodeObject = start_node
    heappush(openList, nodeObject)
    #Add the start node to the closed list, the position is the key, the value is object
    closedList[start_title] = nodeObject

    #While the openlist is not empty
    while openList:
        current_node = heappop(openList)
        print("Current Node is: " + current_node.title)
        current_node.generateNeighbors()
        #List comp to get all the titles of the nodes we want
        neighbor_titles = [node.title for node in current_node.neighbors]
        #Generate the neighbors for the current node beforehand to check its neighbors!
        if goal_title in neighbor_titles: 
            #Retrace to the node that has the goal title
            i = neighbor_titles.index(goal_title)
            retrace_node = current_node.neighbors[i]
            moves = retrace(retrace_node)
            #Moves is just a list of all the nodes visited to get to target title
            return moves
        else: 
            #Check for all the neighbors
            for neighbor_node in current_node.neighbors:
                #The Neighbors are already instantiated wiki node objects we just need to change their cost and steps
                neighbor_node.cost = current_node.steps + 1 + heuristic(neighbor_node, target_node)
                neighbor_node.steps = current_node.steps + 1
                if neighbor_node.title not in closedList or closedList[neighbor_node.title].cost > neighbor_node.cost: 
                    #Add the neighbor and its cost to the closed list
                    #Enqueu the neighbor into the open list
                    closedList[neighbor_node.title] = neighbor_node
                    heappush(openList, neighbor_node)

    #Error where we reached a crazy situation with orphan nodes or dead ends
    return -1