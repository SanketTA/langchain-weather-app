from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from langchain.agents import create_agent
import requests
load_dotenv()

def get_weather(city:str):
    """Get the weather details for the provided city"""
    return {'temperature':'35','weather':'sunny'}

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
agent = create_agent(
    model = llm,
    tools=[get_weather,get_location],
    system_prompt=system_prompt,
)
# user_ask = input('User: ')
# response = agent.invoke(
#     {"messages":[{'role':'user','content':user_ask}]}
# )
# print('Jarvis: ' + str(response["messages"][-1].content))

print(get_weather())