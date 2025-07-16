# base_agent.py
class BaseAgent:
    identity = {
        "name": "base",
        "description": "Base agent class"
    }
    
    def run(self, query: str, context: dict) -> str:
        raise NotImplementedError("Each agent must implement the run method.")
