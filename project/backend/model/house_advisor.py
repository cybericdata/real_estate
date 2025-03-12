from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import hashlib
import logging
from dotenv import load_dotenv
import pandas as pd

from langchain_community.document_loaders import TextLoader, DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain.prompts import PromptTemplate
from langchain.chat_models import init_chat_model
from langchain.chains.summarize import load_summarize_chain
from langchain.schema import AIMessage

# Load environment variables
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY is not set in the environment.")

# Initialize FastAPI
app = FastAPI(title="LLM API", description="FastAPI wrapper for LLM-powered AI Assistant", version="1.0")

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

llm = init_chat_model("llama-3.3-70b-versatile", model_provider="groq")

template = """You are an AI real-estate agent assistant. Answer the following question in a well-structured way.
Use the extra context provided if relevant.

Context: {context}

User Query: {question}

AI Response:"""

prompt = PromptTemplate(input_variables=["context", "question"], template=template)

def enrich_prompt(query, context):
    return prompt.format(context=context, question=query)

# File hashing to check for changes
def hash_file(filepath):
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        hasher.update(f.read())
    return hasher.hexdigest()

def load_text_data(directory):
    loader = DirectoryLoader(directory, glob="*.txt", loader_cls=TextLoader)
    documents = loader.load()

    # Track file hashes
    hash_file_path = "file_hashes.json"
    file_hashes = {}
    
    if os.path.exists(hash_file_path):
        file_hashes = pd.read_json(hash_file_path, typ="series").to_dict()

    new_documents = []
    updated_hashes = {}

    for doc in documents:
        file_path = doc.metadata["source"]
        file_hash = hash_file(file_path)

        if file_path not in file_hashes or file_hashes[file_path] != file_hash:
            new_documents.append(doc)
            updated_hashes[file_path] = file_hash

    # Save updated hashes
    if updated_hashes:
        pd.Series(updated_hashes).to_json(hash_file_path)
    
    return new_documents

documents = load_text_data("./data")

if documents:
    logging.info(f"Found {len(documents)} new/updated documents. Processing embeddings...")

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    chunks = splitter.split_documents(documents)

    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    vector_store = Chroma(persist_directory="./chroma_db", embedding_function=embeddings)

    vector_store.add_documents(chunks)
    vector_store
else:
    logging.info("No new documents found. Using existing embeddings.")
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vector_store = Chroma(persist_directory="./chroma_db", embedding_function=embeddings)

def semantic_search(query, top_k=10):
    results = vector_store.similarity_search(query, top_k)
    return results[0].page_content if results else ""

# Load summarization chain
summarizer = load_summarize_chain(llm, chain_type="map_reduce")

def summarize_text(text):
    return summarizer.run([Document(page_content=text)])

def generative_ai_pipeline(user_query):
    context = semantic_search(user_query)
    enriched_prompt = enrich_prompt(user_query, context)
    response = llm.invoke(enriched_prompt)
    
    if isinstance(response, AIMessage):
        response_text = response.content  # Extract actual text
    else:
        response_text = str(response)
    
    summary = summarize_text(response_text)

    return {"full_response": response.content, "summary": summary}


# API Request Model
class QueryRequest(BaseModel):
    query: str

@app.post("/ask")
async def ask_llm(request: QueryRequest):
    try:
        response = generative_ai_pipeline(request.query)
        return {"query": request.query, "response": response["full_response"], "summary": response["summary"]}
    except Exception as e:
        logging.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "Welcome to the Real-Estate Agent LLM API! Use /ask to interact with the model."}

#uvicorn house_advisor:app --host 0.0.0.0 --port 9000 --reload
