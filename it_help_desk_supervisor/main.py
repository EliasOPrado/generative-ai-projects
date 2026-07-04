import logging
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException

from supervisor.graph import ITHelpDeskSupervisorAgent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

supervisor = ITHelpDeskSupervisorAgent()

class InputData(BaseModel):
    user_input: str

@app.post("/chat")
async def chat(input_data: InputData):

    logger.info(f"Input data: {input_data}")

    if not input_data.user_input:
        raise HTTPException(
            status_code=400,
            detail="User input is required",
        )

    try:
        logger.info("Sending message query.")
        answer = supervisor.execute_supervisor(
            user_input=input_data.user_input
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