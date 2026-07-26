import logging
import os

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from tools.hardware_tools.check_warranty import check_warranty

from editorial_supervisor.prompts.wordpress_publisher_agent_prompt import WORDPRESS_PUBLISHER_AGENT_PROMPT

logger = logging.getLogger(__name__)

load_dotenv()

llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0.7,
    api_key=os.getenv("OPENAI_API_KEY"),
)

wordpress_publisher_agent = create_agent(
    model=llm,
    tools=[check_warranty],
    system_prompt = WORDPRESS_PUBLISHER_AGENT_PROMPT
)