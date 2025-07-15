from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from typing import TypedDict
import os

# Define the state schema that LangGraph requires
class AgentState(TypedDict):
    messages: list
    current_step: str
    status: str

# AI Systems Engineer prompt
AI_SYSTEMS_ENGINEER_PROMPT = """You are the AI Systems Engineer for NovaOS.
Your job is to initialize the system, check core agents, and route tasks accordingly.
Begin by confirming that the Automation Architect should take over."""

# Automation Architect prompt
AUTOMATION_ARCHITECT_PROMPT = """You are the Automation Architect for NovaOS.
You design n8n workflows, Dropbox sync, and external automations.
Confirm you are online and ready for configuration."""

# Initialize the LLM
llm = ChatOpenAI(model="gpt-4o", temperature=0)

def ai_systems_engineer(state: AgentState) -> AgentState:
    print("🟢 AI Systems Engineer is booting...")
    
    try:
        response = llm.invoke(AI_SYSTEMS_ENGINEER_PROMPT)
        print("🧠 AI Systems Engineer:", response.content)
        
        # Update state
        state["messages"].append({"role": "ai_systems_engineer", "content": response.content})
        state["current_step"] = "ai_systems_engineer_complete"
        state["status"] = "success"
        
    except Exception as e:
        print(f"❌ Error in AI Systems Engineer: {e}")
        state["status"] = "error"
        state["messages"].append({"role": "error", "content": str(e)})
    
    return state

def automation_architect(state: AgentState) -> AgentState:
    print("🔧 Automation Architect is now active...")
    
    try:
        response = llm.invoke(AUTOMATION_ARCHITECT_PROMPT)
        print("🧠 Automation Architect:", response.content)
        
        # Update state
        state["messages"].append({"role": "automation_architect", "content": response.content})
        state["current_step"] = "automation_architect_complete"
        state["status"] = "success"
        
    except Exception as e:
        print(f"❌ Error in Automation Architect: {e}")
        state["status"] = "error"
        state["messages"].append({"role": "error", "content": str(e)})
    
    return state

def main():
    print("🚀 Starting NovaOS LangGraph System...")
    
    # Check if OpenAI API key is available
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY not found in environment variables")
        return
    
    print("✅ OpenAI API Key found")
    
    # Create the state graph
    graph = StateGraph(AgentState)
    
    # Add nodes
    graph.add_node("ai_systems_engineer", ai_systems_engineer)
    graph.add_node("automation_architect", automation_architect)
    
    # Set entry point
    graph.set_entry_point("ai_systems_engineer")
    
    # Add edges
    graph.add_edge("ai_systems_engineer", "automation_architect")
    graph.add_edge("automation_architect", END)
    
    # Compile the graph
    app = graph.compile()
    
    # Initialize state
    initial_state = {
        "messages": [],
        "current_step": "starting",
        "status": "pending"
    }
    
    # Run the graph
    print("🎯 Invoking agent workflow...")
    try:
        result = app.invoke(initial_state)
        print("✅ NovaOS Agent System Boot Complete!")
        print(f"📊 Final Status: {result.get('status', 'unknown')}")
        print(f"📝 Steps Completed: {len(result.get('messages', []))}")
        
    except Exception as e:
        print(f"❌ Error running workflow: {e}")

if __name__ == "__main__":
    main()
