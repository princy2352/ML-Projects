from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from qna import nlp_qna  # Assuming this is your Q&A model
from typing import Dict, Any
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# Serve static files like favicon.ico
#app.mount("/static", StaticFiles(directory="static"), name="static")

# Root route
@app.get("/")
async def read_root():
    return {"message": "FastAPI is running!"}

class QARequest(BaseModel):
    context: str
    question: str

class QAResponse(BaseModel):
    response: str

# Endpoint to handle POST requests to /qna
@app.post("/qna/")
async def qna(qa_request: QARequest):
    print(qa_request)
    result = nlp_qna(qa_request.context, qa_request.question)
    return {"answer": result}
