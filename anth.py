# anth.py

import anthropic
import json

client = anthropic.Anthropic()

def generate_response(system=None, user_message=None, max_tokens=4096, temperature=0.8):
    

    system_prompt = f'''
    
    Always use well-formatted markdown.

    {system}
    '''

    if user_message is None:
        user_message = "You are a helpful assistant."
    messages = [{"role": "user", "content": user_message}]
    
    print(f"System prompt: {system_prompt}")

    kwargs = {
        "model": "claude-3-5-sonnet-20240620",
        "max_tokens": max_tokens,
        "temperature": temperature,
        "messages": messages,
        "system" : system_prompt
    }
    
    
    response = client.messages.create(**kwargs)
    return response.content[0].text

def generate_text_response(system=None, user_message=None, max_tokens=4096, temperature=0.8):
    response = generate_response(system, user_message, max_tokens, temperature)
    return response.content[0].text

def generate_json_response(system=None, user_message=None, max_tokens=4096, temperature=0.8):
    if user_message is None:
        user_message = "Please provide your response in valid JSON format."
    else:
        user_message += "\nPlease provide your response in valid JSON format."
    response = generate_response(system, user_message, max_tokens, temperature)
    try:
        json_response = json.loads(response.content[0].text)
    except json.JSONDecodeError:
        return response.content[0].text
    return json_response