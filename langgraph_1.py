from langgraph.graph import StateGraph, START, END
from typing import TypedDict

class BMIState(TypedDict):
    weight: float
    height: float
    bmi: float
    category: str

graph = StateGraph(BMIState)

def calulate_bmi(state: BMIState) -> BMIState:
    weight = state['weight']
    height = state['height']
    bmi = weight/(height*height)
    state['bmi'] = round(bmi, 2)
    return state

def fitness(state: BMIState) -> BMIState:
    bmi = state['bmi']
    
    if bmi < 18:
        state['category'] = "Underweight"
    elif 18.5 < bmi <= 25:
        state['category'] = "Normal"
    elif 25 < bmi < 30:
        state['category'] = "Overweight"
    else:
        state['category'] = "Obese"
    return state
    
graph.add_node('calulate_bmi', calulate_bmi)
graph.add_node('fitness', fitness)


graph.add_edge(START, 'calulate_bmi')
graph.add_edge('calulate_bmi', 'fitness')
graph.add_edge('fitness', END)


workflow = graph.compile()

final_state = workflow.invoke({
    'height': 1.70,
    'weight': 55
})

print(final_state)