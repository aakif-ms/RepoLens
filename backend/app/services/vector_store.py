import chromadb
from chromadb.utils import embedding_functions

client = chromadb.Client()
collection = client.get_or_create_collection(name="repolens_files")

def upsert(doc_id: str, text: str, metadata: dict):
    collection.upsert(
        ids=[doc_id],
        documents=[text],
        metadatas=[metadata]
    )
    
def query(query_text: str, n_results: int = 5):
    return collection.query(
        query_texts=[query_text],
        n_results=n_results
    )