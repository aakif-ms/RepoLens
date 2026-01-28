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
    
def query(query_text: str, n_results: int = 5, repo_id: str = None):
    where_filter = None
    if repo_id:
        where_filter = {"repo_id": {"$eq": repo_id}}
    
    results = collection.query(
        query_texts=[query_text],
        n_results=n_results,
        where=where_filter
    )
    print(f"collection count: {collection.count()}")
    if repo_id:
        print(f"querying for repo_id: {repo_id}")
    return results