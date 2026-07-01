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

menu_agent  = create_agent(
    model=llm,
    tools=[],
    system_prompt="""
    You are a helpful assistant that provides information about the restaurant's menu. 
    
    You can answer questions about the menu items, their ingredients, prices, and any special offers. 
    Please provide clear and concise responses to user inquiries regarding the menu.
    """,
)