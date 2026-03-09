from langgraph.graph import StateGraph,START,END
from langchain_huggingface import ChatHuggingFace,HuggingFaceEndpoint
from langchain_core.messages import SystemMessage,HumanMessage,AIMessage
from dotenv import load_dotenv
from typing import TypedDict,Annotated,Literal
from pydantic import BaseModel,Field
from operator import add
from langchain_core.output_parsers import PydanticOutputParser

load_dotenv()

llm = HuggingFaceEndpoint(
    repo_id="openai/gpt-oss-120b",
    task="text-generation",
    provider="auto",  # let Hugging Face choose the best provider for you
)

model = ChatHuggingFace(llm=llm)


class evaluationSchema(BaseModel):

    sentiment :Literal['Positive','Negative'] =  Field(description="Give the sentiment of this review just return 'Positive' or 'Negative'")

parser = PydanticOutputParser(pydantic_object=evaluationSchema)

class ReviewState(TypedDict):

    review:str
    sentiment:Literal['Positive','Negative']
    response:str
    dignosis_result:str


def callLLM(prompt,with_parser=True):
    # The formating is not reliable because of hugging face models
    if(with_parser):
        format_instructions = parser.get_format_instructions()

        final_prompt = f"""
        {prompt}

        {format_instructions}
        """
    else:
        final_prompt = prompt
    result = model.invoke(final_prompt)
    if(with_parser):
        parsed_output = parser.parse(result.content)
    else:
        parsed_output = result.content

    # Dummay Output
    # parsed_output =evaluationSchema(sentiment= 'Positive')
    return parsed_output

# result = callLLM("statified with this phone")
# print(result)

# Node Evaluation Functions
def find_sentiment(state:ReviewState):
    sentiment = callLLM(state['review'])
    return { 'sentiment': sentiment.sentiment }

def positive_response(state:ReviewState):
    response = callLLM(f"Provide a positive response to this review {state['review']}",False)
    return { 'response':response }

def negative_response(state:ReviewState):
    response = callLLM(f"Provide a negative response to this review {state['review']}",False)
    return { 'response':response }

def run_dignosis(state:ReviewState):
    dignosis_result = callLLM(f"Provide deep diagnosis report why the user is not statified and give a negative response to this review {state['review']}",False)
    return {'dignosis_result':dignosis_result}

    

def check_condition(state:ReviewState) -> Literal['positive_response','negative_response']:
    if(state['sentiment'] == 'Positive'):
        return 'positive_response'
    else:
        return 'negative_response'
    

# Define Graph
graph = StateGraph(ReviewState)

# Nodes
graph.add_node("find_sentiment",find_sentiment)
graph.add_node("positive_response",positive_response)
graph.add_node("negative_response",negative_response)
graph.add_node("run_dignosis",run_dignosis)


# Eges
graph.add_edge(START,"find_sentiment")
graph.add_conditional_edges("find_sentiment",check_condition)

graph.add_edge("negative_response","run_dignosis")
graph.add_edge("run_dignosis",END)
graph.add_edge("positive_response",END)


workflow = graph.compile()

initial_state = {
    'review':"i don't  like this phone battery is weak"
}
result = workflow.invoke(initial_state)
print(result)
