import os
import logging
from operator import add
from typing import Annotated, List, TypedDict

from agents.general_agent import general_agent
from agents.hardware_agent import hardware_agent
from agents.software_agent import software_agent

from dotenv import load_dotenv

from langgraph.types import Send
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph
from langgraph.checkpoint.memory import InMemorySaver
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage

from pydantic import BaseModel, Field
from prompts.supervisor_prompt import SUPERVISOR_PROMPT

logging.basicConfig()
logger = logging.getLogger()

load_dotenv()

llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0.7,
    api_key=os.getenv("OPENAI_API_KEY"),
)


class RouterOutput(BaseModel):
    agents: List[str] = Field(
        description="Agent list placed by supervisor classification."
    )


class HelpDeskState(TypedDict):
    query: str
    messages: Annotated[List[BaseMessage], add]
    agents: List[str]
    answers: Annotated[List[str], add]
    final_answer: str


class ITHelpDeskSupervisorAgent:

    def __init__(self):
        self.logging = logger
        self.graph = StateGraph(HelpDeskState)
        self.graph.add_node("hardware_agent", self.hardware_agent_node)
        self.graph.add_node("software_agent", self.software_agent_node)
        self.graph.add_node("general_agent", self.general_agent_node)
        self.graph.add_node("classify", self.classify_user_intention)
        self.graph.add_node("route", self.route)
        self.graph.add_node("merge", self.merge)

        self.graph.add_edge(START, "classify")
        self.graph.add_conditional_edges("classify", self.route)

        self.graph.add_edge("hardware_agent", "merge")
        self.graph.add_edge("software_agent", "merge")
        self.graph.add_edge("general_agent", "merge")

        self.graph.add_edge("merge", END)


        memory = InMemorySaver()

        self.app = self.graph.compile(checkpointer=memory)

    def classify_user_intention(self, state: HelpDeskState):

        self.logging.info(" Starting the user intention classification.")

        # The {messages} into the prompt will receive the state["messages"]
        prompt = SUPERVISOR_PROMPT.format(messages=state["messages"])

        router = llm.with_structured_output(RouterOutput)

        result = router.invoke(prompt)

        print("RESULT AGENTS --->", result.agents)

        return {"agents": result.agents}

    def route(self, state: HelpDeskState):
        print("Start the agent route")

        return [Send(agent, state) for agent in state["agents"]]

    def execute_supervisor(self, user_input: str):

        print("Starting the supervisor.")

        # Prepare the state to send to the compiled supervisor.
        input_state: HelpDeskState = {
            "query": user_input,
            "messages": [HumanMessage(content=user_input)],
            "agents": [],
            "answers": [],
            "final_answer": "",
        }

        result = self.app.invoke(
            input_state, config={"configurable": {"thread_id": "user-4321"}}
        )

        return result["final_answer"]

    def merge(self, state: HelpDeskState):
        print("Starting merge")

        final_answer = "\n\n".join(state["answers"])

        return {
            "final_answer": final_answer,
            # "messages": [AIMessage(content=final_answer)],
        }

    def hardware_agent_node(self, state: HelpDeskState):
        print(" Starting the hardware agent node.")

        answer = hardware_agent.invoke(
            {
                "messages": state["messages"],
            }
        )

        ai_message = answer["messages"][-1]

        return {"answers": [ai_message.content]}

    def software_agent_node(self, state: HelpDeskState):
        print(" Starting the software agent node.")

        answer = software_agent.invoke(
            {
                "messages": state["messages"],
            }
        )

        ai_message = answer["messages"][-1]

        return {"answers": [ai_message.content]}

    def general_agent_node(self, state: HelpDeskState):
        print(" Starting the general agent node.")

        answer = general_agent.invoke(
            {
                "messages": state["messages"],
            }
        )

        ai_message = answer["messages"][-1]

        return {"answers": [ai_message.content]}
