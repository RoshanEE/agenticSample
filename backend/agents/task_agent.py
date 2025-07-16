import re
import json
from backend.task_executor import route_to_agent
from functools import partial


class TaskAgent:
    def run(self, query: str, transcript: str):
        from config import client
        import json

        prompt = f"""
                    You are a helpful assistant extracting tasks from a meeting transcript.

                    Your ONLY output must be a JSON array of task objects — no explanations, no text outside the JSON.

                    Each task object must have these fields:

                    - label: short string describing the task (for UI button)
                    - agent: the system to handle the task (one of: "jira", "confluence")
                    - params: an object with parameters specific to that agent, for example:

                    Important rules:

                        Only use "agent": "jira" for tasks related to issue/ticket management.

                        Use "agent": "confluence" for tasks that involve documentation or pages.

                        If the task doesn't clearly map to an agent, set "agent": "none".

                        Do not invent agent names. Valid agents are: jira, confluence, none.

                        Keep the assignee, summary and descripton fields even if the agent is none

                    For Jira tasks, params should include:
                    {{
                        "action": "create_ticket",
                        "project": "ENG",
                        "summary": "Fix login bug",
                        "description": "User login fails with 500 error",
                        "issue_type": "Bug",
                        "assignee": "User that has been assigned that task determined from transcript"
                    }}

                    For Confluence tasks, params should include:
                    {{
                        "action": "create_page",
                        "space": "TEAM",
                        "title": "Meeting Summary 2025-07-15",
                        "body": "Summary content goes here.",
                        "assignee": "User that has been assigned that task determined from transcript"
                    }}

                    Example output:
                    ```json
                    [
                    {{
                        "label": "Create login bug ticket",
                        "agent": "jira",
                        "params": {{
                        "action": "create_ticket",
                        "project": "ENG",
                        "summary": "Fix login bug",
                        "description": "User login fails with 500 error",
                        "issue_type": "Bug",
                        "assignee": "Roshan"
                        }}
                    }},
                    {{
                        "label": "Publish meeting summary",
                        "agent": "confluence",
                        "params": {{
                        "action": "create_page",
                        "space": "TEAM",
                        "title": "Meeting Summary 2025-07-15",
                        "body": "Summary content goes here.",
                        "assignee": "Roshan"
                        }}
                    }}
                    ]
                    Meeting transcript:
                    {transcript[:3000]}
                """

        response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
        )

        raw_output = response.choices[0].message.content.strip()

        # Extract JSON block from markdown
        match = re.search(r"```json\s*(\[\s*[\s\S]*?\s*\])\s*```", raw_output)

        if match:
            json_text = match.group(1)
        else:
            # No triple backticks found, try to parse entire output as JSON
            json_text = raw_output

        try:
            tasks = json.loads(json_text)
        except json.JSONDecodeError as e:
            return {
                "message": f"❌ Failed to parse JSON:\n{str(e)}\n\nRaw response:\n{raw_output}",
                "action_buttons": []
            }

        action_buttons = []
        for i, task in enumerate(tasks):
            label = task.get("label", f"Execute Task {i+1}")
            agent_name = task["agent"]
            params = task["params"]

            action_fn = partial(route_to_agent, agent_name, params)
            action_buttons.append((label, action_fn))

        return {
                "message": "### Task Suggestions\n" + "\n".join(
                    f"**{t['label']}** — via `{t['agent']}`" for t in tasks
                ),
                "tasks": tasks  # keep raw task data
            }