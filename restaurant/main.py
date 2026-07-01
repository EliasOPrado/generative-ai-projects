import logging
from pydantic import BaseModel
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse

from agents.menu_agent import menu_agent
from langchain_core.messages import HumanMessage

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

"""
TODO:

1. For each agent create its own endpoint (check whether it is neccessary indeed).
2. Create the supervisor with langgraph and export into the main Fastapi function..
"""

class InputData(BaseModel):
    user_input: str

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/receive-human-input")
async def receive_human_input(input_data: InputData):
    """
    This method is responsible for receiving user input from the frontend.
    """

    if not input_data.user_input:
        return JSONResponse(content={"error": "Campo 'user_input' e obrigatório"}, status_code=400)

    user_input = input_data.user_input
    try:
        resultado = menu_agent.invoke(
            {"messages": [HumanMessage(content=user_input)]}
        )
        mensagem_ia = resultado["messages"][-1]
        return {"resposta": mensagem_ia.content}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))