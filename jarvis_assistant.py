from transformers import GPT2LMHeadModel, GPT2Tokenizer
import pyttsx3
import speech_recognition as sr
import pywhatkit as kit
import requests
from bs4 import BeautifulSoup
import datetime
import os

# Initialize text-to-speech engine
engine = pyttsx3.init()
engine.setProperty('rate', 150)  # Speed of speech
engine.setProperty('volume', 0.9)  # Volume level

# Configure OpenAI API key
def speak(text):
    """Convert text to speech."""
    engine.say(text)
    engine.runAndWait()

def listen():
    """Listen to the user's voice and convert it to text."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        try:
            audio = recognizer.listen(source, timeout=7, phrase_time_limit=10)
            print("Recognizing...")
            query = recognizer.recognize_google(audio)
            print(f"You said: {query}")
            return query.lower()
        except sr.UnknownValueError:
            speak("Sorry, I could not understand. Please repeat.")
            return ""
        except sr.RequestError:
            speak("Service is down. Please try again later.")
            return ""
        except Exception as e:
            print(f"Error: {e}")
            return ""

from transformers import GPT2LMHeadModel, GPT2Tokenizer

# Load pre-trained GPT-2 model and tokenizer
tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
model = GPT2LMHeadModel.from_pretrained("gpt2")

# Set pad token to be the same as eos token to avoid issues
tokenizer.pad_token = tokenizer.eos_token

def process_query(query):
    """Use GPT-2 model to process the query and generate a response."""
    try:
        print("Processing query...")

        # Encode input query with attention mask
        inputs = tokenizer.encode(query, return_tensors="pt", padding=True, truncation=True, max_length=512)
        attention_mask = inputs != tokenizer.pad_token_id  # Create attention mask

        # Generate a response
        outputs = model.generate(inputs, attention_mask=attention_mask, max_length=100, num_return_sequences=1, no_repeat_ngram_size=2)

        # Decode and clean the response
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        return response
    except Exception as e:
        print(f"Error while processing the query: {e}")
        return "I'm sorry, I couldn't process your request."

def get_weather(city):
    """Fetch the weather for a given city."""
    api_key = "QQwa1nTNIPBYwZ3qDXbqQF8d4AnqT7jp"
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    try:
        response = requests.get(url)
        data = response.json()
        if data["cod"] != 200:
            return "Sorry, I couldn't fetch the weather."
        weather = data["weather"][0]["description"]
        temp = data["main"]["temp"]
        return f"The weather in {city} is currently {weather} with a temperature of {temp}°C."
    except Exception as e:
        print(f"Error fetching weather: {e}")
        return "Unable to fetch weather at the moment."

def search_web(query):
    """Perform a web search and return the top result."""
    url = f"https://www.google.com/search?q={query}"
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        result = soup.find("div", class_="BNeawe").text
        return result
    except Exception as e:
        print(f"Error performing web search: {e}")
        return "Sorry, I couldn't search the web right now."

def play_youtube_video(topic):
    """Play a YouTube video on the given topic."""
    speak(f"Playing {topic} on YouTube.")
    kit.playonyt(topic)

def tell_time():
    """Tell the current time."""
    now = datetime.datetime.now().strftime("%H:%M:%S")
    return f"The current time is {now}."

def open_application(app_name):
    """Open an application."""
    if "notepad" in app_name:
        os.system("notepad")
        return "Opening Notepad."
    elif "calculator" in app_name:
        os.system("calc")
        return "Opening Calculator."
    else:
        return "Sorry, I cannot open that application."

def main():
    """Main function to run the assistant."""
    speak("Hello! I am your assistant. How can I help you today?")
    while True:
        query = listen()
        if not query:
            continue
        if "exit" in query or "quit" in query:
            speak("Goodbye! Have a great day!")
            break
        elif "weather" in query:
            city = query.replace("weather in", "").strip()
            response = get_weather(city)
        elif "search for" in query:
            search_term = query.replace("search for", "").strip()
            response = search_web(search_term)
        elif "play" in query and "on youtube" in query:
            topic = query.replace("play", "").replace("on youtube", "").strip()
            play_youtube_video(topic)
            continue
        elif "time" in query:
            response = tell_time()
        elif "open" in query:
            app_name = query.replace("open", "").strip()
            response = open_application(app_name)
        else:
            response = process_query(query)

        print(f"JARVIS: {response}")
        speak(response)

if __name__ == "__main__":
    main()
