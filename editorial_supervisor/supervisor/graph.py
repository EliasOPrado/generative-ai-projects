import logging
from typing import TypedDict, Optional

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver

from editorial_supervisor.agents.editorial_planner_agent import (
    editorial_planner_agent,
)
from editorial_supervisor.agents.research_agent import (
    research_agent,
)
from editorial_supervisor.agents.content_writer_agent import (
    content_writer_agent,
)
from editorial_supervisor.agents.seo_reviewer_agent import (
    seo_reviewer_agent,
)
from editorial_supervisor.agents.publication_formatter_agent import (
    publication_formatter_agent,
)

from editorial_supervisor.services.wordpress_publisher import (
    wordpress_publisher,
)


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MAX_REVIEW_ATTEMPTS = 3


class EditorialState(TypedDict):
    keyword: str
    editorial_brief: dict
    research_result: dict
    article: str
    seo_review: dict
    publication_package: dict
    publication_result: dict
    review_attempts: int
    last_error: str


class EditorialSupervisor:

    def __init__(self):

        workflow = StateGraph(EditorialState)

        workflow.add_node(
            "planner",
            self.planner_node,
        )

        workflow.add_node(
            "research",
            self.research_node,
        )

        workflow.add_node(
            "writer",
            self.writer_node,
        )

        workflow.add_node(
            "reviewer",
            self.reviewer_node,
        )

        workflow.add_node(
            "formatter",
            self.formatter_node,
        )

        workflow.add_node(
            "publisher",
            self.publisher_node,
        )

        workflow.add_edge(
            START,
            "planner",
        )

        workflow.add_edge(
            "planner",
            "research",
        )

        workflow.add_edge(
            "research",
            "writer",
        )

        workflow.add_edge(
            "writer",
            "reviewer",
        )

        workflow.add_conditional_edges(
            "reviewer",
            self.review_router,
            {
                "rewrite": "writer",
                "publish": "formatter",
            },
        )

        workflow.add_edge(
            "formatter",
            "publisher",
        )

        workflow.add_edge(
            "publisher",
            END,
        )

        memory = InMemorySaver()

        self.app = workflow.compile(
            checkpointer=memory,
        )

    ####################################################################
    # PUBLIC API
    ####################################################################

    def execute(
        self,
        keyword: str,
        thread_id: str,
    ):

        logger.info("Starting Editorial Supervisor")

        state: EditorialState = {
            "keyword": keyword,
            "editorial_brief": {},
            "research_result": {},
            "article": "",
            "seo_review": {},
            "publication_package": {},
            "publication_result": {},
            "review_attempts": 0,
        }

        result = self.app.invoke(
            state,
            config={
                "configurable": {
                    "thread_id": thread_id,
                }
            },
        )

        return result

    ####################################################################
    # ROUTER
    ####################################################################

    def review_router(
        self,
        state: EditorialState,
    ):

        review = state["seo_review"]

        if review["approved"]:

            logger.info("Article approved.")

            return "publish"

        attempts = state.get(
            "review_attempts",
            0,
        ) + 1

        if attempts > MAX_REVIEW_ATTEMPTS:

            raise RuntimeError(
                "Maximum review attempts exceeded."
            )

        return "rewrite"

    ####################################################################
    # PLANNER
    ####################################################################

    def planner_node(
        self,
        state: EditorialState,
    ):

        logger.info("Planner Agent")

        result = editorial_planner_agent.invoke(
            {
                "keyword": state["keyword"],
            }
        )

        return {
            "editorial_brief": result,
        }

    ####################################################################
    # RESEARCH
    ####################################################################

    def research_node(
        self,
        state: EditorialState,
    ):

        logger.info("Research Agent")

        result = research_agent.invoke(
            {
                "editorial_brief":
                    state["editorial_brief"],
            }
        )

        return {
            "research_result": result,
        }

        ####################################################################
    # WRITER
    ####################################################################

    def writer_node(
        self,
        state: EditorialState,
    ):

        logger.info("Content Writer Agent")

        review_attempts = state.get(
            "review_attempts",
            0,
        )

        previous_review = None

        if review_attempts > 0:
            previous_review = state["seo_review"]

        result = content_writer_agent.invoke(
            {
                "editorial_brief": state["editorial_brief"],
                "research_result": state["research_result"],
                "previous_review": previous_review,
            }
        )

        return {
            "article": result,
            "review_attempts": review_attempts + 1,
        }

    ####################################################################
    # REVIEWER
    ####################################################################

    def reviewer_node(
        self,
        state: EditorialState,
    ):

        logger.info("SEO Reviewer Agent")

        result = seo_reviewer_agent.invoke(
            {
                "editorial_brief": state["editorial_brief"],
                "research_result": state["research_result"],
                "article": state["article"],
            }
        )

        return {
            "seo_review": result,
        }

    ####################################################################
    # FORMATTER
    ####################################################################

    def formatter_node(
        self,
        state: EditorialState,
    ):

        logger.info("Publication Formatter Agent")

        result = publication_formatter_agent.invoke(
            {
                "article": state["article"],
                "editorial_brief": state["editorial_brief"],
                "seo_review": state["seo_review"],
            }
        )

        return {
            "publication_package": result,
        }

    ####################################################################
    # PUBLISHER
    ####################################################################

    def publisher_node(
        self,
        state: EditorialState,
    ):

        logger.info("Publishing to WordPress")

        result = wordpress_publisher.publish(
            publication_package=state["publication_package"],
        )

        return {
            "publication_result": result,
        }