# defining based on what we are going to split our article (eg: sentence,paragraph)
SECTION_BY =  "sentence"

# defining which features are we going to consider eg: ['title'],['text'],['title','text']
INPUT_TYPE = ['title','text']

# defining the model to get embeddings
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# defining the embedding size
EMBEDDING_SIZE = 384

# defining the similarity metric 
ANNOY_METRIC = 'euclidean'

# defining the depth of ANNOY tree
ANNOY_N_TREE = 50

# defining the threshold score 
THRESHOLD_SCORE = 0.4