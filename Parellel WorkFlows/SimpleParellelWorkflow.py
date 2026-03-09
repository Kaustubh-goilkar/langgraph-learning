from langgraph.graph import StateGraph,START,END
from typing import TypedDict

class BatsManState(TypedDict):
    
    runs:int
    balls:int
    sixes:int
    fours:int

    sr:float
    bpb:float
    boundary_percentage:float
    summary:str


def cal_sr(state:BatsManState):
    sr = (state['runs'] /state['balls']) * 100

    # Partially updating the state 
    return { 'sr' : sr}

def cal_bpb(state:BatsManState):
    bpb = state['balls'] / ( state['fours'] + state['sixes'])
    return { 'bpb': bpb}

def cal_boundary_percentage(state:BatsManState):
    boundary_percentage = (( (state['fours'] * 4) + (state['sixes'] * 6) ) / state['runs']) * 100
    return { 'boundary_percentage' : boundary_percentage}

def summary(state:BatsManState):
    summary = f"""
    Strike rate - {state['sr']} \n
    Ball per bounary - {state['bpb']} \n
    Bounary Percentage - {state['boundary_percentage']}
"""
    return {'summary':summary}

graph = StateGraph(BatsManState)

# Nodes
graph.add_node("cal_sr",cal_sr)
graph.add_node("cal_bpb",cal_bpb)
graph.add_node("cal_boundary_percentage",cal_boundary_percentage)
graph.add_node("summary",summary)

# Edges

graph.add_edge(START,"cal_sr")
graph.add_edge(START,"cal_bpb")
graph.add_edge(START,"cal_boundary_percentage")

graph.add_edge("cal_sr","summary")
graph.add_edge("cal_bpb","summary")
graph.add_edge("cal_boundary_percentage","summary")

graph.add_edge("summary",END)

workflow = graph.compile()

intial_state = {
    'runs':100,
    'balls':50,
    'fours':6,
    'sixes':4
}
result = workflow.invoke(intial_state)
print(result)