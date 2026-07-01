import logging
from pydantic import BaseModel
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse

# from agents.menu_agent import menu_agent
# from langchain_core.messages import HumanMessage

from supervisor.graph import RestaurantAgent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

supervisor = RestaurantAgent()

class InputData(BaseModel):
    user_input: str

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/chat")
async def receive_human_input(input_data: InputData):

    if not input_data.user_input:
        raise HTTPException(
            status_code=400,
            detail="user_input is required."
        )

    try:

        answer = supervisor.execute_supervisor(
            input_data.user_input
        )

        return {
            "response": answer
        }

    except Exception as e:
        logger.exception(e)
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )