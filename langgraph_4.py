#<--------------------- Parallel Work Flow --------------------------------->

from langgraph.graph import StateGraph, START, END
from typing import TypedDict



class BatsmanState(TypedDict):
    runs: int
    balls: int
    sixes: int
    fours: int
    
    sr: float
    bpb: float
    boundary_percent: float
    summery: str

graph = StateGraph(BatsmanState)


def calculate_sr(state: BatsmanState) -> BatsmanState:
    sr = (state['runs']/state['balls'])*100
    
    return {'sr': sr}

def calculate_bpb(state: BatsmanState) -> BatsmanState:
    bpb = state['balls']/(state['fours']+ state['sixes'])
    
    
    return {'bpb': bpb}

def boundary_percent(state: BatsmanState) -> BatsmanState:
    boundary_percent = (((state['fours']*4)+(state['sixes']*6))/state['runs'])*100
    
    
    return {'boundary_percent': boundary_percent}

def summery(state: BatsmanState) -> BatsmanState:
    summery = f"""
    Strike Rate - {state['sr']} \n
    Balls per Boundary - {state['bpb']} \n 
    Boundary Percent - {state['boundary_percent']}
    """
    
    
    
    return {'summery': summery}
 
graph.add_node('calculate_sr', calculate_sr)
graph.add_node('calculate_bpb', calculate_bpb)
graph.add_node('boundary_percent', boundary_percent)


graph.add_node('summery', summery)

graph.add_edge(START, 'calculate_sr')
graph.add_edge(START, 'calculate_bpb')
graph.add_edge(START, 'boundary_percent')


graph.add_edge('calculate_sr','summery')
graph.add_edge('calculate_bpb','summery')
graph.add_edge('boundary_percent','summery')

graph.add_edge('summery', END)


work_flow = graph.compile()


prompt = {
    'balls': 100,
    'runs': 200,
    'sixes': 4,
    'fours': 6 
}


final_flow = work_flow.invoke(prompt)

print(final_flow)