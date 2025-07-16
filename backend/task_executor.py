from backend.agents.jira_agent import JiraAgent
from backend.agents.confluence_agent import ConfluenceAgent

def route_to_agent(agent: str, params: dict) -> str:
    if agent == "jira":
        return JiraAgent().run_from_task(params)
    elif agent == "confluence":
        return ConfluenceAgent().run_from_task(params)
    else:
        return f"❌ Unknown agent: {agent}"
