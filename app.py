from flask import Flask, render_template, request, jsonify
import anth
from prompt_routes import prompt_routes
from conversation_routes import conversation_routes
from conversation_utils import save_conversation, load_conversation, generate_conversation_id
from config import MAX_CONTEXT_TOKENS, MAX_OUTPUT_TOKENS
from utils import calculate_cost
from datetime import datetime

app = Flask(__name__, template_folder='templates')
app.register_blueprint(prompt_routes)
app.register_blueprint(conversation_routes)

client = anth.client

current_conversation_id = None
current_system_prompt = ""

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    global current_conversation_id, current_system_prompt
    
    data = request.get_json()
    user_message = data['user_message']
    max_tokens = min(int(data.get('max_tokens', MAX_CONTEXT_TOKENS)), MAX_CONTEXT_TOKENS)

    if current_conversation_id is None:
        current_conversation_id = generate_conversation_id()
        conversation = {
            'name': 'New Conversation',
            'messages': [],
            'last_updated': datetime.now().isoformat()
        }
    else:
        conversation = load_conversation(current_conversation_id)

    conversation['messages'].append({"role": "user", "content": user_message})
    full_message = "\n".join([f"{msg['role'].capitalize()}: {msg['content']}" for msg in conversation['messages']])
    
    input_tokens = client.count_tokens(full_message)

    while input_tokens > max_tokens and len(conversation['messages']) > 1:
        conversation['messages'].pop(0)
        full_message = "\n".join([f"{msg['role'].capitalize()}: {msg['content']}" for msg in conversation['messages']])
        input_tokens = client.count_tokens(full_message)

    response_text = anth.generate_text_response(
        system=current_system_prompt,
        user_message=full_message,
        max_tokens=MAX_OUTPUT_TOKENS,
        temperature=0.7
    )

    output_tokens = client.count_tokens(response_text)

    conversation['messages'].append({"role": "assistant", "content": response_text})
    conversation['last_updated'] = datetime.now().isoformat()

    # Generate conversation name if it's a new conversation
    if conversation['name'] == 'New Conversation':
        name_prompt = f"""Based on the following conversation, suggest an extremely short (1-5 words) but descriptive name for it. The name should capture the essence of the conversation.

        RETURN ONLY the name without punctuation or intermediate steps.

    Examples:
    Conversation: "How do I bake chocolate chip cookies from scratch?"
    Name: "Baking Chocolate Chip Cookies"

    Conversation: "What are the best places to visit in Paris for a first-time traveler?"
    Name: "Paris Travel Tips"

    Conversation: "Can you explain the basics of quantum computing?"
    Name: "Quantum Computing Basics"

    Now, here's the conversation to name:

    {full_message}

    Suggested name:"""

        conversation_name = anth.generate_text_response(
            system="You are an expert at creating concise, relevant titles for conversations. Your task is to generate extremely short (1-5 words) but descriptive names based on the conversation content. Focus on the main topic or theme.",
            user_message=name_prompt,
            max_tokens=10,
            temperature=0.5
        ).strip()
        conversation['name'] = conversation_name

    save_conversation(current_conversation_id, conversation)

    total_cost = calculate_cost(input_tokens, output_tokens)

    return jsonify({
        'conversation_id': current_conversation_id,
        'conversation_name': conversation['name'],
        'response': response_text,
        'input_tokens': input_tokens,
        'output_tokens': output_tokens,
        'total_cost': total_cost
    })

@app.route('/set_current_conversation', methods=['POST'])
def set_current_conversation():
    global current_conversation_id
    data = request.get_json()
    conversation_id = data['conversation_id']
    conversation = load_conversation(conversation_id)
    if conversation:
        current_conversation_id = conversation_id
        return jsonify({'status': 'success', 'conversation': conversation})
    else:
        return jsonify({'status': 'error', 'message': 'Conversation not found'}), 404

@app.route('/system_prompt', methods=['GET', 'POST'])
def system_prompt():
    global current_system_prompt
    if request.method == 'POST':
        data = request.get_json()
        current_system_prompt = data['system_prompt']
        return jsonify({'status': 'system prompt updated'})
    else:
        return jsonify({'system_prompt': current_system_prompt})

if __name__ == '__main__':
    app.run(debug=True)