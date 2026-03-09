from langgraph.graph import StateGraph,START,END
from langchain_huggingface import ChatHuggingFace,HuggingFaceEndpoint
from langchain_core.messages import SystemMessage,HumanMessage,AIMessage
from dotenv import load_dotenv
from typing import TypedDict,Annotated,Literal
from pydantic import BaseModel,Field
from operator import add
from langchain_core.output_parsers import PydanticOutputParser
from IPython.display import Image, display

load_dotenv()

generation_llm = HuggingFaceEndpoint(
    repo_id="openai/gpt-oss-120b",
    task="text-generation",
    provider="auto",  # let Hugging Face choose the best provider for you
)

common_llm = HuggingFaceEndpoint(
    repo_id="openai/gpt-oss-120b",
    task="text-generation",
    provider="auto",  # let Hugging Face choose the best provider for you
)

generation_model = ChatHuggingFace(llm=generation_llm)
commmon_model = ChatHuggingFace(llm=common_llm)

class evaluationSchema(BaseModel):
    evaluation:Literal['approved','needs_improvement']
    feedback:str

parser = PydanticOutputParser(pydantic_object=evaluationSchema)


# State
class TweetState(TypedDict):
    topic:str
    tweet:str
    evaluation:Literal['approved','needs_improvement']
    feedback:str
    iteration:int
    max_iteration:int

def generate_text(state:TweetState):
    # prompt
    messages = [
        SystemMessage(content="You are a funny and clever Twitter/X influencer."),
        HumanMessage(content=f"""
            Write a short, original, and hilarious tweet on the topic: "{state['topic']}".

            Rules:
            - Do NOT use question-answer format.
            - Max 280 characters.
            - Use observational humor, irony, sarcasm, or cultural references.
            - Think in meme logic, punchlines, or relatable takes.
            - Use simple, day to day english
            """)
    ]
    result = generation_model.invoke(messages).content
    return {'tweet':result}

def evaluating_tweet(state:TweetState):
    format_instructions = parser.get_format_instructions()
    messages = [
    SystemMessage(content="You are a ruthless, no-laugh-given Twitter critic. You evaluate tweets based on humor, originality, virality, and tweet format."),
    HumanMessage(content=f"""
        Evaluate the following tweet:

        Tweet: "{state['tweet']}"

        Use the criteria below to evaluate the tweet:

        1. Originality – Is this fresh, or have you seen it a hundred times before?  
        2. Humor – Did it genuinely make you smile, laugh, or chuckle?  
        3. Punchiness – Is it short, sharp, and scroll-stopping?  
        4. Virality Potential – Would people retweet or share it?  
        5. Format – Is it a well-formed tweet (not a setup-punchline joke, not a Q&A joke, and under 280 characters)?

        Auto-reject if:
        - It's written in question-answer format (e.g., "Why did..." or "What happens when...")
        - It exceeds 280 characters
        - It reads like a traditional setup-punchline joke
        - Dont end with generic, throwaway, or deflating lines that weaken the humor (e.g., “Masterpieces of the auntie-uncle universe” or vague summaries)

        ### Respond ONLY in structured format:
        - evaluation: "approved" or "needs_improvement"  
        - feedback: One paragraph explaining the strengths and weaknesses 
        {format_instructions}
        """)
        ]
    result = commmon_model.invoke(messages)
    paresed_output = parser.parse(result.content)
    return { 'feedback': paresed_output.feedback , 'evaluation':paresed_output.evaluation }

def optimize_tweet(state: TweetState):

    messages = [
        SystemMessage(content="You punch up tweets for virality and humor based on given feedback."),
        HumanMessage(content=f"""
            Improve the tweet based on this feedback:
            "{state['feedback']}"

            Topic: "{state['topic']}"
            Original Tweet:
            {state['tweet']}

            Re-write it as a short, viral-worthy tweet. Avoid Q&A style and stay under 280 characters.
            """)
        ]

    response = common_llm.invoke(messages).content
    iteration = state['iteration'] + 1
    return { 'tweet':response , 'iteration':iteration}

def route_evaluation(state: TweetState):

    if state['evaluation'] == 'approved' or state['iteration'] >= state['max_iteration']:
        return 'approved'
    else:
        return 'needs_improvement'
    


graph = StateGraph(TweetState)

# Nodes
graph.add_node("generate_tweet",generate_text)
graph.add_node("evaluate_tweet",evaluating_tweet)
graph.add_node("optimize_tweet",optimize_tweet)


# Edges
graph.add_edge(START,'generate_tweet')
graph.add_edge('generate_tweet','evaluate_tweet')
graph.add_conditional_edges('evaluate_tweet',route_evaluation, {'approved':END, 'needs_improvement':'optimize_tweet'})
graph.add_edge('optimize_tweet','evaluate_tweet')


workflow = graph.compile()

initial_state = {
    "topic": "LangGraph",
    "iteration": 1,
    "max_iteration": 5
}
# result = workflow.invoke(initial_state)

# print(result)

# Assuming 'workflow' is your compiled graph
try:
    # This creates a PNG and saves it to a file
    graph_image = workflow.get_graph().draw_mermaid_png()
    with open("graph_output.png", "wb") as f:
        f.write(graph_image)
    print("Graph saved as graph_output.png")
    
    # If you are in a Jupyter/Google Colab notebook, use:
    display(Image(graph_image))
except Exception as e:
    print(f"Could not generate image: {e}")