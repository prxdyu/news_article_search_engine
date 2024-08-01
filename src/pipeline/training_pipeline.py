import os
import sys
from src.logger.logger import logging
from src.exception.exception import CustomException
import pandas as pd

from src.components.data_ingestion import DataIngestion
from src.components.data_preprocessing import DataPreProcessing
from src.components.embedding_generation import EmbeddingGeneration
from src.components.annoy_indexing import AnnoyIndexer



# creating object for data ingestion    
data_ingestion = DataIngestion()
raw_data_path  = data_ingestion.initiate_data_ingestion()

# creating object for data preprocessing
data_transformation = DataPreProcessing()
processed_data_path = data_transformation.initiate_data_processing(raw_data_path)

# creating an object for embedding generation
embedding_generation = EmbeddingGeneration()
embeddings_path = embedding_generation.initiate_embedding_generation(processed_data_path)

# creating an object for indexing
indexing = AnnoyIndexer()
index_path = indexing.build_index(embeddings_path)