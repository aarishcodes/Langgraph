# <=================== Contidional WorkFlow Easy Example =====================>
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Literal
import math


class Solution(TypedDict):
    a: int
    b: int
    c: int
    
    equation: str
    discriminant: float
    result: str
    
graph = StateGraph(Solution)

def show_equation(state: Solution) -> Solution:
    equation = f"{state['a']}x² + {state['b']}x + {state['c']}"
        
    return {'equation': equation}

def calulate_descriminate(state: Solution) -> Solution:
    discriminant = state['b']**2 - (4 * state['a'] * state['c'])
    return {'discriminant': discriminant}

def real_roots(state: Solution) -> Solution:
    root1 = (-state['b'] + math.sqrt(state['discriminant'])) / (2 * state['a'])
    root2 = (-state['b'] - math.sqrt(state['discriminant'])) / (2 * state['a'])
    
    result = f'The Roots are {root1} and {root2}'
    
    return {'result': result}



def no_roots(state: Solution) -> Solution:

    result = f'No Real Roots'
    
    return {'result': result}


def repeated_roots(state: Solution) -> Solution:
    root = -state['b'] / (2 * state['a'])
     
    result = f'The Only Roots are {root}'
    
    return {'result': result}

def check_condition(state: Solution)-> Literal["real_roots", "no_roots", "repeated_roots"]:
    if state['discriminant'] > 0:
        return "real_roots"
    elif state['discriminant'] ==0:
        return  "repeated_roots"
    else:
        return "no_roots"
    

graph.add_node('show_equation', show_equation)
graph.add_node('calculate_descriminate', calulate_descriminate)

graph.add_node('real_roots', real_roots)
graph.add_node('no_roots', no_roots)
graph.add_node('repeated_roots', repeated_roots)


graph.add_edge(START, 'show_equation')
graph.add_edge('show_equation', 'calculate_descriminate')

graph.add_conditional_edges('calculate_descriminate', check_condition)

graph.add_edge('real_roots', END)
graph.add_edge('no_roots', END)
graph.add_edge('repeated_roots', END)


work_flow = graph.compile()

initial_state = {
    'a': 4,
    'b': 5,
    'c': -4
}
final_work = work_flow.invoke(initial_state)

print(final_work)


