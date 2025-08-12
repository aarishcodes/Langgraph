from langgraph.graph import StateGraph, START, END
from typing import TypedDict
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()
model = ChatGoogleGenerativeAI(model='gemini-1.5-flash-latest')

class QuestionClass(TypedDict):
    question: str
    answer: str

graph = StateGraph(QuestionClass)

def llm_que(state: QuestionClass) -> QuestionClass:
    question = state['question']
    prompt = f'Answer my Question with a simple response \n {question}'
    answer = model.invoke(prompt).content
    
    state['answer'] = answer
    return state
    

graph.add_node('llm_que', llm_que)

graph.add_edge(START, 'llm_que')
graph.add_edge('llm_que', END)

workflow = graph.compile()

intital_input = {'question': 'Hey Are are you doing'}
final_flow = workflow.invoke(intital_input)

print(final_flow)