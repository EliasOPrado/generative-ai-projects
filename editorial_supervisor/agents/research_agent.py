import logging
import os

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from tools.hardware_tools.check_warranty import check_warranty

from prompts.hardware_agent_prompt import HARDWARE_AGENT_PROMPT

logger = logging.getLogger(__name__)

load_dotenv()

llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0.7,
    api_key=os.getenv("OPENAI_API_KEY"),
)

hardware_agent = create_agent(
    model=llm,
    tools=[check_warranty],
    system_prompt = HARDWARE_AGENT_PROMPT
)