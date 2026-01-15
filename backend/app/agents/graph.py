from langgraph.graph import StateGraph
from typing import TypedDict, List

class State(TypedDict):
    query: str
    contexts: List[dict]
    answer: str
    verified: bool

def intent_node(state: State):
    return state

def retrieve_node(state: State):
    from app.services.vector_store import query
    res = query(state["query"], n_results=5)
    ctx = []
    for doc, meta in zip(res["documents"][0], res["metadatas"][0]):
        ctx.append({"text": doc, "path": meta["path"]})
    return {**state, "contexts": ctx}

def explain_node(state: State):
    if not state["contexts"]:
        return {**state, "answer": "Not enough context", "verified": False}

    answer = "Explanation based on files: \n" + "\n".join(c["path"] for c in state["contexts"])
    return {**state, "answer": answer, "verified": True}

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