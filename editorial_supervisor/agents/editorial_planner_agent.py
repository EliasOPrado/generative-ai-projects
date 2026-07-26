import logging
import os
from typing import List

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from langchain_core.output_parsers import JsonOutputParser
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from prompts.general_agent_prompt import GENERAL_AGENT_PROMPT

logger = logging.getLogger(__name__)

load_dotenv()

llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0.7,
    api_key=os.getenv("OPENAI_API_KEY"),
)

general_agent = create_agent(
    model=llm,
    tools=[],
    system_prompt=GENERAL_AGENT_PROMPT,
)