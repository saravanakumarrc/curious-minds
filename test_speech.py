import speech_recognition as sr
import pyttsx3
import subprocess

# Init
recognizer = sr.Recognizer()
engine = pyttsx3.init()

import re

def speak(text):
    text = text.replace("\n", " ").strip()
    print(f"[DEBUG] Speaking: '{text}'")
    if text:
        try:
            engine.say(text)
            engine.runAndWait()
        except Exception as e:
            print(f"Error speaking: {e}")

def listen():
    with sr.Microphone() as source:
        print("🎤 Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        text = recognizer.recognize_google(audio)  # uses Google STT
        print("You:", text)
        return text
    except:
        return ""

def ask_gemma(prompt):
    process = subprocess.Popen(
        ["ollama", "run", "gemma4", prompt],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    output, error = process.communicate()  # Wait for process to complete
    
    # Remove thinking blocks - handle multiple patterns
    output = re.sub(r'(Thinking\.\.\..*?)(?=\n(?:I am|Hey|Hello|Sure|Yes|No|The|This|That|What|How|Why)|\Z)', '', output, flags=re.DOTALL | re.IGNORECASE)
    output = re.sub(r'Thinking Process:.*?\.\.\.done thinking\.\s*', '', output, flags=re.DOTALL)
    
    output = output.strip()
    print(f"[DEBUG] Response after filtering: '{output}'")
    return output

# Main loop
while True:
    user_input = listen()

    if user_input == "":
        continue

    if "exit" in user_input.lower():
        speak("Goodbye!")
        break

    response = ask_gemma(user_input)
    print("Gemma:", response)
    speak(response)
