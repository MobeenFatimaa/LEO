import os

import speech_recognition as sr
import pyttsx3

from dotenv import load_dotenv
from google import genai
from google.genai import types

from tools.basic_tools import (
    open_website,
    get_time,
    calculate
)


# ==========================================
# CONFIGURATION
# ==========================================

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError(
        "GEMINI_API_KEY was not found in the .env file."
    )

client = genai.Client(
    api_key=GEMINI_API_KEY
)


# ==========================================
# TEXT TO SPEECH
# ==========================================

engine = pyttsx3.init()


def speak(text):
    print("LEO:", text)

    engine.say(text)
    engine.runAndWait()


# ==========================================
# SPEECH RECOGNITION
# ==========================================

def listen():

    recognizer = sr.Recognizer()

    with sr.Microphone() as source:

        print("\nListening...")

        recognizer.adjust_for_ambient_noise(
            source,
            duration=1
        )

        try:

            audio = recognizer.listen(
                source,
                timeout=5,
                phrase_time_limit=10
            )

        except sr.WaitTimeoutError:

            print("No speech detected.")

            return ""

    try:

        text = recognizer.recognize_google(audio)

        print("You:", text)

        return text.lower()

    except sr.UnknownValueError:

        print("LEO couldn't understand you.")

        return ""

    except sr.RequestError:

        speak(
            "I'm having trouble connecting "
            "to the speech recognition service."
        )

        return ""


# ==========================================
# WAKE WORD
# ==========================================

def wait_for_wake_word():

    while True:

        command = listen()

        if not command:
            continue

        if "leo" in command:

            command = command.replace(
                "leo",
                "",
                1
            ).strip()

            if command:
                return command

            speak("Yes?")

            return ""


# ==========================================
# GEMINI AI BRAIN
# ==========================================

def ask_ai(command):

    response = client.models.generate_content(

        model="gemini-3.7-flash",

        contents=command,

        config=types.GenerateContentConfig(

            system_instruction=(
                "You are LEO, a helpful personal AI voice assistant. "
                "You communicate naturally and concisely because "
                "your responses will be spoken aloud. "
                "Use available tools whenever they are appropriate. "
                "Do not explain how to perform an action when you "
                "can perform it using a tool."
            ),

            tools=[
                open_website,
                get_time,
                calculate
            ]
        )
    )

    return response.text


# ==========================================
# MAIN PROGRAM
# ==========================================

speak(
    "Hello. I am Leo. "
    "I am ready."
)


while True:

    command = wait_for_wake_word()

    if not command:

        command = listen()

    if not command:

        continue


    # Exit command

    if (
        "exit" in command
        or "quit" in command
        or "goodbye" in command
    ):

        speak(
            "Goodbye. See you later."
        )

        break


    # Send command to Gemini

    try:

        answer = ask_ai(command)

        speak(answer)

    except Exception as e:

        print("ERROR:", e)

        speak(
            "Sorry, I encountered a problem."
        )
