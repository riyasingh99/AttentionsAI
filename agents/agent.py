import json
from pathlib import Path
from typing import Optional, List
from textwrap import dedent

# Use absolute imports
from phi.assistant import Assistant
from phi.tools import Toolkit
from phi.tools.duckduckgo import DuckDuckGo
from phi.tools.file import FileTools
from phi.llm.ollama import Ollama
from phi.knowledge import AssistantKnowledge
from phi.embedder.ollama import OllamaEmbedder
from phi.storage.assistant.postgres import PgAssistantStorage
from phi.vectordb.pgvector import PgVector2
from phi.utils.log import logger

# Database configuration
db_url = "postgresql+psycopg://ai:ai@localhost:5532/ai"
cwd = Path(__file__).parent.resolve()
scratch_dir = cwd.joinpath("scratch")
if not scratch_dir.exists():
    scratch_dir.mkdir(exist_ok=True, parents=True)

def get_tour_guide_agent(
    llm_id: str = "llama3",
    travel_insights: bool = True,
    cultural_expert: bool = True,
    itinerary_planner: bool = True,
    file_tools: bool = False,
    user_id: Optional[str] = None,
    run_id: Optional[str] = None,
    debug_mode: bool = True,
) -> Assistant:
    logger.info(f"-*- Creating {llm_id} Tour Guide Agent -*-")

    # Add tools available to the Tour Guide Agent
    tools: List[Toolkit] = []
    extra_instructions: List[str] = []

    if travel_insights:
        tools.append(DuckDuckGo(fixed_max_results=5))
        extra_instructions.append(
            "You can use the web search tool to find travel information, recent changes, and popular attractions."
        )

    if file_tools:
        tools.append(FileTools(base_dir=cwd))
        extra_instructions.append(
            "Use read_file to read files, save_file to save new data, and list_files to show available documents in the directory."
        )

    # Create specialized assistants for team members
    team: List[Assistant] = []

    if cultural_expert:
        _cultural_expert = Assistant(
            name="Cultural Expert",
            llm=Ollama(model=llm_id),
            role="Provide historical and cultural context about tourist locations",
            description="You are an expert in history and culture, providing engaging and detailed insights about global destinations.",
            instructions=[
                "Offer rich cultural backgrounds and historical insights about landmarks and cities.",
                "Ensure your responses are captivating, educational, and engaging for travelers."
            ],
            debug_mode=debug_mode,
        )
        team.append(_cultural_expert)
        extra_instructions.append(
            "Delegate questions about cultural or historical aspects of travel locations to the Cultural Expert."
        )

    if itinerary_planner:
        _itinerary_planner = Assistant(
            name="Itinerary Planner",
            llm=Ollama(model=llm_id),
            role="Create personalized travel itineraries",
            description="You specialize in crafting travel itineraries that consider user preferences and time constraints.",
            instructions=[
                "Design custom itineraries that fit the user's requirements, considering travel time and activity durations.",
                "Include a balance of sightseeing, relaxation, and local experiences."
            ],
            debug_mode=debug_mode,
        )
        team.append(_itinerary_planner)
        extra_instructions.append(
            "To create detailed travel itineraries, delegate the task to the Itinerary Planner."
        )

    # Create the Tour Guide Agent
    agent = Assistant(
        name="Tour Guide Agent",
        run_id=run_id,
        user_id=user_id,
        llm=Ollama(model=llm_id),
        description=dedent(
            """\
            You are a Tour Guide Agent designed to assist with travel planning, providing valuable cultural insights, and crafting travel itineraries.
            """
        ),
        instructions=[
            "When handling user queries related to travel, think and determine if:\n"
            " - You should use the DuckDuckGo tool to find recent information.\n"
            " - You need to delegate a task to a team member for specific expertise.\n"
            " - Clarify any details with the user if needed.",
            "Ensure that your answers are informative, engaging, and tailored for travel enthusiasts.",
            "Use the Cultural Expert for historical context and cultural details.",
            "Use the Itinerary Planner to create travel schedules and plans."
        ],
        extra_instructions=extra_instructions,
        storage=PgAssistantStorage(table_name="tour_guide_runs", db_url=db_url),
        knowledge_base=AssistantKnowledge(
            vector_db=PgVector2(
                db_url=db_url,
                collection="tour_guide_documents",
                embedder=OllamaEmbedder(model="text-embedding-3-small", dimensions=1536),
            ),
            num_documents=3,
        ),
        tools=tools,
        team=team,
        show_tool_calls=True,
        search_knowledge=True,
        read_chat_history=True,
        add_chat_history_to_messages=True,
        num_history_messages=4,
        markdown=True,
        add_datetime_to_instructions=True,
        introduction=dedent(
            """\
            Hi, I'm your Tour Guide Agent, here to provide travel assistance, cultural insights, and personalized itineraries. Let's start your journey! 🌍\
            """
        ),
        debug_mode=debug_mode,
    )
    return agent