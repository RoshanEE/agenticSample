from config import client

class SummaryAgent:
    def run(self, transcript: str) -> str:
        prompt = f"Summarize the following Webex meeting transcript:\n\n{transcript[:3000]}"
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()
