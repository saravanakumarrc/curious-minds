import speech_recognition as sr
from gtts import gTTS
import pygame
import io
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage, HumanMessage
import re

# Initialize speech engine
recognizer = sr.Recognizer()

# Initialize pygame mixer for audio playback
pygame.mixer.init()

# Initialize LangChain with Ollama
model = OllamaLLM(model="gemma4")

# Master prompt
SYSTEM_PROMPT = """You are a helpful, friendly AI assistant having a real-time voice conversation.
Keep your responses concise and natural for spoken audio (typically 1-3 sentences).
Be warm, engaging, and directly answer the user's questions.
Avoid lengthy explanations unless specifically asked.
Do not include thinking processes, reasoning, or markdown formatting in your response.
Just give a direct, conversational answer."""

# Create the prompt template
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM_PROMPT),
        ("placeholder", "{chat_history}"),
        ("human", "{input}"),
    ]
)

# Create conversation chain
chain = prompt | model

# Chat history storage - manually managed list
chat_history = []


def speak(text):
    """Convert text to speech using gTTS and play it"""
    text = text.strip()
    if not text:
        return
    
    # Clean up markdown/special characters
    text = re.sub(r'\*+', '', text)
    text = text.replace("**", "").replace("__", "").replace("  ", " ")
    
    print(f"🤖 Assistant: {text}\n")
    
    try:
        # Create gTTS object
        tts = gTTS(text=text, lang='en', slow=False)
        
        # Play audio using pygame
        audio_fp = io.BytesIO()
        tts.write_to_fp(audio_fp)
        audio_fp.seek(0)
        
        # Load and play with pygame
        pygame.mixer.music.load(audio_fp)
        pygame.mixer.music.play()
        
        # Wait for audio to finish
        while pygame.mixer.music.get_busy():
            pass
            
    except Exception as e:
        print(f"❌ Error in text-to-speech: {e}")


def listen():
    """Listen for user speech and convert to text"""
    try:
        with sr.Microphone() as source:
            print("🎤 Listening...")
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=10)

        text = recognizer.recognize_google(audio)
        print(f"👤 You: {text}\n")
        return text
    except sr.UnknownValueError:
        print("❌ Could not understand audio, try again\n")
        return ""
    except sr.RequestError as e:
        print(f"❌ Speech recognition service error: {e}\n")
        return ""
    except Exception as e:
        print(f"❌ Error: {e}\n")
        return ""


def chat(user_input):
    """Generate response using LangChain with conversation history"""
    try:
        # Add user message to history
        chat_history.append(HumanMessage(content=user_input))
        
        # Get response
        response = chain.invoke(
            {"input": user_input, "chat_history": chat_history}
        )
        
        # Add assistant response to history
        chat_history.append(AIMessage(content=response))
        
        return response
    except Exception as e:
        print(f"❌ Error generating response: {e}")
        return "Sorry, I encountered an error. Please try again."


def main():
    """Main voice chat loop"""
    print("\n" + "="*50)
    print("🎯 Voice Chat Assistant Started")
    print("="*50)
    print("Say 'exit' or 'quit' to end the conversation\n")
    
    speak("Hello! I'm your voice assistant. How can I help you today?")
    
    while True:
        # Listen for user input
        user_input = listen()
        
        if not user_input:
            continue
        
        # Check for exit commands
        if any(word in user_input.lower() for word in ["exit", "quit", "goodbye", "bye"]):
            speak("Goodbye! Thanks for chatting with me.")
            break
        
        # Get and speak response
        response = chat(user_input)
        speak(response)


if __name__ == "__main__":
    main()


if __name__ == "__main__":
    main()
