# Graph Flow :-  UserInput(Height,Weight) -> Cal BMI -> Output

from typing import TypedDict
from langgraph.graph import StateGraph,START,END



# Define State
class BMIState(TypedDict):
    height:float
    weight:float
    bmi:float
    fitness_label:str

def calcualte_BMI(state:BMIState) -> BMIState:
    weight = state["weight"]
    height = state["height"]
    bmi = round(weight / (height ** 2),2)
    state["bmi"] = bmi
    return state

def label_BMI(state:BMIState) -> BMIState:
    bmi = state["bmi"]
    if(bmi < 18.5):
        state["fitness_label"] = "Underweight"
    elif(bmi < 25):
        state["fitness_label"] = "Normal"
    else:
        state["fitness_label"] = "Overweight"
    return state



# Defining graph
graph = StateGraph(state_schema=BMIState)

# Adding the Node in Graph
graph.add_node("Calculate_bmi",calcualte_BMI)
graph.add_node("label_bmi",label_BMI)

# START and END are just the Dummy node for the Graph 
graph.add_edge(START,'Calculate_bmi')
graph.add_edge("Calculate_bmi","label_bmi")
graph.add_edge('label_bmi',END)

# Complie the Graph
workflow  = graph.compile()

# execute the Graph
intial_state = {"weight":90, "height":1.2}
output_state = workflow.invoke(intial_state)
print(output_state)



