import docx
import PyPDF2
import os
import requests
import os
from dotenv import load_dotenv
import json
from io import BytesIO
from django.conf import settings
from django.core.mail import send_mail
import base64
from .prompts import mindspace_role_prompt,get_mindspace_input
load_dotenv()


    

def role_classifier(system_role,user_role):
    message = [{
        "role": "system",
        "content": f"""{system_role}"""
        },
    {
        "role": "user",
        "content": f"""{user_role}"""
    }]
    return message


def add_message(role, message , messages):
    messages.append({"role": role, "content": message})


def mindspace_messages(user_query):
    system_role = mindspace_role_prompt
    user_role = get_mindspace_input(user_query)
    message = [{
        'role':"system",
        "content":f"""{system_role}"""
        },
    {
        "role": "user",
            "content": f"""{user_role}"""
        }]

    return message
        
def make_openai_call(messages,model_name='gpt-3.5-turbo',temperature=0.7,stream:bool=True):
    request_payload = {
                'model': model_name,
                'temperature': temperature,
                'messages': messages,
                'stream': stream,
            }
    response = requests.post(
            'https://api.openai.com/v1/chat/completions',
            headers={
                'Authorization': f'Bearer {os.getenv(f"OPENAI_API_KEY")}',
                'Content-Type': 'application/json',
            },
            json=request_payload,
            stream=stream,
        )
    if stream == False:
        res=json.loads(response.content.decode('utf-8'))
        res = res['choices'][0].get('message').get('content')
        print(res)
        return res
    else:
        for chunk in response.iter_lines():
            if chunk:
                payloads = chunk.decode().split("\n\n")
                for payload in payloads:
                    if '[DONE]' in payload:
                        break
                    if payload.startswith("data:"):
                        data = json.loads(payload.replace("data:", ""))
                        yield f"data: {json.dumps(data)}\n\n"

def encode_image(image_path):
    return base64.b64encode(image_path.read()).decode('utf-8')
  
def vision_messages(image_path,vision_role_prompt):
    base64_image = encode_image(image_path)
    message = [{
        'role':"system",
        "content":f"""{vision_role_prompt}"""
        },
    {
        "role": "user",
        "content": [
            {
            "type": "text",
            # "text": f"""{vision_query_prommpt}"""
            "text":"""What is the question addressed in this image."""
            },
            {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{base64_image}",
                "detail": "high"
            }
            }
        ]},
        
    ]

    return message
  
from .prompts import gpt_vision_prompt
def make_openai_vision_call(image_path,model_name='gpt-4-vision-preview',temperature=0.5):

    messages = vision_messages(image_path=image_path,vision_role_prompt=gpt_vision_prompt)
    
    request_payload = {
                'model': model_name,
                'temperature': temperature,
                'messages': messages,
                'max_tokens':4096,
            }
    response = requests.post(
            'https://api.openai.com/v1/chat/completions',
            headers={
                'Authorization': f'Bearer {os.getenv(f"OPENAI_API_KEY")}',
                'Content-Type': 'application/json',
            },
            json=request_payload,
        )
    
    res = response.json()  # Parse response as JSON
    res = res['choices'][0].get('message').get('content')
    return res