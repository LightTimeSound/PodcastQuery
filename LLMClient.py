import requests
from openai import OpenAI

class LLMClient:
    def __init__(self, base_url):
        self.client = OpenAI(base_url=base_url, api_key="not-needed")
        self.model = "local-model"
        self.system_message = "You are an AI that is exceptional at summarizing text and providing key insights from the text."
        self.temperature = 0.5
    
    def summarize(self, text, max_tokens=3000):
        completion = self.client.chat.completions.create(
        model=self.model,
        messages=[
            {"role": "system", "content": self.system_message},
            {"role": "user", "content": text}
        ],
        temperature=self.temperature,
        )
        
        return completion.choices[0].message.content