import os
import openai
# from openai import OpenAI
import json

OPENAI_KEY=""

client = openai.ChatCompletion(api_key=OPENAI_KEY)

# TODO: Add Function calls, json support.

openai.api_key=""

class Responce():
    def __init__(self,model: str = None) -> None:
        if model:
            self.model = model
        else:
            self.model = "gpt-3.5-turbo-1106"


    def func_responce(self,system_message, messages,function = True,stream:bool = True):
        if function:
            response = client.create(
            model=self.model,
            temperature = 0.0,
            response_format={ "type": "json_object" },
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": messages}
            ],
            )
            return response.choices[0].message.content
        else:
            return openai.ChatCompletion.create(model = self.model, messages = [{'role': self.role, 'content': messages}],)
    
    def token_used(self,responce):
        print(responce)
        return responce['usage']['total_tokens']
