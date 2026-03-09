from langgraph.graph import StateGraph,START,END
from langchain_huggingface import ChatHuggingFace,HuggingFaceEndpoint
from langchain_core.messages import SystemMessage,HumanMessage,AIMessage
from dotenv import load_dotenv
from typing import TypedDict

load_dotenv()

llm = HuggingFaceEndpoint(
    repo_id="MiniMaxAI/MiniMax-M2.5",
    task="text-generation",
    provider="auto",  # let Hugging Face choose the best provider for you
)

class LLMState(TypedDict):
    question:str
    answer:str

def getAnswer(state:LLMState) -> LLMState:
   state["answer"] =  model.invoke(state["question"]).content
   return state

model = ChatHuggingFace(llm=llm)
graph = StateGraph(LLMState)

# Adding the nodes
graph.add_node("get_answer",getAnswer)

graph.add_edge(START,"get_answer")
graph.add_edge("get_answer",END)

workflow = graph.compile()

result = workflow.invoke({"question":"What is LangGraph"})
print(result)




