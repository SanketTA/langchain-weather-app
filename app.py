from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from worker import agent
from langchain_core.messages import AIMessage
import uuid

app = Flask(__name__)
app.secret_key = 'Sanket@1234'

@app.route('/')
def home():
    if 'message' not in session:
        session['message'] = []
    return render_template('index.html',messages = session['message'])

@app.route('/get_weather', methods=['POST'])
def get_weather():
    user_ask = request.form.get('query')
    latitude = request.form.get('latitude')
    longitude = request.form.get('longitude')
    if latitude and longitude:
        session['user_location'] = {'lat': latitude, 'lon': longitude}
    if not user_ask:
        return jsonify({"error": "Please provide a query in the request body."}), 400
    response = agent.invoke(
        {"messages":[{'role':'user','content':user_ask}]},
        {'configurable':{"thread_id":str(uuid.uuid4())}}
    )
    last_message = response['messages'][-1]
    if isinstance(last_message, AIMessage):
        content = last_message.content
        if isinstance(content, list):
            final_response = " ".join(
                block.get('text', '') for block in content if isinstance(block, dict)
            )
        else:
            final_response = content
    session['message'].append({'type':'human','content':user_ask})
    session['message'].append({'type':'ai','content':final_response})
    session.modified = True
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
