from langgraph.graph import StateGraph
from typing import TypedDict, List
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import os
from dotenv import load_dotenv

load_dotenv()

llm = ChatOpenAI(
    model="gpt-5-mini",
    temperature=0.1,
    api_key=os.getenv("OPENAI_API_KEY")
)

prompt_template = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful code analysis assistant. Answer questions based on the provided code context."),
    ("user", "Query: {query}\n\nCode Context:\n{context}\n\nPlease provide a clear, accurate answer based on the code provided.")
])

chain = prompt_template | llm | StrOutputParser()

class State(TypedDict):
    query: str
    contexts: List[dict]
    answer: str
    verified: bool
    repo_id: str 

def intent_node(state: State):
    return state

def retrieve_node(state: State):
    from app.services.vector_store import query
    
    repo_id = state.get("repo_id")
    res = query(state["query"], n_results=5, repo_id=repo_id)
    
    ctx = []
    for doc, meta in zip(res["documents"][0], res["metadatas"][0]):
        ctx.append({"text": doc, "path": meta["path"]})
    return {**state, "contexts": ctx}

def explain_node(state: State):
    if not state["contexts"]:
        return {**state, "answer": "Not enough context", "verified": False}

    context_text = "\n\n".join([
        f"File: {ctx['path']}\n{ctx['text']}" 
        for ctx in state["contexts"]
    ])
    
    try:
        answer = chain.invoke({
            "query": state["query"],
            "context": context_text
        })
        
        return {**state, "answer": answer, "verified": True}
        
    except Exception as e:
        return {**state, "answer": f"Error generating explanation: {str(e)}", "verified": False}

def verify_node(state: State):
    if not state["verified"]:
        state["answer"] = "I don't have enough information from the codebase to answer confidently"
    
    return state


graph = StateGraph(State)
graph.add_node("intent", intent_node)
graph.add_node("retrieve", retrieve_node)
graph.add_node("explain", explain_node)
graph.add_node("verify", verify_node)

graph.set_entry_point("intent")
graph.add_edge("intent", "retrieve")
graph.add_edge("retrieve", "explain")
graph.add_edge("explain", "verify")

app = graph.compile()