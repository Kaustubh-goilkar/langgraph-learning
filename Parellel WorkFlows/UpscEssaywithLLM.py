from langgraph.graph import StateGraph,START,END
from langchain_huggingface import ChatHuggingFace,HuggingFaceEndpoint
from langchain_core.messages import SystemMessage,HumanMessage,AIMessage
from dotenv import load_dotenv
from typing import TypedDict,Annotated
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

    feedback :str =  Field(description="detailed feedback for the essay")
    score:int = Field(description='Score out of 10',ge=0, le=10)

parser = PydanticOutputParser(pydantic_object=evaluationSchema)


class UpscEssayState(TypedDict):
    essay:str
    language_feedback:str
    analysis_feedback:str
    clarity_feedback:str
    overall_feedback:str

    individual_score:Annotated[list[int],add]

    avg_score:int
    

def callLLM(prompt):
    # The formating is not reliable because of hugging face models
    format_instructions = parser.get_format_instructions()

    final_prompt = f"""
    {prompt}

    {format_instructions}
    """
    result = model.invoke(final_prompt)
    # print('Content ', result)
    parsed_output = parser.parse(result.content)
    return parsed_output

def evaluate_language(state:UpscEssayState):
    prompt = f"Evaluate the language quality of the following essay and provide a feedback and assign a score out of 10 \\n {state['essay']}'\n"
    model_output = callLLM(prompt)
    return {'language_feedback' : model_output.feedback,'individual_score':[model_output.score]}

def analysis_feedback(state:UpscEssayState):
    prompt = f"Evaluate the analysis of the following essay and provide a feedback and assign a score out of 10 \\n {state['essay']}'\n"
    model_output = callLLM(prompt)
    return {'analysis_feedback' : model_output.feedback,'individual_score':[model_output.score]}    

def clarity_feedback(state:UpscEssayState):
    prompt = f"Evaluate the clarity of the following essay and provide a feedback and assign a score out of 10 \\n {state['essay']}'\n"
    model_output = callLLM(prompt)
    return {'clarity_feedback' : model_output.feedback,'individual_score':[model_output.score]}    

def final_evaluation(state:UpscEssayState):

    avg_score = sum(state['individual_score']) / len(state['individual_score'])
    return { 'avg_score' : avg_score}
    



essay = """
India in the Age of AI

As the world enters a transformative era defined by artificial intelligence (AI), India stands at a critical juncture — one where it can either emerge as a global leader in AI innovation or risk falling behind in the technology race. The age of AI brings with it immense promise as well as unprecedented challenges, and how India navigates this landscape will shape its socio-economic and geopolitical future.

India's strengths in the AI domain are rooted in its vast pool of skilled engineers, a thriving IT industry, and a growing startup ecosystem. With over 5 million STEM graduates annually and a burgeoning base of AI researchers, India possesses the intellectual capital required to build cutting-edge AI systems. Institutions like IITs, IIITs, and IISc have begun fostering AI research, while private players such as TCS, Infosys, and Wipro are integrating AI into their global services. In 2020, the government launched the National AI Strategy (AI for All) with a focus on inclusive growth, aiming to leverage AI in healthcare, agriculture, education, and smart mobility.

One of the most promising applications of AI in India lies in agriculture, where predictive analytics can guide farmers on optimal sowing times, weather forecasts, and pest control. In healthcare, AI-powered diagnostics can help address India’s doctor-patient ratio crisis, particularly in rural areas. Educational platforms are increasingly using AI to personalize learning paths, while smart governance tools are helping improve public service delivery and fraud detection.

However, the path to AI-led growth is riddled with challenges. Chief among them is the digital divide. While metropolitan cities may embrace AI-driven solutions, rural India continues to struggle with basic internet access and digital literacy. The risk of job displacement due to automation also looms large, especially for low-skilled workers. Without effective skilling and re-skilling programs, AI could exacerbate existing socio-economic inequalities.

Another pressing concern is data privacy and ethics. As AI systems rely heavily on vast datasets, ensuring that personal data is used transparently and responsibly becomes vital. India is still shaping its data protection laws, and in the absence of a strong regulatory framework, AI systems may risk misuse or bias.

To harness AI responsibly, India must adopt a multi-stakeholder approach involving the government, academia, industry, and civil society. Policies should promote open datasets, encourage responsible innovation, and ensure ethical AI practices. There is also a need for international collaboration, particularly with countries leading in AI research, to gain strategic advantage and ensure interoperability in global systems.

India’s demographic dividend, when paired with responsible AI adoption, can unlock massive economic growth, improve governance, and uplift marginalized communities. But this vision will only materialize if AI is seen not merely as a tool for automation, but as an enabler of human-centered development.

In conclusion, India in the age of AI is a story in the making — one of opportunity, responsibility, and transformation. The decisions we make today will not just determine India’s AI trajectory, but also its future as an inclusive, equitable, and innovation-driven society.
"""

graph = StateGraph(UpscEssayState)

# nodes
graph.add_node('evaluate_language',evaluate_language)
graph.add_node('analysis_feedback',analysis_feedback)
graph.add_node('clarity_feedback',clarity_feedback)
graph.add_node('final_evaluation',final_evaluation)



# edage
graph.add_edge(START,'evaluate_language')
graph.add_edge(START,'analysis_feedback')
graph.add_edge(START,'clarity_feedback')

graph.add_edge('evaluate_language','final_evaluation')
graph.add_edge('analysis_feedback','final_evaluation')
graph.add_edge('clarity_feedback','final_evaluation')

graph.add_edge('final_evaluation',END)

workflow = graph.compile()

initial_state = {
    'essay':essay
}

result = workflow.invoke(initial_state)
print(result)