import os
import json

import speech_recognition as sr
import pyttsx3

from dotenv import load_dotenv
from google import genai

from tools.basic_tools import (
    open_website,
    open_application,
    open_vscode,
    open_folder,
    get_time,
    get_date,
    calculate,
    get_weather
)

from memory import (
    remember_fact,
    forget_fact,
    get_memory
)


# ============================================================
# CONFIGURATION
# ============================================================

load_dotenv()

GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY"
)

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

IMPORTANT TOOL RULES:

1. Use Google Search when the user asks for:
- Current information
- Latest news
- Recent events
- Current prices
- Recent technology developments
- Information that may have changed recently
- Up-to-date facts

2. Use the weather tool when the user asks about:
- Weather
- Temperature
- Rain
- Humidity
- Wind
- Current conditions
for a location.

3. Use the date tool when the user asks:
- What is today's date?
- What day is it?
- Today's date

4. Use the time tool when the user asks:
- What time is it?
- Current time

5. Use the website tool when the user asks you to:
- Open Google
- Open YouTube
- Open GitHub
- Open LinkedIn
- Open Gmail
- Open Kaggle
- Open ChatGPT
- Open Gemini
or another supported website.

6. Use the application tool when the user asks you to:
- Open Chrome
- Open Notepad
- Open Calculator
- Open Paint
- Open Command Prompt
- Open PowerShell
- Open File Explorer
- Open Task Manager

7. Use the VS Code tool when the user asks:
- Open VS Code
- Open Visual Studio Code

8. Use the folder tool when the user asks:
- Open Desktop
- Open Downloads
- Open Documents
- Open Pictures
- Open Videos
- Open Music

9. Use the calculator tool for mathematical calculations.

10. Use memory tools when the user explicitly asks you to:
- Remember something
- Forget something
- Tell them something stored in memory

If a tool can perform an action, perform the action instead
of simply explaining how the user could do it.

Never claim that you performed an action if the tool was not
actually executed.

If a tool returns an error, explain the error briefly.

You are a voice assistant, so keep answers reasonably short.
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

        text = recognizer.recognize_google(
            audio
        )

        print("You:", text)

        return text.lower()

    except sr.UnknownValueError:

        print(
            "LEO couldn't understand you."
        )

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
# WAKE WORD
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
# TOOL DEFINITIONS
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
                    "Website name. Supported websites include "
                    "google, youtube, linkedin, facebook, "
                    "github, gmail, kaggle, chatgpt, and gemini."
                )
            }
        },
        "required": [
            "website"
        ]
    }
}


open_application_tool = {
    "type": "function",
    "name": "open_application",
    "description": (
        "Open a supported Windows application."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "application": {
                "type": "string",
                "description": (
                    "Application name such as Chrome, "
                    "Notepad, Calculator, Paint, "
                    "Command Prompt, PowerShell, "
                    "File Explorer, or Task Manager."
                )
            }
        },
        "required": [
            "application"
        ]
    }
}


open_vscode_tool = {
    "type": "function",
    "name": "open_vscode",
    "description": (
        "Open Visual Studio Code on the Windows computer."
    ),
    "parameters": {
        "type": "object",
        "properties": {},
        "required": []
    }
}


open_folder_tool = {
    "type": "function",
    "name": "open_folder",
    "description": (
        "Open a common Windows folder."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "folder": {
                "type": "string",
                "description": (
                    "Folder name such as Desktop, Documents, "
                    "Downloads, Pictures, Videos, or Music."
                )
            }
        },
        "required": [
            "folder"
        ]
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


get_date_tool = {
    "type": "function",
    "name": "get_date",
    "description": (
        "Get today's date."
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
                    "Mathematical expression such as "
                    "25 * 4 or 100 / 5."
                )
            }
        },
        "required": [
            "expression"
        ]
    }
}


weather_tool = {
    "type": "function",
    "name": "get_weather",
    "description": (
        "Get current weather information for a city "
        "or location."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "location": {
                "type": "string",
                "description": (
                    "City or location name such as "
                    "Rawalpindi, Islamabad, Lahore, "
                    "Karachi, or London."
                )
            }
        },
        "required": [
            "location"
        ]
    }
}


remember_fact_tool = {
    "type": "function",
    "name": "remember_fact",
    "description": (
        "Save an important personal fact or preference "
        "that the user explicitly asks LEO to remember."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "key": {
                "type": "string",
                "description": (
                    "Category of information."
                )
            },
            "value": {
                "type": "string",
                "description": (
                    "Information that should be remembered."
                )
            }
        },
        "required": [
            "key",
            "value"
        ]
    }
}


forget_fact_tool = {
    "type": "function",
    "name": "forget_fact",
    "description": (
        "Delete a previously saved personal fact "
        "when the user asks LEO to forget it."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "key": {
                "type": "string",
                "description": (
                    "Category of information to forget."
                )
            }
        },
        "required": [
            "key"
        ]
    }
}


get_memory_tool = {
    "type": "function",
    "name": "get_memory",
    "description": (
        "Retrieve a personal fact previously saved "
        "in LEO's persistent memory."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "key": {
                "type": "string",
                "description": (
                    "Category of memory to retrieve."
                )
            }
        },
        "required": [
            "key"
        ]
    }
}


# ============================================================
# ALL TOOLS
# ============================================================

tools = [

    {
        "type": "google_search"
    },

    open_website_tool,

    open_application_tool,

    open_vscode_tool,

    open_folder_tool,

    get_time_tool,

    get_date_tool,

    calculate_tool,

    weather_tool,

    remember_fact_tool,

    forget_fact_tool,

    get_memory_tool
]


# ============================================================
# TOOL EXECUTION
# ============================================================

def execute_tool(name, arguments):

    print(f"\n[TOOL] {name}")
    print(f"[ARGS] {arguments}")

    if name == "open_website":

        return open_website(
            arguments["website"]
        )

    elif name == "open_application":

        return open_application(
            arguments["application"]
        )

    elif name == "open_vscode":

        return open_vscode()

    elif name == "open_folder":

        return open_folder(
            arguments["folder"]
        )

    elif name == "get_time":

        return get_time()

    elif name == "get_date":

        return get_date()

    elif name == "calculate":

        return calculate(
            arguments["expression"]
        )

    elif name == "get_weather":

        return get_weather(
            arguments["location"]
        )

    elif name == "remember_fact":

        return remember_fact(
            arguments["key"],
            arguments["value"]
        )

    elif name == "forget_fact":

        return forget_fact(
            arguments["key"]
        )

    elif name == "get_memory":

        return get_memory(
            arguments["key"]
        )

    return "Unknown tool."


# ============================================================
# GEMINI REQUEST
# ============================================================

def ask_ai(
    command,
    previous_interaction_id=None
):

    interaction = client.interactions.create(

        model="gemini-3.8-flash",

        input=command,

        previous_interaction_id=(
            previous_interaction_id
        ),

        system_instruction=(
            SYSTEM_INSTRUCTION
        ),

        tools=tools
    )


    # --------------------------------------------------------
    # TOOL EXECUTION LOOP
    # --------------------------------------------------------

    while True:

        function_calls = []

        for step in interaction.steps:

            if step.type == "function_call":

                function_calls.append(step)


        # ----------------------------------------------------
        # NO TOOL CALL
        # ----------------------------------------------------

        if not function_calls:

            return (
                interaction.output_text,
                interaction.id
            )


        # ----------------------------------------------------
        # EXECUTE TOOLS
        # ----------------------------------------------------

        function_results = []


        for step in function_calls:

            try:

                arguments = step.arguments

                if isinstance(
                    arguments,
                    str
                ):

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


        # ----------------------------------------------------
        # SEND TOOL RESULTS BACK TO GEMINI
        # ----------------------------------------------------

        interaction = client.interactions.create(

            model="gemini-3.8-flash",

            previous_interaction_id=(
                interaction.id
            ),

            system_instruction=(
                SYSTEM_INSTRUCTION
            ),

            tools=tools,

            input=function_results
        )


# ============================================================
# MAIN LOOP
# ============================================================

def main():

    speak(
        "Hello. I am Leo. "
        "I am ready."
    )


    previous_interaction_id = None


    while True:

        command = wait_for_wake_word()


        if not command:

            command = listen()


        if not command:

            continue


        # ----------------------------------------------------
        # EXIT COMMANDS
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
        # ASK GEMINI
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
