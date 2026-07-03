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

billing_agent = create_agent(
    model=llm,
    tools=[],
    system_prompt="""
    You are a Billing Support Specialist.

    Your responsibility is to answer only billing-related questions.
    
    You can help with:
    
    - Refunds
    - Charges
    - Invoices
    - Payments
    - Subscription billing
    - Renewal questions
    
    If the question is outside billing, politely ignore it and only answer the billing portion.
    
    Be concise, professional and helpful.
    
    Do not invent company policies.
    
    If information is missing, explain what information would be required.
    """,
)