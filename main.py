from langchain.chat_models import ChatOpenAI
from langgraph.graph import StateGraph, END

AI_SYSTEMS_ENGINEER_PROMPT = """You are the AI Systems Engineer for NovaOS.
Your job is to initialize the system, check core agents, and route tasks accordingly.
Begin by confirming that the Automation Architect should take over.
"""

AUTOMATION_ARCHITECT_PROMPT = """You are the Automation Architect for NovaOS.
You design n8n workflows, Dropbox sync, and external automations.
Confirm you are online and ready for configuration.
"""

llm = ChatOpenAI(model="gpt-4o", temperature=0)

def ai_systems_engineer(state):
    print("🟢 AI Systems Engineer is booting...")
    response = llm.invoke(AI_SYSTEMS_ENGINEER_PROMPT)
    print("🧠 AI Systems Engineer:", response.content)
    return state

def automation_architect(state):
    print("🔧 Automation Architect is now active...")
    response = llm.invoke(AUTOMATION_ARCHITECT_PROMPT)
    print("🧠 Automation Architect:", response.content)
    return state

graph = StateGraph()
graph.add_node("ai_systems_engineer", ai_systems_engineer)
graph.add_node("automation_architect", automation_architect)
graph.set_entry_point("ai_systems_engineer")
graph.add_edge("ai_systems_engineer", "automation_architect")
graph.set_finish_point("automation_architect")

app = graph.compile()
app.invoke({})
