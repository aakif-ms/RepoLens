from fastapi import APIRouter
from pydantic import BaseModel
from app.agents.graph import app

router = APIRouter(prefix="/ask")

class AskReq(BaseModel):
    q: str

@router.post("/")
def ask(req: AskReq):
    state = {"query": req.q, "contexts": [], "answer": "", "verified": False}
    return app.invoke(state)