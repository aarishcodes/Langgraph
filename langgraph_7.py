# =======================Contitional WorkFLow Better Example ===============================

from langgraph.graph import StateGraph, START, END
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from typing import TypedDict, Literal
from pydantic import BaseModel, Field


load_dotenv()

model = ChatGoogleGenerativeAI(model='gemini-1.5-flash-latest')

class ReviewState(TypedDict):
    review: str
    sentiment: str
    diagnosis: dict
    response: str
    
graph = StateGraph(ReviewState)

class ReviewSchema(BaseModel):
    sentiment: Literal["positive", "negative"] = Field(description='Sentiment of the review')

class DiagnosisSchema(BaseModel):
    issue_type: Literal["UX", "Performance", "Bug", "Support", "Other"] = Field(description='The category of issue mentioned in the review')
    tone: Literal["angry", "frustrated", "disappointed", "calm"] = Field(description='The emotional tone expressed by the user')
    urgency: Literal["low", "medium", "high"] = Field(description='How urgent or critical the issue appears to be')

structure_model = model.with_structured_output(ReviewSchema)

structure_model2 = model.with_structured_output(DiagnosisSchema)


def find_sentiment(state: ReviewState)->ReviewState:
    prompt = f'For the following review find out the sentiment \n {state["review"]}'
    
    sentiment = structure_model.invoke(prompt).sentiment
    
    return {'sentiment': sentiment}

def positive_response(state: ReviewState) -> ReviewState:
    prompt = f"""Write a warm thank-you message in response to this review:
    \n\n\"{state['review']}\"\n
    Also, kindly ask the user to leave feedback on our website."""
    
    response = model.invoke(prompt).content
    
    return {'response': response}

def generate_diagnoses(state: ReviewState) -> ReviewState:
    prompt = f"""Diagnose this negative review:\n\n{state['review']}\n"
    "Return issue_type, tone, and urgency.
    """
    response = structure_model2.invoke(prompt)

    return {'diagnosis': response.model_dump()}
    
    
def negative_response(state: ReviewState) -> ReviewState:
    diagnosis = state['diagnosis']

    prompt = f"""You are a support assistant.
    The user had a '{diagnosis['issue_type']}' issue, sounded '{diagnosis['tone']}', and marked urgency as '{diagnosis['urgency']}'.
    Write an empathetic, helpful resolution message.
    """
    
    response = model.invoke(prompt).content

    return {'response': response }


    
def check_condition(state: ReviewState) -> Literal["positive_response", "generate_diagnoses"]:
    if state['sentiment'] == 'positive':
        return "positive_response"
    else:
        return "generate_diagnoses"
    

# Nodes
graph.add_node('find_sentiment', find_sentiment)
graph.add_node('positive_response', positive_response)

graph.add_node('generate_diagnoses', generate_diagnoses)
graph.add_node('negative_response', negative_response)


graph.add_edge(START, 'find_sentiment')

graph.add_conditional_edges('find_sentiment', check_condition)

graph.add_edge('positive_response', END)


graph.add_edge('generate_diagnoses', 'negative_response')
graph.add_edge('negative_response', END)


work_flow = graph.compile()


intial_state={
    'review': "I’ve been trying to log in for over an hour now, and the app keeps freezing on the authentication screen. I even tried reinstalling it, but no luck. This kind of bug is unacceptable, especially when it affects basic functionality."
}


final_flow=work_flow.invoke(intial_state)

print(final_flow)

