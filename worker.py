from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import AIMessage
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver # For saving chat in session only
from langgraph.checkpoint.sqlite import SqliteSaver
from dotenv import load_dotenv
import requests
import uuid
import os
load_dotenv()

def get_weather(city:str):
    """Get the weather details for the provided city"""
    API_KEY = os.getenv("OPENWEATHER_API_KEY")
    exclude = "minutely,hourly,alerts"
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid={API_KEY}"
    response = requests.get(url)
    data = response.json()
    return {
    "temperature": data["main"]["temp"],
    "feels_like": data["main"]["feels_like"],
    "weather": data["weather"][0]["description"],
    "humidity": data["main"]["humidity"],
    "wind_speed": data["wind"]["speed"]}

def get_location():
    """Get the location details of user i.e, city and contry so we can pass it to get_weather tool for weather details"""
    from flask import session
    if 'user_location' in session:
        lat = session['user_location']['lat']
        lon = session['user_location']['lon']
        API_KEY = os.getenv("OPENWEATHER_API_KEY")
        response = requests.get(
            f'http://api.openweathermap.org/geo/1.0/reverse?lat={lat}&lon={lon}&limit=1&appid={API_KEY}'
        )
        data = response.json()
        city = data[0]['name']
        country = data[0]['country']
        return f"{city}, {country}"
llm = ChatGoogleGenerativeAI(
    model = 'gemini-2.5-flash',
    temperature = 0.7,
)

system_prompt = """
You are an intelligent and helpful Weather Assistant with the speaking style of JARVIS from Iron Man — calm, professional, concise, and slightly sophisticated.
Your responsibilities and workflow:
1. Detect User Location
   - If the user does not specify a city or location, call `get_location()`.
   - Use the returned location data to call `get_weather(city)`.
2. Fetch Weather Information
   - If the user already provides a city or location, directly call `get_weather(location)`.
   - Present the weather details in a clear, natural, and user-friendly manner.
3. Conversational Style
   - Respond in a polished AI assistant tone similar to JARVIS.
   - Be intelligent, efficient, and slightly conversational without sounding robotic or overly dramatic.
4. Follow-up Questions
   - If the user asks follow-up questions unrelated to weather, answer them normally as a capable AI assistant.
   - Do not force the conversation back to weather unless the user asks about it.
5. Response Quality
   - Keep responses concise but informative.
   - Prioritize clarity, accuracy, and helpfulness.
   - Avoid unnecessary technical jargon unless the user requests detailed explanations.
"""
connection = SqliteSaver.from_conn_string('weather.db')
checkpointer = connection.__enter__()
agent = create_agent(
    model = llm,
    tools=[get_weather,get_location], 
    system_prompt=system_prompt,
    checkpointer=checkpointer
    )
# while True:
#     user_ask = input('User: ')
#     if user_ask in ['bye','break','stop']:
#         break
#     response = agent.invoke(
#         {"messages":[{'role':'user','content':user_ask}]},
#         {'configurable':{"thread_id":str(uuid.uuid4())}}
#     )
#     last_message = response['messages'][-1]
#     if isinstance(last_message, AIMessage):
#         final_response = last_message.text
#     print(f"Jarvis: {final_response}")
