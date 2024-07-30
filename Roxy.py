import speech_recognition as sr
import pyttsx3
import google.generativeai as gen_ai
import re

# Replace with your actual API key
API_KEY = "AIzaSyDcrRJR6kpQ44S0dMkjGKQ6FtGCoBSxjLs"

def init_speech():
    recognizer = sr.Recognizer()
    engine = pyttsx3.init()
    # Change the voice to a different one, if available
    voices = engine.getProperty('voices')
    for voice in voices:
        if 'Zira' in voice.name:  # Example of a clear, robotic-sounding voice
            engine.setProperty('voice', voice.id)
            break
    engine.setProperty('rate', 150)  # Adjust speech rate for smoother flow
    return recognizer, engine

def recognize_speech(recognizer, timeout=None):
    with sr.Microphone() as source:
        if timeout:
            print(f"You have {timeout} seconds to speak.")
        audio = recognizer.listen(source, timeout=timeout)
        try:
            text = recognizer.recognize_google(audio)
            return text
        except sr.UnknownValueError:
            return None
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")
            return None

def generate_response(history):
    gen_ai.configure(api_key=API_KEY)
    model = gen_ai.GenerativeModel("gemini-1.5-flash")  # or use a specific Gemini model like "gemini-1.5-flash"
    conversation = "\n".join(history)
    response = model.generate_content(f"Respond as a friendly chat assistant named Roxy:\n{conversation}")
    return response.text

def clean_text(text):
    # Remove characters '#' and '*', and any potential emojis
    text = text.replace("#", "").replace("*", "")
    text = re.sub(r'[^\x00-\x7F]+', '', text)  # Remove emojis and non-ASCII characters
    return text

def speak(engine, text):
    engine.say(text)
    engine.runAndWait()

def main():
    recognizer, engine = init_speech()
    history = []

    while True:
        print("Say 'Hello Roxy' to wake me up.")
        wake_word = recognize_speech(recognizer)
        if wake_word and "hello roxy" in wake_word.lower():
            greeting = "Hi there! How can I assist you today?"
            print(greeting)
            speak(engine, greeting)
            while True:
                user_input = recognize_speech(recognizer, timeout=10)
                if user_input:
                    cleaned_input = clean_text(user_input)
                    history.append(f"User: {cleaned_input}")
                    response = generate_response(history)
                    cleaned_response = clean_text(response)
                    history.append(f"Roxy: {cleaned_response}")
                    print(f"Roxy: {cleaned_response}")
                    speak(engine, cleaned_response)
                    if "goodbye roxy" in cleaned_input.lower():
                        print("Goodbye! Have a great day!")
                        speak(engine, "Goodbye! Have a great day!")
                        break
                else:
                    print("No input received. Going back to sleep mode.")
                    break

if __name__ == "__main__":
    main()