from atlassian import Jira
import os

class JiraAgent:
    def __init__(self):
        self.jira = Jira(
            url=os.getenv("JIRA_URL"),
            username=os.getenv("JIRA_USER"),
            password=os.getenv("JIRA_API_TOKEN")
        )

    def run_from_task(self, params: dict) -> str:
        try:
            action = params.get("action")
            if action == "create_ticket":
                issue = self.jira.issue_create(fields={
                    "project": {"key":os.getenv("JIRA_PROJECT_KEY")},
                    "summary": params["summary"],
                    "description": params["description"],
                    "issuetype": {"name": params["issue_type"]}
                })
                return f"✅ Jira ticket created: {issue['key']}"
            else:
                return "❓ Unsupported Jira action"
        except Exception as e:
            return f"❌ Jira task failed: {str(e)}"

    def run(self, query: str) -> str:
        # Step 1: Ask GPT to convert query to structured action
        from config import client

        prompt = f"""
        You are an assistant converting natural language Jira requests into structured JSON.
        Respond in JSON like this:
        {{
          "action": "create_ticket",
          "project": "ABC",
          "summary": "Add login endpoint",
          "description": "We need login API by Monday.",
          "issue_type": "Task"
        }}

        Query: {query}
        """

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )

        import json
        try:
            data = json.loads(response.choices[0].message.content)
            action = data.get("action")

            if action == "create_ticket":
                issue = self.jira.issue_create(fields={
                    "project": os.getenv("JIRA_PROJECT_KEY"),
                    "summary": data["summary"],
                    "description": data["description"],
                    "issuetype": {"name": data["issue_type"]}
                })
                return f"✅ Jira ticket created: {issue['key']}"

            elif action == "delete_ticket":
                self.jira.issue_delete(data["ticket_key"])
                return f"🗑️ Jira ticket {data['ticket_key']} deleted"

            elif action == "edit_ticket":
                self.jira.issue_update(issue_key=data["ticket_key"], fields=data["fields"])
                return f"✏️ Jira ticket {data['ticket_key']} updated"

            else:
                return "❓ Unsupported Jira action."
        except Exception as e:
            return f"❌ Failed to process Jira action: {str(e)}"
