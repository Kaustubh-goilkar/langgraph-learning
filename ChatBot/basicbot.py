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

checkpoint = MemorySaver()
graph = StateGraph(state_schema=ChatbotState)

# Nodes
graph.add_node("chat_bot",chat_bot)

# Edges
graph.add_edge(START,'chat_bot')
graph.add_edge('chat_bot',END)

# compile graph
chatBotWorkflow = graph.compile(checkpointer=checkpoint)
# result = chatBotWorkflow.invoke({'messages':[HumanMessage('Hi how are you')]})

while True:
    user_message = input("Type here : ")
    if user_message.strip().lower() in ['exit','quit','by']:
        break

    config = { 'configurable':{'thread_id': '1'} }
    result = chatBotWorkflow.invoke({'messages':[HumanMessage(user_message)]},config=config)
    print("AI : ", result['messages'][-1].content)
