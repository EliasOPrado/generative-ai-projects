import logging
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException

from supervisor.graph import ITHelpDeskSupervisorAgent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

supervisor = ITHelpDeskSupervisorAgent()

class ChatRequest(BaseModel):
    message: str
    thread_id: str

@app.post("/chat")
async def chat(request: ChatRequest):

    logger.info(f"Input data: {request.message} and thread id: {request.thread_id}")

    if not request.message:
        raise HTTPException(
            status_code=400,
            detail="User input is required",
        )

    try:
        logger.info("Sending message query.")
        answer = supervisor.execute_supervisor(
            user_input=request.message,
            thread_id=request.thread_id,
        )

        logger.info("Answer received.")
        return {
            "response": answer,
        }
    except Exception as e:
        logger.exception(e)
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )