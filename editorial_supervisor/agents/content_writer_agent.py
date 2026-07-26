import logging
import os

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI

from editorial_supervisor.prompts.content_writer_agent_prompt import CONTENT_WRITER_AGENT_PROMPT

logger = logging.getLogger(__name__)

load_dotenv()

llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0.7,
    api_key=os.getenv("OPENAI_API_KEY"),
)

content_writer_agent = create_agent(
    model=llm,
    tools=[],
    system_prompt = CONTENT_WRITER_AGENT_PROMPT
)