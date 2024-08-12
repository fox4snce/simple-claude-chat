import os
import json
from datetime import datetime

CONVERSATIONS_DIR = "conversations"

if not os.path.exists(CONVERSATIONS_DIR):
    os.makedirs(CONVERSATIONS_DIR)

def save_conversation(conversation_id, conversation):
    file_path = os.path.join(CONVERSATIONS_DIR, f"{conversation_id}.json")
    with open(file_path, 'w') as f:
        json.dump(conversation, f, indent=2)

def load_conversation(conversation_id):
    file_path = os.path.join(CONVERSATIONS_DIR, f"{conversation_id}.json")
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            return json.load(f)
    return None

def delete_conversation(conversation_id):
    file_path = os.path.join(CONVERSATIONS_DIR, f"{conversation_id}.json")
    if os.path.exists(file_path):
        os.remove(file_path)
        return True
    return False

def list_conversations():
    conversations = []
    for filename in os.listdir(CONVERSATIONS_DIR):
        if filename.endswith(".json"):
            conversation_id = filename[:-5]  # Remove .json extension
            conversation = load_conversation(conversation_id)
            if conversation:
                conversations.append({
                    'id': conversation_id,
                    'name': conversation['name'],
                    'last_updated': conversation['last_updated']
                })
    return sorted(conversations, key=lambda x: x['last_updated'], reverse=True)

def generate_conversation_id():
    return datetime.now().strftime("%Y%m%d%H%M%S")