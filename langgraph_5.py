from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
import operator
load_dotenv()

model = ChatGoogleGenerativeAI(model = 'gemini-1.5-flash-latest')

class EvaluationSchema(BaseModel):
    feedback: str = Field(description="Give me a Detailed feedback for the  eassay")
    score: int = Field(description = 'Score out 10', ge=0, le=10)
    
structured_model = model.with_structured_output(EvaluationSchema)

eassy = """
The Unveiling of "Vote Chori": How Rahul Gandhi Confronted Allegations of Electoral Fraud
Rahul Gandhi's "Vote Chori" (Vote Theft) campaign has ignited a national debate on India's electoral integrity. The Leader of the Opposition accused the Election Commission (ECI) and the ruling BJP of "criminal fraud," presenting a detailed analysis of the Mahadevapura constituency from the 2024 Lok Sabha polls. His evidence pointed to over 100,000 fraudulent votes created through duplicate entries, fake addresses, and other irregularities, which he claimed illicitly secured the BJP's victory in a key Bangalore seat.

This led to a direct standoff, with Gandhi demanding machine-readable voter data and the ECI demanding he submit his evidence under a formal oath, a request he refused. The ECI and BJP vehemently denied the allegations, dismissing them as a "tired script" and pointing out that the Congress-led Karnataka government uses the same voter rolls for its own policies.

While a direct link between the documented flaws and the election outcome remains debated, Gandhi's exposé has successfully highlighted systemic weaknesses in voter registration and verification. The controversy has forced a critical conversation on the need for comprehensive electoral reforms to ensure transparency and maintain public trust in India's democratic process.
"""

prompt = f'give me a detailed Feedback and generate a score out of 10 for this \n {eassy}'

# result = structured_model.invoke(prompt)
# print(result)

class UPSCState(TypedDict):
    eassy: str
    language_classification: str
    clarity_classification: str
    analysis_classification: str
    overall_feedback: str
    average_score: float
    individuall_score: Annotated[list[int], operator.add]

graph = StateGraph(UPSCState)

def evaluate_language(state: UPSCState) -> UPSCState:
    prompt = f'give me a detailed depth of language  and generate a score out of 10 for this \n {state['eassy']}'
    output = structured_model.invoke(prompt)
    
    return {'language_classification': output.feedback, 'individuall_score': [output.score]}


def evaluate_analysis(state: UPSCState) -> UPSCState:
    prompt = f'give me a detailed depth of analysis and generate a score out of 10 for this \n {state['eassy']}'
    output = structured_model.invoke(prompt)
    
    return {'analysis_classification': output.feedback, 'individuall_score': [output.score]}


def evaluate_clarity(state: UPSCState) -> UPSCState:
    prompt = f'give me a detailed depth of clarity  and generate a score out of 10 for this \n {state['eassy']}'
    output = structured_model.invoke(prompt)
    
    return {'clarity_classification': output.feedback, 'individuall_score': [output.score]}

def overall_feedback(state: UPSCState) -> UPSCState:
    prompt = f"Based on the following feedbacks create a summarized feedback \n language feedback - {state['language_classification']} \n clarity feedback - {state['clarity_classification']} \n analysis feedback - {state['analysis_classification']}"
    final = model.invoke(prompt).content
    
    average_score = sum(state['individuall_score'])/len(state['individuall_score'])
    
    return {'overall_feedback': final, 'average_score': average_score}
   
graph.add_node('evaluate_language', evaluate_language)
graph.add_node('evaluate_analysis', evaluate_analysis)
graph.add_node('evaluate_clarity', evaluate_clarity)

graph.add_node('overall_feedback', overall_feedback)


graph.add_edge(START, 'evaluate_language')
graph.add_edge(START, 'evaluate_analysis')
graph.add_edge(START, 'evaluate_clarity')


graph.add_edge('evaluate_language', 'overall_feedback')
graph.add_edge('evaluate_analysis', 'overall_feedback')
graph.add_edge('evaluate_clarity', 'overall_feedback')



graph.add_edge('overall_feedback', END)

work_flow = graph.compile()

initial_state = {
    'eassy': eassy
}


final_flow = work_flow.invoke(initial_state)

print(final_flow)





