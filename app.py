from flask import Flask, request, jsonify, render_template
from worker import agent
from langchain_core.messages import AIMessage
import uuid

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/get_weather', methods=['POST'])
def get_weather():
    user_ask = request.form.get('query')
    if not user_ask:
        return jsonify({"error": "Please provide a query in the request body."}), 400
    response = agent.invoke(
        {"messages":[{'role':'user','content':user_ask}]},
        {'configurable':{"thread_id":str(uuid.uuid4())}}
    )
    last_message = response['messages'][-1]
    # last_message = "[{'type': 'text', 'text': 'Right away, sir. The current weather in Pune, India, is 29.52 degrees Celsius, though it feels more like 29.83 degrees. The humidity is at 46%, and you can expect broken clouds with a gentle wind speed of 0.45 meters per second.', 'extras': {'signature': 'Cr8CAQw51seKl2ug0l9Rl9qT7otlWZ5mao+y5XcXfpRFHEzAmziiz48Nzxa7/+zj7G5++a/xkKgN+aRxt08xgUgrBFAXlnZgh1CGWpg3EbHbN4u2y5QEJGLb//L1zU69NUhIjgLrAdVOjFVIjLxb9wTamyPWkFIuu0V7c38+IWR4MeQC9PUbjT7FJEney2Hhdan6+DAs/H5DzzGff+e1Fw3xvF4IWko04B2/TJyEV8khAzhvQpbB6QDP6AfJgBqRQJypABucc6zkAZm95x9n3Bgt5Fq83Gq/OE7qUsY1msJxA8Ma3k+4U0NfvCfNSKOGgGtpN+XHeAaMANTTKC611k9s5HXPR5PCYqnu768PJwce+y8Wuzud/RmLfYTln0eu1EY8XQq9cx28iBp7ukZEb4pEgmuNeJD4U9Nu/1L/ztLzmg=='}}] additional_kwargs={} response_metadata={'finish_reason': 'STOP', 'model_name': 'gemini-2.5-flash', 'safety_ratings': [], 'model_provider': 'google_genai'} id='lc_run--019e4b94-909c-7542-bd64-0b95a9818dfe-0' tool_calls=[] invalid_tool_calls=[] usage_metadata={'input_tokens': 330, 'output_tokens': 151, 'total_tokens': 481, 'input_token_details': {'cache_read': 0}, 'output_token_details': {'reasoning': 86}}"
    if isinstance(last_message, AIMessage):
        final_response = last_message.text
    return render_template('index.html', response=final_response, query=user_ask)

if __name__ == '__main__':
    app.run(debug=True)