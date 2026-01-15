import chromadb
import os
from chromadb.utils import embedding_functions
from dotenv import load_dotenv

load_dotenv()

embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

client = chromadb.Client()
collection = client.get_or_create_collection(name="repolens_files", embedding_function=embedding_fn)

def upsert(doc_id: str, text: str, metadata: dict):
    collection.upsert(
        ids=[doc_id],
        documents=[text],
        metadatas=[metadata]
    )
    print(f"Upserted documents with id: {doc_id}")
    
def query(query_text: str, n_results: int = 5):
    results = collection.query(
                query_texts=[query_text],
                n_results=n_results)
    print(f"collection count: {collection.count()}")
    return results