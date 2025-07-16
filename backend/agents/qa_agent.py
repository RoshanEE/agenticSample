from config import client

class QAAgent:
    def run(self, query: str, transcript: str) -> str:
        messages = [
            {"role": "system", "content": "You're a meeting assistant helping answer questions from the transcript."},
            {"role": "user", "content": f"Transcript:\n{transcript[:3000]}"},
            {"role": "user", "content": f"Question: {query}"}
        ]
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
        )
        return response.choices[0].message.content.strip()
