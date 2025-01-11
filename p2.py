from transformers import GPT2LMHeadModel, GPT2Tokenizer
import pyttsx3
import speech_recognition as sr
import requests
from bs4 import BeautifulSoup

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

# Load pre-trained GPT-2 model and tokenizer
tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
model = GPT2LMHeadModel.from_pretrained("gpt2")
tokenizer.pad_token = tokenizer.eos_token

def generate_text(prompt):
    """Generate a response using Hugging Face GPT-2 model."""
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, padding=True)
    
    # Generate the attention mask manually
    attention_mask = inputs['attention_mask']

    # Generate output with attention mask explicitly set and avoid repetition
    output = model.generate(inputs["input_ids"], max_length=100, 
                            pad_token_id=tokenizer.eos_token_id, 
                            attention_mask=attention_mask, 
                            num_return_sequences=1, 
                            no_repeat_ngram_size=2)
    
    return tokenizer.decode(output[0], skip_special_tokens=True)

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
        elif "search" in query:
            search_term = query.replace("search", "").strip()
            result = search_web(search_term)
            print(f"Result: {result}")
            speak(result)
        else:
            response = generate_text(query)
            print(f"JARVIS: {response}")
            speak(response)

if __name__ == "__main__":
    main()
