import os
import time
import speech_recognition as sr
import pyttsx3
import numpy as np
import torch
from transformers import GPT2LMHeadModel, GPT2Tokenizer
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize the GPT-2 model and tokenizer
model_name = 'gpt2'
tokenizer = GPT2Tokenizer.from_pretrained(model_name)
model = GPT2LMHeadModel.from_pretrained(model_name)

def generate_response(prompt):
    """Generate a response using GPT-2 with proper handling for text generation."""
    inputs = tokenizer.encode(prompt, return_tensors='pt')
    
    # Create an attention mask
    attention_mask = torch.ones(inputs.shape, dtype=torch.long)

    try:
        outputs = model.generate(
            inputs,            
            max_length=300,
            num_return_sequences=1,
            pad_token_id=tokenizer.eos_token_id,
            attention_mask=attention_mask
        )
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        return response.strip()
    except Exception as e:
        print(f"An error occurred: {e}")
        return "Sorry, there was an error processing your request."

# Initialize TTS engine
engine = pyttsx3.init()
voice = engine.getProperty('voices')[1]  # Select a voice
engine.setProperty('voice', voice.id)

# Define name and greetings
greetings = [
    "What's up user?",
]

def listen_for_wake_word(source):
    print("Listening for 'Baymax'...")
    while True:
        audio = r.listen(source)
        try:
            text = r.recognize_google(audio)
            if "baymax" in text.lower():
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

            # Generate a response using GPT-2
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