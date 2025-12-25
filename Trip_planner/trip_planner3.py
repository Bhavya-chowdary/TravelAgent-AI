"""
Trip Planner 3 - LangGraph based travel itinerary generator
Uses Groq LLM and Tavily API for research
"""

import os
from dotenv import load_dotenv
load_dotenv()

# ============================================
# 1. Load API Keys
# ============================================
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

# ============================================
# 2. Define State Schema
# ============================================
from typing import TypedDict, List
from langgraph.graph import StateGraph, START, END

class Tripplannerstate(TypedDict):
    destination: str
    dates: str
    content: List[str]
    itinerary: str

# ============================================
# 3. Initialize LLM
# ============================================
from langchain_groq import ChatGroq
model = ChatGroq(api_key=GROQ_API_KEY, model="llama-3.1-8b-instant", temperature=0.7)

PLAN_PROMPT = """You are an expert travel planner tasked with creating a high \
level itinerary outline.Write such an outline for the user provided \
destination and dates. Give an outline of the itinerary."""

from langchain_core.messages import SystemMessage, HumanMessage

def plan_node(state: Tripplannerstate) -> Tripplannerstate:
    """Generate high-level itinerary outline"""
    prompt = [
        SystemMessage(content=PLAN_PROMPT),
        HumanMessage(content=f"Destination: {state['destination']}\nDates: {state['dates']}")
    ]
    response = model.invoke(prompt)
    state['itinerary'] = response.content.split('\n')
    return state

# ============================================
# 4. Research Node with Tavily
# ============================================
from pydantic import BaseModel

class Queries(BaseModel):
    queries: List[str]

from tavily import TavilyClient

# Verify API key is loaded
if os.getenv('TAVILY_API_KEY'):
    print("✓ Tavily API Key loaded successfully")
    tavily = TavilyClient(api_key=os.getenv('TAVILY_API_KEY'))
    print("✓ TavilyClient initialized")
else:
    print("✗ TAVILY_API_KEY not found. Please add it to your .env file")
    tavily = None

RESEARCH_PLAN_PROMPT = """You are a travel planner tasked with finding events \
for a user visiting. Generate a list of search queries that will gather \
information on local events during this period such as music festivals, \
food fairs or any other noteworthy events. \
Also mention beaches or natural attractions if relevant or any famous temples \
Also suggest famous or top rated restaurants in the area for Lunch & dinner \
Also suggest best hotels to stay in the area. \
Only generate 3 queries max."""

def research_plan_node(state: Tripplannerstate) -> dict:
    """Search for local events and attractions using Tavily"""
    if tavily is None:
        print("Error: Tavily client not initialized")
        return {'content': []}
    
    queries = model.with_structured_output(Queries).invoke([
        SystemMessage(content=RESEARCH_PLAN_PROMPT),
        HumanMessage(content=f"{state['destination']}\n\nHere is my dates:\n\n{state['dates']}")
    ])
    content = []
    for q in queries.queries:
        response = tavily.search(query=q, max_results=2)
        for r in response['results']:
            content.append(r['content'])
    return {'content': content}

# ============================================
# 5. Generation Node
# ============================================
WRITER_PROMPT = """You are a travel agent tasked with creating the best \
possible travel itinerary for the user's trip. Generate a detailed itinerary \
based on the provided destination, dates, and any relevant information. \
If the user provides feedback or changes, respond with a revised version \
of your previous itinerary.\
While writing, ensure the itinerary is comprehensive and engaging.
i.e plan itinerary as , visit beaches during evening times, 
Utilize all the information below as needed:

{content}
"""

def generation_node(state: Tripplannerstate) -> dict:
    """Generate final detailed itinerary"""
    content = "\n\n".join(state['content'] or [])
    user_message = HumanMessage(
        content=f"{state['destination']}\n\nHere is my dates:\n\n{state['dates']}")
    messages = [
        SystemMessage(content=WRITER_PROMPT.format(content=content)),
        user_message
    ]
    response = model.invoke(messages)
    return {'itinerary': response.content}

# ============================================
# 6. Build Graph
# ============================================
graph_builder = StateGraph(Tripplannerstate)

# Add nodes
graph_builder.add_node('plan_node', plan_node)
graph_builder.add_node('research_node', research_plan_node)
graph_builder.add_node('generation_node', generation_node)

# Add edges
graph_builder.add_edge(START, 'plan_node')
graph_builder.add_edge('plan_node', 'research_node')
graph_builder.add_edge('research_node', 'generation_node')
graph_builder.add_edge('generation_node', END)

# ============================================
# 7. Compile Graph
# ============================================
from langgraph.checkpoint.memory import MemorySaver
memory = MemorySaver()
tripgraph = graph_builder.compile(checkpointer=memory)

# ============================================
# 8. Run Trip Planner
# ============================================
def generate_trip_itinerary(destination: str, dates: str, thread_id: str = '1'):
    """
    Generate a complete trip itinerary for the given destination and dates
    
    Args:
        destination: Travel destination (e.g., "Pondicherry, INDIA")
        dates: Travel dates (e.g., "2025-12-24 to 2025-12-31")
        thread_id: Thread ID for conversation memory
    
    Returns:
        Complete itinerary as a string
    """
    thread = {'configurable': {'thread_id': thread_id}}
    
    print(f"\n🌍 Generating itinerary for {destination} from {dates}...\n")
    
    # Stream the graph execution
    for s in tripgraph.stream({
        'destination': destination,
        'dates': dates
    }, thread):
        print(f"Processing: {list(s.keys())}")
    
    # Get final result
    result = tripgraph.get_state(thread).values
    return result['itinerary']

# ============================================
# 9. Main Execution
# ============================================
if __name__ == "__main__":
    # Example usage
    destination = input("Enter destination: ") or "Pondicherry, INDIA"
    dates = input("Enter dates: ") or "2025-12-24 to 2025-12-31"
    
    itinerary = generate_trip_itinerary(destination, dates)
    
    print("\n" + "="*60)
    print("FINAL ITINERARY")
    print("="*60)
    print(itinerary)
