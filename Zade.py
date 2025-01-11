import pyttsx3
import speech_recognition as sr
import requests
from transformers import GPT2LMHeadModel, GPT2Tokenizer
import pyjokes
from googletrans import Translator
import datetime
import os
import webbrowser
from textblob import TextBlob
from bs4 import BeautifulSoup

# Initialize text-to-speech engine
engine = pyttsx3.init()
engine.setProperty('rate', 150)  # Speed of speech
engine.setProperty('volume', 0.9)  # Volume level

# Load GPT-2 model and tokenizer
tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
model = GPT2LMHeadModel.from_pretrained("gpt2")

# Set pad token to be the same as eos token to avoid issues
tokenizer.pad_token = tokenizer.eos_token

# Initialize Translator
translator = Translator()

# Function to speak text
def speak(text):
    """Convert text to speech."""
    engine.say(text)
    engine.runAndWait()

# Function to listen to voice input
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

# Function to process a query with GPT-2 model
def process_query(query):
    """Use GPT-2 model to process the query and generate a response."""
    try:
        print("Processing query...")

        # Encode input query
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

# Function to get weather information
def get_weather(city):
    """Fetch the weather for a given city."""
    api_key = "YOUR_API_KEY"
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

# Function to tell the current time
def tell_time():
    """Tell the current time."""
    now = datetime.datetime.now().strftime("%H:%M:%S")
    return f"The current time is {now}."

# Function to fetch a joke
def get_joke():
    """Fetch a joke."""
    return pyjokes.get_joke()

# Function to translate text
def translate_text(text, target_language='en'):
    """Translate text to a given language."""
    translation = translator.translate(text, dest=target_language)
    return translation.text

# Function to perform web search
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

# Function to open an application (e.g., Notepad, Calculator)
# Function to open an application (e.g., Notepad, Calculator)
def open_application(app_name):
    """Open an application based on the user's command."""
    if "notepad" in app_name:
        os.system("notepad")
        return "Opening Notepad."
    elif "calculator" in app_name:
        os.system("calc")
        return "Opening Calculator."
    else:
        return "Sorry, I cannot open that application."

# Function to open a website
def open_website(website):
    """Open a website based on the user's command."""
    webbrowser.open(website)
    return f"Opening {website}"


# Main function to run the assistant
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
        elif "time" in query:
            response = tell_time()
        elif "joke" in query:
            response = get_joke()
        elif "translate" in query:
            text = query.replace("translate", "").strip()
            response = translate_text(text)
        elif "search" in query:
            search_term = query.replace("search", "").strip()
            response = search_web(search_term)
        elif "open" in query:
            if "website" in query:
                website = query.replace("open website", "").strip()
                response = open_website(website)
            else:
                app_name = query.replace("open", "").strip()
                response = open_application(app_name)
        else:
            response = process_query(query)

        print(f"Assistant: {response}")
        speak(response)

if __name__ == "__main__":
    main()
