import os
import time
import speech_recognition as sr
import pyttsx3
import numpy as np
from dotenv import load_dotenv
from openai import OpenAI
from openai import RateLimitError, OpenAIError

# Load environment variables
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Initialize TTS engine
engine = pyttsx3.init()
voice = engine.getProperty('voices')[1]  # Select a voice
engine.setProperty('voice', voice.id)

# Define name and greetings
greetings = [
    "What's up user?",
]

def generate_response(prompt):
    """Generate a response from OpenAI's API with rate limit handling."""
    retry_attempts = 5
    for attempt in range(retry_attempts):
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500
            )
            return response['choices'][0]['message']['content'].strip()
        except RateLimitError:
            wait_time = 2 ** attempt  # Exponential backoff
            print(f"Rate limit exceeded. Waiting for {wait_time} seconds before retrying...")
            time.sleep(wait_time)
        except OpenAIError as e:
            print(f"An error occurred: {e}")
            return "Sorry, there was an error processing your request."
    return "Sorry, unable to generate a response at the moment."

def listen_for_wake_word(source):
    print("Listening for 'Hello'...")
    while True:
        audio = r.listen(source)
        try:
            text = r.recognize_google(audio)
            if "hello" in text.lower():
                print("Wake word detected.")
                engine.say(np.random.choice(greetings))
                engine.runAndWait()
                listen_and_respond(source)
                break
        except sr.UnknownValueError:
            pass
        except sr.RequestError as e:
            print(f"Error recognizing speech: {e}")
            time.sleep(2)

def listen_and_respond(source):
    print("Listening...")
    while True:
        audio = r.listen(source)
        try:
            text = r.recognize_google(audio)
            print(f"You said: {text}")
            if not text:
                continue

            # Generate a response using OpenAI
            response_text = generate_response(text)
            print(f"AI Response: {response_text}")

            # Speak the response
            engine.say(response_text)
            engine.runAndWait()

        except sr.UnknownValueError:
            print("Silence detected, listening for wake word...")
            listen_for_wake_word(source)
            break
        except sr.RequestError as e:
            print(f"Could not request results; {e}")
            engine.say(f"Could not request results; {e}")
            engine.runAndWait()
            listen_for_wake_word(source)
            break

# Initialize recognizer and microphone
r = sr.Recognizer()
with sr.Microphone() as source:
    listen_for_wake_word(source)
