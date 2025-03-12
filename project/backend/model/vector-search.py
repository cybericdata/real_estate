from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

import pandas as pd
import os
import logging
from dotenv import load_dotenv


OPEN_AI_KEY = os.getenv("OPEN_AI_KEY")

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

def convert_to_text_file(csv_file="house_cleaned.csv", output_file="tagged_description.txt"):
    try:
        houses = pd.read_csv(csv_file)
        houses['tagged_description'].to_csv(output_file, sep = '\n', index=False, header=False)
        logging.info(f"Text file '{output_file}' created successfully.")
    except Exception as e:
        logging.error(f"Error converting CSV to text: {e}")

def text_splitter(input_file="tagged_description.txt"):
    try:    
        raw_documents = TextLoader(input_file).load()
        text_splitter = CharacterTextSplitter(chunk_size=0, chunk_overlap=0, separator="\n")
        documents = text_splitter.split_documents(raw_documents)
        logging.info(f"Successfully split text into {len(documents)} documents.")
        return documents
    except Exception as e:
        logging.error(f"Error splitting text: {e}")
        return []


def embedding_text(documents):
    try:
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
        house_vector_db = Chroma(embedding_function=embeddings)
        house_vector_db.add_documents(documents=documents)
        logging.info("Documents successfully embedded in vector database.")
        return house_vector_db
    except Exception as e:
        logging.error(f"Error embedding text: {e}")
        return None

def main():
    convert_to_text_file()
    splitted_document = text_splitter()
    if not splitted_document:  # Check if documents were successfully split
        logging.error("No documents to embed. Exiting...")
        return
    
    house_db = embedding_text(splitted_document)

    if house_db:
        query = "Where can I get a house in Maitama?"
        results = house_db.similarity_search(query, k=10)
        logging.info(f"Top 10 search results:\n{results}")
    else:
        logging.error("Vector database creation failed.")


if __name__ == "__main__":
    main()