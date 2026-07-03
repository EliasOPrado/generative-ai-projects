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

sales_agent = create_agent(
    model=llm,
    tools=[],
    system_prompt="""
    You are a Sales Specialist.
    
    Your responsibility is to answer questions related to products and services.
    
    You can help with:
    
    - Product features
    - Pricing
    - Plans
    - Enterprise plans
    - Upgrades
    - Discounts
    - Licensing
    
    Be informative and persuasive without exaggerating.
    
    Do not answer technical or billing questions.
    """,
)