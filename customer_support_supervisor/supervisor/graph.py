import os
import logging
from operator import add
from typing import Annotated
from dotenv import load_dotenv
from typing_extensions import TypedDict, List
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage
from pydantic import BaseModel, Field
from langgraph.types import Send
from langchain_core.messages import AIMessage
from langgraph.graph import StateGraph, START, END
from agents.billing_agent import billing_agent
from agents.sales_agent import sales_agent
from agents.technical_agent import technical_agent
from agents.general_agent import general_agent
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import InMemorySaver

logger = logging.getLogger(__name__)

load_dotenv()

llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0.7,
    api_key=os.getenv("OPENAI_API_KEY"),
)

class CustomerSupportState(TypedDict):
    query: str
    messages: Annotated[list[BaseMessage], add]
    agents: List[str]
    answers: Annotated[list[str], add]
    final_answer: str

class RouterOutput(BaseModel):
    agents: List[str] = Field(
        description="Lista de agentes relevantes para a pergunta do usuário. "
    )

class CustomerSupportAgent:

    def __init__(self):
        self.logging = logger
        self.graph = StateGraph(CustomerSupportState)

        self.graph.add_node("classify", self.classify_user_intention)

        self.graph.add_node("billing_agent", self.billing_agent_node)
        self.graph.add_node("sales_agent", self.sales_agent_node)
        self.graph.add_node("technical_agent", self.technical_agent_node)
        self.graph.add_node("general_agent", self.general_agent_node)

        self.graph.add_node("merge_results", self.merge_results)

        self.graph.add_edge(START, "classify")
        self.graph.add_conditional_edges("classify", self.route)

        self.graph.add_edge("billing_agent", "merge_results")
        self.graph.add_edge("sales_agent", "merge_results")
        self.graph.add_edge("technical_agent", "merge_results")
        self.graph.add_edge("general_agent", "merge_results")

        self.graph.add_edge("merge_results", END)

        memory = InMemorySaver()

        self.app = self.graph.compile(
            checkpointer=memory
        )

    def execute_supervisor(self, user_input: str):

        self.logging.info("Start the supervisor")

        input_state: CustomerSupportState = {
            "query": user_input,
            "messages": [
                HumanMessage(content=user_input)
            ],
            "agents": [],
            "answers": [],
            "final_answer": "",
        }

        result = self.app.invoke(
            input_state,
            config={
                "configurable": {
                    "thread_id": "user-123"
                }
            }
        )

        return result["final_answer"]

    def classify_user_intention(self, state: CustomerSupportState):

        self.logging.info("Start the agent classification")

        prompt = f"""
        You are a Customer Support Supervisor.

        Your responsibility is NOT to answer the customer.
        
        Your only responsibility is to determine which specialized agents should handle the user's request.
        
        Available agents:
        
        - general_agent
          Handles:
          - Greetings (e.g. "Hello", "Hi", "Good morning")
          - Small talk (e.g. "How are you?")
          - Questions about the assistant's capabilities
          - Requests that are outside the scope of the specialized agents
          - Politely informing users what kinds of customer support are available
          - Asking the user to clarify their request if it is too vague
        
          Select this agent whenever the user's request does not clearly belong to Billing, Technical Support, or Sales.
        
        - billing_agent
          Handles:
          - Refund requests
          - Invoices
          - Charges
          - Payments
          - Subscription questions
          - Billing issues
        
        - technical_agent
          Handles:
          - Login problems
          - Errors
          - Bugs
          - Password reset
          - Website issues
          - API issues
          - Mobile app issues
        
        - sales_agent
          Handles:
          - Product information
          - Pricing
          - Plans
          - Features
          - Upgrades
          - Discounts
          - Purchasing questions
        
        The user may need one or multiple agents.
        
        Examples:
        
        User:
        "I was charged twice."
        
        Output:
        ["billing_agent"]
        
        User:
        "I can't login."
        
        Output:
        ["technical_agent"]
        
        User:
        "I'd like to upgrade my subscription."
        
        Output:
        ["sales_agent"]
        
        User:
        "I can't login and I want a refund."
        
        Output:
        ["technical_agent", "billing_agent"]
        
        User:
        "Tell me about your Enterprise plan."
        
        Output:
        ["sales_agent"]
        
        "Hello"

        Output:
        ["general_agent"]
        
        User:
        "How are you?"
        
        Output:
        ["general_agent"]
        
        User:
        "What can you help me with?"
        
        Output:
        ["general_agent"]
        
        User:
        "Tell me a joke."
        
        Output:
        ["general_agent"]
        
        User:
        "Hi, I can't log in."
        
        Output:
        ["general_agent", "technical_agent"]
        
        User:
        "Hello, I'd like a refund."
        
        Output:
        ["general_agent", "billing_agent"]
        
        User request:

        {state["query"]}

        Return every agent needed.
        
        Return ONLY the list of agent names.
        Do not answer the user.
        """
        router = llm.with_structured_output(RouterOutput)

        result = router.invoke(prompt)

        return {
            "agents": result.agents
        }

    def route(self, state: CustomerSupportState):

        self.logging.info("Start the agent route")

        return [
            Send(agent, state)
            for agent in state["agents"]
        ]

    def merge_results(self, state: CustomerSupportState):

        self.logging.info("Start the agent merge results")

        final_answer = "\n\n".join(state["answers"])

        return {
            "final_answer": final_answer,
            "messages": [
                AIMessage(content=final_answer)
            ],
        }

    def general_agent_node(self, state: CustomerSupportState):

        self.logging.info("Start the agent general agent")

        answer = general_agent.invoke({
            "messages": state["messages"],
        })

        ai_message = answer["messages"][-1]

        return {
            "answers": [
                ai_message.content
            ]
        }

    def billing_agent_node(self, state: CustomerSupportState):

        self.logging.info("Start the agent billing agent")

        answer = billing_agent.invoke({
            "messages": state["messages"],
        })

        ai_message = answer["messages"][-1]

        return {
            "answers": [
                ai_message.content
            ]
        }

    def sales_agent_node(self, state: CustomerSupportState):

        self.logging.info("Start the agent sales agent")

        answer = sales_agent.invoke({
            "messages": state["messages"],
        })

        ai_message = answer["messages"][-1]

        return {
            "answers": [
                ai_message.content
            ]
        }

    def technical_agent_node(self, state: CustomerSupportState):

        self.logging.info("Start the agent technical agent")

        answer = technical_agent.invoke({
            "messages": state["messages"],
        })

        ai_message = answer["messages"][-1]

        return {
            "answers": [
                ai_message.content
            ]
        }
