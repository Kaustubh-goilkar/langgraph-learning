from langgraph.graph import StateGraph,START,END
from langchain_huggingface import ChatHuggingFace,HuggingFaceEndpoint
from langchain_core.messages import SystemMessage,HumanMessage,AIMessage
from dotenv import load_dotenv
from typing import TypedDict

load_dotenv()

llm = HuggingFaceEndpoint(
    # repo_id="MiniMaxAI/MiniMax-M2.5",
    repo_id="openai/gpt-oss-120b",
    task="text-generation",
    provider="auto",  # let Hugging Face choose the best provider for you
)

class BlogState(TypedDict):
    title:str
    outline:str
    content:str
    blogRating:str

def create_ouline(state:BlogState) -> BlogState:
    title = state['title']

    prompt = f"Generate a detailed outline for the blog on this topic :-  {title}"
    state["outline"] = model.invoke(prompt).content
    return state

def create_blog(state:BlogState) -> BlogState:
    outline = state['outline']
    prompt = f"Generate a detailed blog content for this outline :-  {outline}"
    state["content"] = model.invoke(prompt).content
    return state

def evalute_blog(state:BlogState) -> BlogState:
    outline = state['outline']
    blog = state["content"]
    prompt = f"Based on this '{outline}' rate my blog '{blog} from 1 to 10"
    state["blogRating"] = model.invoke(prompt).content
    return state



model = ChatHuggingFace(llm=llm)
graph = StateGraph(BlogState)

# Nodes
graph.add_node("create_outline",create_ouline)
graph.add_node("create_blog",create_blog)
graph.add_node("evaluate_blog",evalute_blog)


# Edges
graph.add_edge(START,"create_outline")
graph.add_edge("create_outline","create_blog")
graph.add_edge("create_blog","evaluate_blog")
graph.add_edge("evaluate_blog",END)

worflow = graph.compile()

result = worflow.invoke({"title":"LangGraph"})
print(result['blogRating'])