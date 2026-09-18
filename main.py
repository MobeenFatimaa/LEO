import os
import json

import speech_recognition as sr
import pyttsx3

from dotenv import load_dotenv
from google import genai

from tools.basic_tools import (
    open_website,
    get_time,
    calculate
)


# ============================================================
# CONFIGURATION
# ============================================================

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError(
        "GEMINI_API_KEY was not found in your .env file."
    )


# ============================================================
# GEMINI CLIENT
# ============================================================

client = genai.Client(
    api_key=GEMINI_API_KEY
)


# ============================================================
# LEO PERSONALITY
# ============================================================

SYSTEM_INSTRUCTION = """
You are LEO, a personal AI voice assistant.

Your name is LEO.

You are helpful, concise, friendly, and natural.

Your responses will be spoken aloud, so avoid:
- Long explanations
- Excessive formatting
- Markdown
- Unnecessary lists

You have access to tools.

Use Google Search when the user asks for:
- Current information
- Latest news
- Recent events
- Current prices
- Recent technology developments
- Information that may have changed recently
- Real-time or up-to-date facts

Use custom tools when appropriate.

If a tool can perform an action, perform the action instead
of simply explaining how the user could do it.

When the user asks a normal general knowledge question,
answer naturally.

Never claim that you performed an action if the tool was not
actually executed.
"""


# ============================================================
# TEXT TO SPEECH
# ============================================================

engine = pyttsx3.init()


def speak(text):

    if not text:
        return

    print("LEO:", text)

    engine.say(text)

    engine.runAndWait()


# ============================================================
# SPEECH RECOGNITION
# ============================================================

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

        print(
            "Speech recognition service unavailable."
        )

        speak(
            "I'm having trouble connecting "
            "to the speech recognition service."
        )

        return ""


# ============================================================
# WAKE WORD DETECTION
# ============================================================

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


# ============================================================
# CUSTOM TOOL DEFINITIONS
# ============================================================

open_website_tool = {
    "type": "function",
    "name": "open_website",
    "description": (
        "Open a supported website in the user's "
        "default web browser."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "website": {
                "type": "string",
                "description": (
                    "Website name. Supported websites are "
                    "google, youtube, linkedin, facebook, "
                    "and github."
                )
            }
        },
        "required": ["website"]
    }
}


get_time_tool = {
    "type": "function",
    "name": "get_time",
    "description": (
        "Get the current local time."
    ),
    "parameters": {
        "type": "object",
        "properties": {},
        "required": []
    }
}


calculate_tool = {
    "type": "function",
    "name": "calculate",
    "description": (
        "Calculate a basic mathematical expression."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "expression": {
                "type": "string",
                "description": (
                    "A mathematical expression such as "
                    "25 * 4 or 100 / 5."
                )
            }
        },
        "required": ["expression"]
    }
}


# ============================================================
# ALL LEO TOOLS
# ============================================================

tools = [
    {
        "type": "google_search"
    },

    open_website_tool,

    get_time_tool,

    calculate_tool
]


# ============================================================
# TOOL EXECUTION
# ============================================================

def execute_tool(name, arguments):

    print(
        f"\n[TOOL] {name}"
    )

    print(
        f"[ARGS] {arguments}"
    )


    if name == "open_website":

        return open_website(
            arguments["website"]
        )


    elif name == "get_time":

        return get_time()


    elif name == "calculate":

        return calculate(
            arguments["expression"]
        )


    return "Unknown tool."


# ============================================================
# GEMINI AGENT
# ============================================================

def ask_ai(command, previous_interaction_id=None):

    interaction = client.interactions.create(

        model="gemini-3.8-flash",

        input=command,

        previous_interaction_id=previous_interaction_id,

        system_instruction=SYSTEM_INSTRUCTION,

        tools=tools
    )


    while True:

        function_calls = []


        for step in interaction.steps:

            if step.type == "function_call":

                function_calls.append(step)


        if not function_calls:

            return (
                interaction.output_text,
                interaction.id
            )


        function_results = []


        for step in function_calls:

            try:

                arguments = step.arguments

                if isinstance(arguments, str):

                    arguments = json.loads(
                        arguments
                    )


                result = execute_tool(
                    step.name,
                    arguments
                )


                function_results.append({

                    "type": "function_result",

                    "name": step.name,

                    "call_id": step.id,

                    "result": [
                        {
                            "type": "text",
                            "text": json.dumps(
                                {
                                    "result": result
                                }
                            )
                        }
                    ]

                })


            except Exception as e:

                print(
                    "[TOOL ERROR]",
                    e
                )


                function_results.append({

                    "type": "function_result",

                    "name": step.name,

                    "call_id": step.id,

                    "result": [
                        {
                            "type": "text",
                            "text": json.dumps(
                                {
                                    "error": str(e)
                                }
                            )
                        }
                    ]

                })


        interaction = client.interactions.create(

            model="gemini-3.8-flash",

            previous_interaction_id=interaction.id,

            system_instruction=SYSTEM_INSTRUCTION,

            tools=tools,

            input=function_results
        )


# ============================================================
# MAIN PROGRAM
# ============================================================

def main():

    speak(
        "Hello. I am Leo. "
        "I am ready."
    )


    previous_interaction_id = None


    while True:

        # ----------------------------------------------------
        # WAIT FOR "LEO"
        # ----------------------------------------------------

        command = wait_for_wake_word()


        # ----------------------------------------------------
        # IF USER ONLY SAID "LEO"
        # ----------------------------------------------------

        if not command:

            command = listen()


        if not command:

            continue


        # ----------------------------------------------------
        # EXIT
        # ----------------------------------------------------

        if (
            "exit" in command
            or "quit" in command
            or "goodbye" in command
            or "shut down" in command
        ):

            speak(
                "Goodbye. See you later."
            )

            break


        # ----------------------------------------------------
        # SEND TO GEMINI
        # ----------------------------------------------------

        try:

            answer, previous_interaction_id = ask_ai(
                command,
                previous_interaction_id
            )


            if answer:

                speak(answer)

            else:

                speak(
                    "I couldn't generate a response."
                )


        except Exception as e:

            print(
                "\n[ERROR]",
                repr(e)
            )

            speak(
                "Sorry, something went wrong."
            )


# ============================================================
# START LEO
# ============================================================

if __name__ == "__main__":

    main()
