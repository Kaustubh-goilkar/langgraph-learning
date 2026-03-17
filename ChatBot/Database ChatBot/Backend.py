from langgraph.graph import StateGraph,START,END
from langchain_huggingface import ChatHuggingFace,HuggingFaceEndpoint
from langchain_core.messages import BaseMessage,SystemMessage,HumanMessage,AIMessage
from dotenv import load_dotenv
from typing import TypedDict,Annotated
from pydantic import BaseModel,Field
from operator import add
from langgraph.graph.message import add_messages
from langchain_core.output_parsers import PydanticOutputParser
from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3

load_dotenv()

llm = HuggingFaceEndpoint(
    repo_id="openai/gpt-oss-20b",
    task="conversational",
    # provider="auto",  # let Hugging Face choose the best provider for you
)

model = ChatHuggingFace(llm=llm)


class ChatbotState(TypedDict):

    # Add messages is optimized reducer which will append new message to messages array
    messages:Annotated[list[BaseMessage],add_messages]

def chat_bot(state: ChatbotState):
    messages = state["messages"]

    response = model.invoke(messages)

    return{'messages':[response]}

# Make connect to Sqlite
conn = sqlite3.connect(database="chatbot.db",check_same_thread=False)
checkpointer = SqliteSaver(conn = conn)

graph = StateGraph(state_schema=ChatbotState)

# Nodes
graph.add_node("chat_bot",chat_bot)

# Edges
graph.add_edge(START,'chat_bot')
graph.add_edge('chat_bot',END)

# compile graph
chatBotWorkflow = graph.compile(checkpointer=checkpointer)

def retrieve_all_threads():
    all_threads = set()
    for checkpoint in checkpointer.list(None):
        all_threads.add(checkpoint.config['configurable']['thread_id'])

    return list(all_threads)