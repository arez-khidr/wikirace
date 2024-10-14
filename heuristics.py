from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import spacy
import string

nlp = spacy.load("en_core_web_lg")

def greedy_links(current_node, target_node):
    #get a list of neighbors
    # neighbors = current_node.neighbors

    # # #check if current node has direct links to the target article
    # # #iterate through each of the links
    # # for neighbor in neighbors:
    # #     #if the link is the same as the target node's title
    # #     if neighbor.title == target_node.title:
    # #         #then go to the target node
    # #         return target_node
    
    # #if there isn't any direct links for either the current node or neighbor nodes, then choose the neighbor with the most links
    # #if there are neighbors
    # if neighbors:
    #     #then find the neighbor with the most links
    #     #iterate through each neighbor using lambda to find the neighbor with the most links (length of list neighbors' links)
    #     for link in neighbors:
    #         print(f"Amount of links for {neighbor}: {len(neighbor.links)}")
    #     greedy_neighbor = max(neighbors, key=lambda n: len(n.links))
    #     #find the amount of links from the greedy neighbor
    #     links = len(greedy_neighbor.links)
    #     print(f"Amount of links for greedy neighbor {greedy_neighbor}: {links}")
    #     #divide the amount of links by 1 to inverse the amount (cost should be low)
    #     links_cost = 1/links
    #     #and return it
    #     return links_cost

    # #if there aren't any neighbors, return nothing, as it is a dead end in the graph
    # return None

    return 1/len(current_node.links)

def tfidf(current_node, target_node):
    #get the content from the current neighbor and the target node
    current_text = preprocess_text(current_node.content, True)
    target_text = preprocess_text(target_node.content, True)

    #create a list of the two texts that should be vectorized and compared
    compare_texts = [current_text, target_text]

    #create a TF-IDF vectorizer to convert data into TF-IDF vectors
    #add stop words so that common words like 'the' are not included in the tfidf when vectorizing (another part of preprocessing)
    tfidf = TfidfVectorizer(stop_words='english')

    #fit the vectorizer on both the current neighbor and target node's content by putting them into one list
    #builds a vocabulary list from both neighbor/target content
    #creates a TF-IDF matrix where each row represents a Wiki article in each column represents a word from the combined vocabulary
    tfidf_matrix = tfidf.fit_transform(compare_texts)

    #change the matrix into an array so it can be used more easily
    #each row is one of the input texts and each column is a specific word from the combined vocab of both texts
    tfidf_scores = tfidf_matrix.toarray()

    #get the feature names (words) for the vectorizer so I can find each word and their corresponding tfidf value
    words = tfidf.get_feature_names_out()

    #create a list of word-tfidf tuple pairs
    word_score_pairs = list(zip(words, tfidf_scores[0]))

    #sort the list based on the scores in descending order (getting the second element (tfidf scores) from each tuple and compare to one another)
    sorted_wsp = sorted(word_score_pairs, key=lambda x: x[1], reverse=True)

    #get the top 3 words with the highest tfidf scores from the sorted list
    top_3 = sorted_wsp[:3]

    #finds the words and their corresponding scores so we can see which one it chooses out of this list
    print(f"TF-IDF values for top 3 words in current article {current_node.title}: ")
    for word, score in top_3:
        #if the score is over 0 (sparse matrix so many will just be equal to 0)
        if score > 0.0:
            print(f"{word}: {score}")
    
    #find the cosine similarity between the two tfidf vectors (current and target articles)
    similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])

    #get the tfidf cost, which is the opposite of the similiarity score, since cost is good when it's low
    tfidf_cost = 1 - similarity

    #return tfidf cost
    return tfidf_cost

    '''
    #find the highest tfidf score from the current code's content, which is the most important word when compared to the target node
    #use .max() to find the max value for current_text (zeroth row of array)
    highest_tfidf_score = tfidf_scores[0].max()
    print(f"Highest TF-IDF score: {highest_tfidf_score}")

    #if the highest tfidf score is 0, then avoid division by 0 (there should be a number though) so code doesn't crash
    if highest_tfidf_score == 0:
        #avoid division by 0
        return float('inf')
    #otherwise
    else:
        #subtract the highest tfidf score from 1 to get the cost (must be low, so subtract from 1)
        tfidf_cost = 1 - highest_tfidf_score
    #return cost
    return tfidf_cost
    '''

def word_embeddings(current_node, target_node):
    #get the titles from the current neighbor and the target node and preprocess to lessen noise
    current_title = preprocess_text(current_node.title, False)
    target_title = preprocess_text(target_node.title, False)

    #create vector representations of the current title and target title
    ct_vector = nlp(current_title)
    tt_vector = nlp(target_title)

    #find the cosine similarity between the two vectorized objects with similarity() method
    cosine_similarity = ct_vector.similarity(tt_vector)
    #print(cosine_similarity)
    #get the cost of the cosine similarity between two vectorized titles (current and target) by subtracting it by 1
    wb_cost = 1 - cosine_similarity
    #return cost
    return wb_cost

def preprocess_text(text, lemmatize = False):
    #remove punctuation by joining the resulting list of characters that aren't punctuation (encapsulated by string.punctuation)
    text = ''.join([char for char in text if char not in string.punctuation])
    
    #lowercase all the text
    text = text.lower()

    #remove extra spaces
    text = ' '.join(text.split())

    #if the text should be lemmatized
    if lemmatize: 
        #lemmatize/tokenize the text with spacy's large language model
        #process text into tokens
        text = nlp(text)
        #join the extracted lemmatized tokens (use .lemma_ to find the lemma of the tokens) back into text
        text = ' '.join([token.lemma_ for token in text])

    #return text
    return text

