
import os

import logging
from operator import add
from typing import Annotated
from dotenv import load_dotenv
from typing_extensions import TypedDict
from langchain_openai import ChatOpenAI
from typing import List
from pydantic import BaseModel, Field
from langgraph.types import Send
from langgraph.graph import StateGraph, START, END
from agents.menu_agent import menu_agent
from agents.reservation_agent import  reservation_agent

logger = logging.getLogger(__name__)

load_dotenv()

llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0.7,
    api_key=os.getenv("OPENAI_API_KEY"),
)

class RestaurantState(TypedDict):
    query: str
    agents: List[str]
    answers: Annotated[list[str], add]
    final_answer: str

class RouterOutput(BaseModel):
    agents: List[str] = Field(
        description="Lista de agentes relevantes para a pergunta do usuário. "
    )

class RestaurantAgent:

    def __init__(self):
        self.logging = logger
        self.graph = StateGraph(RestaurantState)

        self.graph.add_node(
            "classify",
            self.classify_user_intention,
        )

        self.graph.add_node(
            "menu_agent",
            self.menu_agent_node,
        )

        self.graph.add_node(
            "reservation_agent",
            self.reservation_agent_node,
        )

        self.graph.add_node(
            "merge",
            self.merge_results,
        )

        self.graph.add_edge(START, "classify")

        self.graph.add_conditional_edges(
            "classify",
            self.route,
        )

        self.graph.add_edge("menu_agent", "merge")
        self.graph.add_edge("reservation_agent", "merge")

        self.graph.add_edge("merge", END)

        self.app = self.graph.compile()

    def menu_agent_node(self, state: RestaurantState):
        self.logging.info(" Went to 'menu_agent_node'")
        answer = menu_agent.invoke({
            "query": state["query"],
        })

        ai_message = answer["messages"][-1]

        return {
            "answers": [
                ai_message.content
            ]
        }

    def reservation_agent_node(self, state: RestaurantState):
        self.logging.info(" Went to 'reservation_agent_node'")
        answer = reservation_agent.invoke({
            "query": state["query"],
        })

        ai_message = answer["messages"][-1]

        return {
            "answers": [
                ai_message.content
            ]
        }

    def classify_user_intention(self, state: RestaurantState):
        self.logging.info("Start the agent classification.")
        prompt = f"""
        You are a restaurant supervisor.

        Available agents:

        - menu_agent
        - reservation_agent
        
        Select every agent required to answer the user's request.

        Return only the agent names.
        
        Examples:
        
        User:
        I'd like today's menu.
        
        Output:
        ["menu_agent"]
        
        User:
        I'd like to reserve a table.
        
        Output:
        ["reservation_agent"]
        
        User:
        I'd like today's menu and reserve a table.
        
        Output:
        ["menu_agent", "reservation_agent"]

        User request:

        {state["query"]}

        Return every agent needed.
        """

        router = llm.with_structured_output(RouterOutput)

        result = router.invoke(prompt)

        return {
            "agents": result.agents
        }

    def route(self, state: RestaurantState):
        self.logging.info(" Start the agent route.")
        return [
            Send(agent, state)
            for agent in state["agents"]
        ]

    def merge_results(self, state: RestaurantState):
        self.logging.info(" Start the agent merge.")
        return {
            "final_answer": "\n\n".join(state["answers"])
        }

    def execute_supervisor(self, user_input: str):
        self.logging.info("Start the supervisor.")

        input_state: RestaurantState = {
            "query": user_input,
            "agents": [],
            "answers": [],
            "final_answer": ""
        }

        result = self.app.invoke(input_state)

        return result["final_answer"]