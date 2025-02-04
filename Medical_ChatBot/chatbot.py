import streamlit as st
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os
import pyttsx3
import speech_recognition as sr

# Streamlit page setup
st.set_page_config(page_title="ChatBot")
st.header("Speech-Enabled ChatBot")

# Load environment variables
load_dotenv()

# Initialize ChatOpenAI
chat = ChatOpenAI(temperature=0.5)

# Initialize session state for conversation
if 'flowmessages' not in st.session_state:
    st.session_state['flowmessages'] = [
        SystemMessage(content="You are a helpful medical AI assistant")
    ]

# Initialize text-to-speech engine
engine = pyttsx3.init()

def say_text(text):
    """Convert text to speech."""
    engine.say(text)
    engine.runAndWait()

# Function to handle user input and bot response
def get_chatmodel_response(question):
    st.session_state['flowmessages'].append(HumanMessage(content=question))
    answer = chat(st.session_state['flowmessages'])
    st.session_state['flowmessages'].append(AIMessage(content=answer.content))
    return answer.content

# Function to capture speech input
def capture_speech():
    """Capture speech from microphone and convert it to text."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("Listening... Please speak now.")
        try:
            # Adjust for ambient noise and record audio
            recognizer.adjust_for_ambient_noise(source)
            audio_data = recognizer.listen(source, timeout=5)
            # Recognize speech using Google Web Speech API
            text = recognizer.recognize_google(audio_data)
            return text
        except sr.UnknownValueError:
            return "Sorry, I couldn't understand that."
        except sr.RequestError as e:
            return f"Speech Recognition error: {e}"

# Button for capturing speech
if st.button("Talk to the Bot"):
    user_input = capture_speech()
    st.write(f"**You said:** {user_input}")
    
    if user_input:
        # Get bot response
        response = get_chatmodel_response(user_input)
        st.subheader("Bot Response:")
        st.write(response)
        
        # Convert bot response to speech
        say_text(response)
