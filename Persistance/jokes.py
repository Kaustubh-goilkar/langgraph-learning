from langgraph.graph import StateGraph,START,END
from langchain_huggingface import ChatHuggingFace,HuggingFaceEndpoint
from langchain_core.messages import BaseMessage,SystemMessage,HumanMessage,AIMessage
from dotenv import load_dotenv
from typing import TypedDict,Annotated
from pydantic import BaseModel,Field
from operator import add
from langgraph.graph.message import add_messages
from langchain_core.output_parsers import PydanticOutputParser
from langgraph.checkpoint.memory import MemorySaver,InMemorySaver

load_dotenv()

llm = HuggingFaceEndpoint(
    repo_id="openai/gpt-oss-20b",
    task="conversational",
    # provider="auto",  # let Hugging Face choose the best provider for you
)

model = ChatHuggingFace(llm=llm)

class JokesState(TypedDict):

    topic : str
    joke : str
    explanation: str


def generate_joke(state: JokesState):
    topic = state['topic']

    response = model.invoke(f'Generate a joke on {topic}').content

    return { 'joke': response}

def explain_joke(state: JokesState):
    joke = state['joke']

    response = model.invoke(f'Explain this joke  {joke}').content

    return { 'explanation': response}


graph = StateGraph(JokesState)

# Nodes
graph.add_node("generate_joke",generate_joke)
graph.add_node("explain_joke",explain_joke)

# Edges

graph.add_edge(START,'generate_joke')
graph.add_edge('generate_joke','explain_joke')
graph.add_edge('explain_joke',END)

checkpointer = InMemorySaver()

workflow = graph.compile(checkpointer=checkpointer)

initial_state = {
    'topic':'Rain'
}

config = {
    'configurable':{'thread_id':1}
}

result = workflow.invoke(input=initial_state,config=config)
final_state = workflow.get_state(config=config)

# Fetch all state History when the state change
state_history = list(workflow.get_state_history(config=config))
print(state_history)