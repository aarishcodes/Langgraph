#<-----------------------------------Sequential Work Flow ----------------->


from langgraph.graph import StateGraph, START, END
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from typing import TypedDict

load_dotenv()
model = ChatGoogleGenerativeAI(model='gemini-1.5-flash-latest')

class BlogState(TypedDict):
    title: str
    outline: str
    content: str
    evaluation: int
    
graph = StateGraph(BlogState)

def create_outline(state: BlogState) -> BlogState:
    title = state['title']
    prompt = f'create a outline on the topic - {title}'
    
    outline = model.invoke(prompt).content
    state['outline'] = outline
    
    return state

def create_blog(state: BlogState) -> BlogState:
    title = state['title']
    outline = state['outline']
    
    prompt = f'Write me a detailed Blog on the topic - {title} on the outline \n {outline}'
    
    content = model.invoke(prompt).content
    state['content'] = content
    
    return state


def evaluation(state: BlogState) -> BlogState:
    outline = state['outline']
    content = state['content']
    prompt = f'Give me a Evaluation Score on the basis of this {outline} of this {content}'
    evaluation = model.invoke(prompt).content
    state['evaluation'] = evaluation
    
    return state

graph.add_node('create_blog', create_blog)
graph.add_node('create_outline', create_outline)
graph.add_node('evaluation', evaluation)

graph.add_edge(START, 'create_outline')
graph.add_edge('create_outline','create_blog')
graph.add_edge('create_blog', 'evaluation')
graph.add_edge('evaluation', END)


workflow = graph.compile()

intital_prompt = {'title': 'How Langgraph is channging the world'}

final_flow = workflow.invoke(intital_prompt)

# print(final_flow)
# print(final_flow['title'])
# print(final_flow['content'])
# print(final_flow['outline'])
print(final_flow['evaluation'])
