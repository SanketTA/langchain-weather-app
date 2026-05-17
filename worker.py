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
    location_response = requests.get("https://ipapi.co/json/",headers={'User-agent':'your-bot 0.1'})
    data = location_response.json()
    return {'city':data['city'],'contry':data['country_name'],'latitude':data['latitude'],'longitude':data['longitude']}

llm = ChatGoogleGenerativeAI(
    model = 'gemini-2.5-flash',
    temperature = 0.7,
)

system_prompt = """
YOU ARE THE HELPFULL WEATHER ASSISTANT.
YOUR WORKFLOW:
1. If user did not provided for which city they want to investigate the weather details call get_location()
and get the location details and pass them to get_weather(city) and get weather details from it.
2. If user have provided the location details directly call get_weather for that location and sed it to user.
3. Remember you are going to sound like Jarvis in the movie IRONMAN in marvel cinematic universe.
"""

with SqliteSaver.from_conn_string('weather.db') as checkpointer:
    agent = create_agent(
    model = llm,
    tools=[get_weather,get_location], 
    system_prompt=system_prompt,
    checkpointer=checkpointer
    )
    while True:
        user_ask = input('User: ')
        if user_ask in ['bye','break','stop']:
            break
        response = agent.invoke(
            {"messages":[{'role':'user','content':user_ask}]},
            {'configurable':{"thread_id":str(uuid.uuid4())}}
        )
        last_message = response['messages'][-1]
        if isinstance(last_message, AIMessage):
            final_response = last_message.text
        print(f"Jarvis: {final_response}")
