import os
import logging
from dotenv import load_dotenv
from typing import List
from pydantic import BaseModel, Field
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import JsonOutputParser

logger = logging.getLogger(__name__)

load_dotenv()

llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0.7,
    api_key=os.getenv("OPENAI_API_KEY"),
)

technical_agent = create_agent(
    model=llm,
    tools=[],
    system_prompt="""
    You are a Technical Support Specialist.

    Your responsibility is to solve technical problems.
    
    You can help with:
    
    - Login problems
    - Password reset
    - Errors
    - Bugs
    - Website issues
    - Mobile app issues
    - API issues
    - Performance issues
    
    Think step by step before proposing a solution.
    
    If more information is required, ask clear troubleshooting questions.
    
    Do not answer billing or sales questions.
    """,
)