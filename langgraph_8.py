from langgraph.graph import StateGraph, START, END
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from typing import TypedDict, Literal
from pydantic import BaseModel, Field
from langchain_core.messages import HumanMessage, SystemMessage


load_dotenv()

generate_llm = ChatGoogleGenerativeAI(model='gemini-1.5-flash-latest')
optimize_llm = ChatGoogleGenerativeAI(model='gemini-1.5-flash-latest')
evaluate_llm = ChatGoogleGenerativeAI(model='gemini-1.5-flash-latest')

class XtweetGenerator(TypedDict):
    topic: str
    tweet: str
    evaluation: Literal['approved', 'not_approved']
    iteration: int
    max_iteration: int
    feedback: str
    
    
graph = StateGraph(XtweetGenerator)

class TweetSchema(BaseModel):
    evaluation: Literal["approved", "needs_improvement"] = Field(..., description="Final evaluation result.")
    feedback: str = Field(..., description="feedback for the tweet.")

structure_evaluate_model = evaluate_llm.with_structured_output(TweetSchema)


def generate_tweet(state: XtweetGenerator)-> XtweetGenerator:
    messages = [
        SystemMessage(content="You are a funny and clever Twitter/X influencer."),
        HumanMessage(content=f"""
        Write a short, original, and hilarious tweet on the topic: "{state['topic']}".

        Rules:
        - Do NOT use question-answer format.
        - Max 280 characters.
        - Use observational humor, irony, sarcasm, or cultural references.
        - Think in meme logic, punchlines, or relatable takes.
        - Use simple, day to day english
        """)
    ]
    tweet = generate_llm.invoke(messages).content

    return {'tweet': tweet}



def evaluate_tweet(state: XtweetGenerator):
    messages = [
    SystemMessage(content="You are a ruthless, no-laugh-given Twitter critic. You evaluate tweets based on humor, originality, virality, and tweet format."),
    HumanMessage(content=f"""
        Evaluate the following tweet:

        Tweet: "{state['tweet']}"

        Use the criteria below to evaluate the tweet:

        1. Originality – Is this fresh, or have you seen it a hundred times before?  
        2. Humor – Did it genuinely make you smile, laugh, or chuckle?  
        3. Punchiness – Is it short, sharp, and scroll-stopping?  
        4. Virality Potential – Would people retweet or share it?  
        5. Format – Is it a well-formed tweet (not a setup-punchline joke, not a Q&A joke, and under 280 characters)?

        Auto-reject if:
        - It's written in question-answer format (e.g., "Why did..." or "What happens when...")
        - It exceeds 280 characters
        - It reads like a traditional setup-punchline joke
        - Dont end with generic, throwaway, or deflating lines that weaken the humor (e.g., “Masterpieces of the auntie-uncle universe” or vague summaries)

        ### Respond ONLY in structured format:
        - evaluation: "approved" or "needs_improvement"  
        - feedback: One paragraph explaining the strengths and weaknesses 
        """)
    ]

    response = structure_evaluate_model.invoke(messages)

    return {'evaluation':response.evaluation, 'feedback': response.feedback}
    

def optimize_tweet(state: XtweetGenerator)-> XtweetGenerator:
    messages = [
        SystemMessage(content="You punch up tweets for virality and humor based on given feedback."),
        HumanMessage(content=f"""
        Improve the tweet based on this feedback:
        "{state['feedback']}"

        Topic: "{state['topic']}"
        Original Tweet:
        {state['tweet']}

        Re-write it as a short, viral-worthy tweet. Avoid Q&A style and stay under 280 characters.
        """)
            ]

    response = optimize_llm.invoke(messages).content
    iteration = state['iteration'] + 1

    return {'tweet': response, 'iteration': iteration}
    
def route_evaluation(state: XtweetGenerator):

    if state['evaluation'] == 'approved' or state['iteration'] >= state['max_iteration']:
        return 'approved'
    else:
        return 'needs_improvement'    
    
    
graph.add_node('generate_tweet', generate_tweet)
graph.add_node('evaluate_tweet', evaluate_tweet)
graph.add_node('optimize_tweet', optimize_tweet)

graph.add_edge(START, 'generate_tweet')
graph.add_edge('generate_tweet', 'evaluate_tweet')
graph.add_conditional_edges('evaluate_tweet', route_evaluation, {'approved': END, 'needs_improvement': 'optimize_tweet'})

graph.add_edge('optimize_tweet', 'evaluate_tweet')

work_flow = graph.compile()

initial_state = {
    "topic": "Indian Politics",
    "iteration": 1,
    "max_iteration": 5
}

final_flow = work_flow.invoke(initial_state)

print(final_flow['tweet'])
