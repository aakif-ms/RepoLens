import uuid
import json
from dotenv import load_dotenv
from datetime import datetime
from typing import Dict, List, AsyncGenerator
from langchain_openai import ChatOpenAI
from langchain_core.messages import (HumanMessage, AIMessage, SystemMessage)
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory


load_dotenv()

class ChatServices:
    def __init__(self):
        self.sessions: Dict[str, dict] = {}
        
        self.llm = ChatOpenAI(
            model="gpt-5-mini",
            temperature=0.1,
            streaming=True
        )
        
    def create_session(self, repo_id: str) -> str:
        session_id = str(uuid.uuid4())
        
        self.sessions[session_id] = {
            "repo_id": repo_id,
            "created_at": datetime.now(),
            "history": InMemoryChatMessageHistory(),
            "messages": []
        }
        
        return session_id
        
    def get_session(self, session_id: str) -> dict:
        return self.sessions.get(session_id)

    def add_message_to_session(self, session_id: str, role: str, content: str):
        session = self.get_session(session_id)
        if not session:
            return

        session["messages"].append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        
        history = session["history"]

        if role == "user":
            history.add_message(HumanMessage(content=content))
        elif role == "assistant":
            history.add_message(AIMessage(content=content))
        
    
    async def stream_chat_response(self, session_id: str, user_message: str) -> AsyncGenerator[str, None]:
        session = self.get_session(session_id)
        if not session:
            yield json.dumps({"error": "Session not found"})
            return
        
        self.add_message_to_session(session_id, "user", user_message)
        
        context = self.get_repo_context(session["repo_id"])
        
        system_message = SystemMessage(
            content=f"""
            You are a helpful AI assistant that answers questions about a code repository.

            Repository context:
            {context}

            Answer clearly and reference code when relevant.
            """
        )
        
        history = session["history"]

        runnable = RunnableWithMessageHistory(
            runnable=self.llm,
            get_session_history=lambda _: history
        )
        
        full_response = ""
        
        try:
            async for chunk in runnable.astream(
                [system_message, HumanMessage(content=user_message)],
                config={"configurable": {"session_id": session_id}},
            ):
                if chunk.content:
                    full_response += chunk.content
                    yield json.dumps({"content": chunk.content})

            self.add_message_to_session(session_id, "assistant", full_response)
        
        except Exception as e:
            yield json.dumps({"error": str(e)})
            
    def get_repo_context(self, repo_id: str) -> str:
        return f"Repository context for {repo_id}"

    def get_chat_history(self, session_id: str) -> List[dict]:
        session = self.get_session(session_id)
        return session["messages"] if session else []
    
chat_service = ChatServices()