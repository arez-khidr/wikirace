from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import spacy

def greedy_links(current_node, target_node):
    #get a list of neighbors
    neighbors = current_node.neighbors

    #check if current node has direct links to the target article
    #iterate through each of the links
    for neighbor in neighbors:
        #if the link is the same as the target node's title
        if neighbor == target_node.title:
            #then go to the target node
            return target_node
    
    #if there isn't any direct links for either the current node or neighbor nodes, then choose the neighbor with the most links
    #if there are neighbors
    if neighbors:
        #then find the neighbor with the most links
        #iterate through each neighbor using lambda to find the neighbor with the most links (length of list neighbors' links)
        greedy_neighbor = max(neighbors, key=lambda n: len(n.links))
        #and return it
        return greedy_neighbor

    #if there aren't any neighbors, return nothing, as it is a dead end in the graph
    return None

def tfidf(current_node, target_node):
    #get the content from the current neighbor and the target node
    current_text = current_node.content
    target_text = target_node.content
    #create a list of the two texts that should be vectorized and compared
    compare_texts = [current_text, target_text]

    #create a TF-IDF vectorizer to convert data into TF-IDF vectors
    tfidf = TfidfVectorizer()

    #fit the vectorizer on both the current neighbor and target node's content by putting them into one list
    #builds a vocabulary list from both neighbor/target content
    #creates a TF-IDF matrix where each row represents a Wiki article in each column represents a word from the combined vocabulary
    tfidf_matrix = tfidf.fit_transform(compare_texts)
    #I want to see if it's giving a proper tfidf matrix
    #print(tfidf_matrix)

    #find the cosine similarity between the two vectors in the tfidf matrix (the current text and target text)
    #gives cosine similarity between every pair of docs (including themselves) in matrix format
    cosine_sim = cosine_similarity(tfidf_matrix)
    #I want to see if it's giving a proper cosine similarity matrix
    #print(cosine_sim)

    #return the value at index [0,1], which represents the similarity between the current neighbor's text and the target node's text (could also be [1,0], but [0,0] and [1,1] represents the cosine similarity of the exact same Wiki articles)
    #we return a 1 - cosine sim as for the a start algorithm the node with the lowest cost is at the top of hte heap
    return 1 - cosine_sim[0,1]

def word_embeddings(current_node, target_node):
    #load a large language model for word embeddings and assign it to nlp object
    nlp = spacy.load("en_core_web_lg")

    #get the titles from the current neighbor and the target node
    current_title = current_node.title
    target_title = target_node.title

    #create vector representations of the current title and target title
    ct_vector = nlp(current_title)
    tt_vector = nlp(target_title)

    #find the cosine similarity between the two vectorized objects with similarity() method
    cosine_similarity = ct_vector.similarity(tt_vector)

    #print(cosine_similarity)
    #return the cosine_similarity between the two vectorized titles (neighbor and target)
    return 1 - cosine_similarity
