from atlassian import Confluence
import os

class ConfluenceAgent:
    def __init__(self):
        self.confluence = Confluence(
            url=os.getenv("CONFLUENCE_URL"),
            username=os.getenv("CONFLUENCE_USER"),
            password=os.getenv("CONFLUENCE_API_TOKEN")
        )

    def run_from_task(self, params: dict) -> str:
        try:
            if params.get("action") == "create_page":
                page = self.confluence.create_page(
                    space=os.getenv("CONFLUENCE_SPACE_KEY"),
                    title=params["title"],
                    body=params["body"]
                )
                return f"📘 Confluence page created: {page['_links']['base']}{page['_links']['webui']}"
            else:
                return "❓ Unsupported Confluence action"
        except Exception as e:
            return f"❌ Confluence task failed: {str(e)}"

    def run(self, query: str) -> str:
        from config import client

        prompt = f"""
        Convert this Confluence request into structured JSON:
        {{
            "action": "create_page",
            "space": "ENG",
            "title": "Meeting Summary 2025-07-15",
            "body": "This page contains key meeting decisions and tasks."
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

            if action == "create_page":
                page = self.confluence.create_page(
                    space=data["space"],
                    title=data["title"],
                    body=data["body"]
                )
                return f"📘 Confluence page created: {page['_links']['base']}{page['_links']['webui']}"

            elif action == "delete_page":
                self.confluence.remove_page(data["page_id"])
                return f"🗑️ Page {data['page_id']} deleted"

            elif action == "edit_page":
                self.confluence.update_page(
                    page_id=data["page_id"],
                    title=data["title"],
                    body=data["body"]
                )
                return f"✏️ Page {data['page_id']} updated"

            else:
                return "❓ Unsupported Confluence action."
        except Exception as e:
            return f"❌ Failed to process Confluence action: {str(e)}"
