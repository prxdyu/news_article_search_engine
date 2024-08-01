""" THIS PYTHON FILE CONTAINS THE UTILITY FUNCTIONS """

# importing the required libraries
import pandas as pd
import numpy as np
from functools import reduce
import boto3
import os
import re
import tqdm
import pickle
import json

import spacy
from spacy.lang.en.stop_words import STOP_WORDS as spacy_stop_words
import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords as nltk_stop_words

# defining the lemmatizer and stopwords
STOP_WORDS = set(spacy_stop_words).union(set(nltk_stop_words.words("english")))
SPACY_TOKENIZER = spacy.load('en_core_web_sm')

""" # Load the .env file to access the environment variables
from dotenv import load_dotenv
load_dotenv() """

AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
REGION_NAME = os.getenv('REGION_NAME')

BUCKET_NAME = os.getenv('BUCKET_NAME')




# defining a function to get data from aws s3
def get_data_from_s3(filename,path):
    """ 
    downloads the raw data from aws

    filename  : the name of the file to download
    path      : the download path
    """

    # Configure boto3 to use your AWS credentials
    session = boto3.Session(
                        aws_access_key_id=AWS_ACCESS_KEY_ID,
                        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                        region_name=REGION_NAME
                            )
    # Create an S3 client
    s3 = session.client('s3')
    # Download the file
    s3.download_file(BUCKET_NAME, filename, path)
    return True


# defining a function to upload data to aws s3 bucket
def upload_to_s3(file_path,object_name=None):
    """
    file_path    : path of the file
    object_name  : what name to save the file in s3
    """
    # Configure boto3 to use your AWS credentials
    session = boto3.Session(
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=REGION_NAME
    )
    # Create an S3 client
    s3 = session.client('s3')
    # if the object name is not given then the filename is taken in default
    if object_name is None:
        object_name = file_path.split('/')[-1]

    try:
        s3.upload_file(file_path, BUCKET_NAME, object_name)
        return True
    except FileNotFoundError:
        print(f"The file {file_path} was not found")
    
    except Exception as e:
        print(f"An error occurred: {e}")
        


# defining a function to save the dictionary into a json 
def save_json(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f)


# defining a function to get embeddings from the model
def get_embeddings(model,sentences:list,mode:str="training",batch_size:int=32)->list:
    """
    model      : model to get embeddings from
    sentences  : list of sentences whose embeddings we want to get
    
    """
    embeddings = model.encode(sentences,show_progress_bar=False,device="cpu",batch_size=batch_size)
    return embeddings.tolist()


# defining a function which splits given article into paragraphs
def text_to_paragraphs(text:str)->list:
    """splits given article into paragraphs and returns list of paragraphs """
    # if the text is not a str then return an empty list
    if not isinstance(text, str):
        return []
    # split the text into paragraphs
    paragraphs = list(filter(lambda x: x!="", text.split("\n")))
    return paragraphs



def text_to_sentences(text:str)->list:
    """ splits the given text into sentences and returns a list of sentences """
    # if the text is not a str then return an empty list
    if not isinstance(text, str):
        return []
     # split the text into sentences
    sentences = SPACY_TOKENIZER(text).sents
    sentences = [str(sentence) for sentence in sentences]
    return sentences


# defining a function to seprarate capitalized words
def separate_capitalilzed_words(text:str)->str:
    """" 'ThisIsAWord' -> 'This Is A Word' """
    assert isinstance(text, str)
    text = re.sub(r"([a-z])([A-Z])", r"\1 \2", text)
    return text


# defining a function to preprocess the text
def preprocess_text(text:str)->str:
    """
    text : string to preprocess
    returns preprocessed text
    """
    # typecasting text to the str
    text = str(text)
    # separating the capitalized words
    text = separate_capitalilzed_words(text)
    # lowercasing all letters in the text
    text = text.lower()
    # removing non_alphanumeric elements
    pattern = '[^a-zA-Z0-9%\ \n]+'
    text = re.sub(pattern, '', text)
    # removing digits 
    text = re.sub(r'\d+', '', text)
    # fixing white spaces
    text = "\n".join(" ".join(text.split()).split("\n"))
    # removing stopwords
    text = " ".join([word for word in text.lower().split() if word not in STOP_WORDS])
    # tokenization
    text = " ".join([token.text for token in SPACY_TOKENIZER(text)])
    # lemmatization
    text = " ".join([token.lemma_ for token in SPACY_TOKENIZER(text)])
    
    return text






# defining a function to pre-process (splitting the article into sentences or paragraphs each split is called a section)
def preprocess_article(article_id:int,title:str,text:str,section_by:str="paragraph",input_type=['title','text'])->list:
    """
    article_id    : unique ID of the article
    title         : title of the article
    text          : text/body of the article
    section_by    : based on what we are going to split our article (eg: sentence,paragraph) default is by paragraph
    input_type   : which features are we going to consider eg: ['title'],['text'],['title','text'] default is ['title','text']
    
    """
    # if we are going to use only 'title' for generating embeddings
    if input_type==['title']:    
        sections = [preprocess_text(title)]
        
    # if we are going to use 'text' feature for generating embeddings
    elif input_type==['text']:    
        if section_by=="paragraph": # if we are going to split the text into paragraphs
            sections = text_to_paragraphs(text)
        elif section_by=="sentence":  # if we are going to split the text into sentences
            sections = text_to_sentences(text)
        elif section_by==None: # if we are not going to split
            sections = [text]
        else:
            raise ValueError("Invalid section_by value, it must be either 'paragraph' or 'sentence'.")
            
    # if we are going to use both 'title' and 'text' features
    elif input_type==['title','text']:
        if section_by=="paragraph":  # if we are going to split the text into paragraphs
            sections = text_to_paragraphs(text)
        elif section_by=="sentence":  # if we are going to split the text into sentences
            sections = text_to_sentences(text)
        elif section_by==None:
            sections = [text]
        else:
            raise ValueError("Invalid section_by value, it must be either 'paragraph' or 'sentence'.")
        # preprocessing the 'title'
        title = preprocess_text(title)
        # prprocessing the sections (text splitted into)
        section = list(map(preprocess_text,sections))
        # combining the 'title' and sections 
        sections = [title] + section
        # filtering the sentences which are greater than 2 words
        sections = list(filter(lambda x:len(x.split())>2,sections))

    # edge case
    else:
        raise ValueError("Invalid input_type value. Allowed values are ['title'], ['text'] and ['title', 'text']")

    # getting the no of splits 
    section_count = len(sections)

    return list(zip([article_id]*section_count,sections))  # [ (1,sections), (2,sections) ]








# defining a function which preprocess the data
def preprocess_data(data,section_by,input_type):
    
    """
    data            : dataframe with raw data
    section_by      : based on what we are going to split our article (eg: sentence,paragraph)
    input_type      : which features are we going to consider eg: ['title'],['text'],['title','text']
    
    """

    # if we don't want to split our article
    if section_by==None:
        
        if input_type==['title']:   # if we are going to use only title feature for embedding
            data = data[['article_id','title']]
            data['title'] = data['title'].apply(preprocess_text)  
        elif input_type==['text']:  # if we are going to use only text feature for embedding
            data = data[['article_id','text']]
            data['text'] = data['text'].apply(preprocess_text)
        else:  # if we want to use both title and text for embeddings
            a = list(reduce(lambda x, y: x+y, map(lambda x: [(x[0], preprocess_text(x[1])), (x[0], preprocess_text(x[2]))], tqdm.tqdm(data[["article_id", "title", "text"]].values, desc="Processing data", leave=True))))
            data = pd.DataFrame(a,columns=["article_id", "text"])


    # if we want to split the text by either parapgraph or sentence wise
    elif section_by=="paragraph" or section_by=="sentence":
            data = list(reduce(lambda x, y: x+y, map(lambda x: preprocess_article(x[0],x[1],x[2],section_by,input_type), tqdm.tqdm(data[["article_id", "title", "text"]].values, desc="Processing data", leave=True))))
            data = pd.DataFrame(data,columns=['article_id','text'])
    else:
        raise ValueError("Invalid section_by value. Allowed values are 'paragraph' and 'sentence' and None")
    
    # generating id for each splits
    data['section_id']= range(data.shape[0])

    # generating a mapping from article_id to section_id to find the article_id for a given section_id by creating  a dictionary where article_id is the key and corresponding section_ids is the value
    article_section_mapping = data.groupby('article_id')['section_id'].apply(list).to_dict()

    # generating a mapping from section_id to article_id to find the article_id of a given section_id by creating  a dictionary where section_id is the key and the corresponding article_id is the value
    section_article_mapping = data.set_index('section_id')['article_id'].to_dict()

    

    # Pickling the dictionaries
    article_section_mapping_path = 'artifacts/article_section_mapping.pkl'
    with open(article_section_mapping_path, 'wb') as f:
        pickle.dump(article_section_mapping, f)

    section_article_mapping_path = 'artifacts/section_article_mapping.pkl'
    with open(section_article_mapping_path, 'wb') as f:
        pickle.dump(section_article_mapping, f)

    

    return data,article_section_mapping_path,section_article_mapping_path

        
        
    
def get_article_meta_data(dff):
    """
    returns a dictionary where article_id is the key and its title,category and subcategory is the value
    """
    df = dff.copy()
    df = df.set_index('article_id')
    df = df[['title','category','subcategory']]
    return dict(zip(  list(df.index),df.values.tolist() ))
