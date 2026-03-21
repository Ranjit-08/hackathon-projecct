from flask import Blueprint, request, jsonify
import requests
from config import Config
from utils.jwt_helper import token_required

mock_bp = Blueprint('mock', __name__)

SYSTEM_PROMPT = """You are an expert technical interviewer. Your goal:
1. Greet the candidate and ask what role they are preparing for.
2. Ask ONE focused interview question at a time (mix technical + behavioral).
3. After each answer, give brief constructive feedback (2-3 sentences).
4. Adapt next question based on the answer.
5. After 5-6 exchanges, give a final overall assessment with strengths and areas to improve.

Keep tone professional but encouraging. Format each response clearly:
- If asking a question: state it plainly
- If giving feedback: start with "📝 Feedback:" then the feedback, then ask the next question

Start: Greet the candidate warmly and ask what role they are interviewing for."""

@mock_bp.route('/chat', methods=['POST'])
@token_required(role='user')
def chat():
    d        = request.get_json() or {}
    messages = d.get('messages', [])
    if not isinstance(messages, list):
        return jsonify({'error': 'messages must be a list'}), 400

    try:
        resp = requests.post(
            'https://api.groq.com/openai/v1/chat/completions',
            headers={
                'Authorization': f'Bearer {Config.GROQ_API_KEY}',
                'Content-Type':  'application/json'
            },
            json={
                'model':    Config.GROQ_MODEL,
                'messages': [{'role': 'system', 'content': SYSTEM_PROMPT}, *messages],
                'max_tokens':  600,
                'temperature': 0.75
            },
            timeout=30
        )
        if resp.status_code != 200:
            return jsonify({'error': 'AI service unavailable', 'detail': resp.text}), 502
        return jsonify({'message': resp.json()['choices'][0]['message']['content']})
    except requests.Timeout:
        return jsonify({'error': 'AI service timed out, please retry'}), 504
    except Exception as e:
        return jsonify({'error': str(e)}), 500