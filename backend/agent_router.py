from config import client
from backend.agents.summary_agent import SummaryAgent
from backend.agents.qa_agent import QAAgent
from backend.agents.task_agent import TaskAgent
from backend.agents.jira_agent import JiraAgent
from backend.agents.confluence_agent import ConfluenceAgent

def route_query(query: str, transcript: str):
    system_prompt = (
        "You're a smart router. Based on the query and transcript, decide which agent is best:\n"
        "- 'summary' for meeting summaries\n"
        "- 'qa' for Q&A on the transcript\n"
        "- 'task' for deciding tasks from the meeting\n"
        "- 'jira' for ticket-related tasks\n"
        "- 'confluence' for wiki/page tasks\n"
        "Only respond with the agent name."
    )
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Query: {query}\nTranscript:\n{transcript[:2000]}"}
    ]

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )
    agent = response.choices[0].message.content.strip().lower()

    if agent == "summary":
        return {"message": SummaryAgent().run(transcript)}
    elif agent == "qa":
        return {"message": QAAgent().run(query, transcript)}
    elif agent == "task":
        return TaskAgent().run(query, transcript)
    elif agent == "jira":
        return {"message": JiraAgent().run(query)}
    elif agent == "confluence":
        return {"message": ConfluenceAgent().run(query)}
    else:
        return {"message": "❌ Could not determine the right agent."}

def route_to_agent(agent: str, params: dict) -> str:
    if agent == "jira":
        return JiraAgent().run_from_task(params)
    elif agent == "confluence":
        return ConfluenceAgent().run_from_task(params)
    else:
        return f"❌ Unknown agent: {agent}"