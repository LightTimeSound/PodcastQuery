import requests
from openai import OpenAI

class LLMClient:
    def __init__(self, base_url, api_key="not-needed"):
        self.client = OpenAI(base_url=base_url, api_key=api_key)
        self.model = "local-model"
    
    def summarize(self, text, max_tokens=3000):
        system_message = "Given the following transcript, summarize the content in 3-5 sentences."
        completion = self.client.chat.completions.create(
        model=self.model,
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": text}
        ],
        temperature=0.5,
        )
        
        return completion.choices[0].message.content
    
    def convert_query_to_search_terms(self, query):
        additional_sys_message = "Given the following prompt, think step-by-step about what terms could be extracted to query a vector database for relevant information. The vector database contains transcripts from a financial and machine learning podcast. You always respond exactly in this format: term1, term2, term3, etc. Your response should consist only of terms and commas."
        completion = self.client.chat.completions.create(
        model=self.model,
        messages=[
            {"role": "system", "content": additional_sys_message},
            {"role": "user", "content": query}
        ],
        temperature=0.0,
        )
        
        return completion.choices[0].message.content