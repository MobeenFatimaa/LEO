import os
import json

import speech_recognition as sr
import pyttsx3

from dotenv import load_dotenv
from google import genai

from tools.basic_tools import (
    open_website,
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

Your responses will be spoken aloud.

Keep responses short and conversational.

Avoid:
- Markdown
- Long explanations
- Excessive lists
- Unnecessary formatting


============================================================
GOOGLE SEARCH
============================================================

You have access to Google Search.

Use Google Search when the user asks for:

- Latest news
- Current events
- Recent developments
- Current information
- Current prices
- Recent technology news
- Recent company information
- Information that may have changed recently

For example:

"Leo, what is the latest AI news?"

"Leo, what happened in technology today?"

"Leo, what are the latest developments in Gemini?"

Do not use search unnecessarily for simple general questions.


============================================================
WEATHER
============================================================

You have a weather tool.

Use the weather tool when the user asks about:

- Current weather
- Temperature
- Humidity
- Rain
- Wind
- Weather conditions
- How the weather feels

If the user specifies a city, use that city.

For example:

"What's the weather in Rawalpindi?"

"What's the temperature in London?"

"How is the weather in Dubai?"

Do not guess weather information.


============================================================
DATE AND TIME
============================================================

Use the time tool when the user asks for the current time.

Use the date tool when the user asks for today's date.


============================================================
WEBSITES
============================================================

Use the website tool when the user asks you to open:

- Google
- YouTube
- LinkedIn
- Facebook
- GitHub


============================================================
CALCULATOR
============================================================

Use the calculator when the user asks for mathematical
calculations.


============================================================
PERSISTENT MEMORY
============================================================

You have persistent local memory.

Only save information when the user explicitly asks you
to remember or save it.

When the user says:

"Remember that..."

use the remember_fact tool.

When the user asks you to forget something,
use the forget_fact tool.

When the user asks about information that may have been
saved previously, use the get_memory tool.

Never invent memories.

Never claim that something was saved unless the memory
tool actually executed successfully.


============================================================
GENERAL BEHAVIOR
============================================================

If a tool can perform an action, use the tool.

Never claim an action was completed if the tool was not
actually executed.

For normal questions that don't require a tool,
answer directly.

You are a voice assistant, so keep spoken responses natural
and reasonably short.
"""


# ============================================================
# TEXT TO SPEECH
# ============================================================

engine = pyttsx3.init()


def speak(text):

    if not text:
        return

    print(
        "LEO:",
        text
    )

    engine.say(text)

    engine.runAndWait()


# ============================================================
# SPEECH RECOGNITION
# ============================================================

def listen():

    recognizer = sr.Recognizer()

    with sr.Microphone() as source:

        print(
            "\nListening..."
        )

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

            print(
                "No speech detected."
            )

            return ""


    try:

        text = recognizer.recognize_google(
            audio
        )

        print(
            "You:",
            text
        )

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

            speak(
                "Yes?"
            )

            return ""


# ============================================================
# WEBSITE TOOL DEFINITION
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
                    "Website name. Supported websites "
                    "are google, youtube, linkedin, "
                    "facebook, and github."
                )
            }
        },

        "required": [
            "website"
        ]
    }
}


# ============================================================
# TIME TOOL DEFINITION
# ============================================================

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


# ============================================================
# DATE TOOL DEFINITION
# ============================================================

get_date_tool = {

    "type": "function",

    "name": "get_date",

    "description": (
        "Get the current local date."
    ),

    "parameters": {

        "type": "object",

        "properties": {},

        "required": []
    }
}


# ============================================================
# CALCULATOR TOOL DEFINITION
# ============================================================

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


# ============================================================
# WEATHER TOOL DEFINITION
# ============================================================

weather_tool = {

    "type": "function",

    "name": "get_weather",

    "description": (
        "Get the current weather for a specified city "
        "or location."
    ),

    "parameters": {

        "type": "object",

        "properties": {

            "location": {

                "type": "string",

                "description": (
                    "The city or location for which "
                    "the user wants current weather."
                )
            }
        },

        "required": [
            "location"
        ]
    }
}


# ============================================================
# MEMORY TOOL DEFINITIONS
# ============================================================

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
        "Delete a previously saved personal fact."
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
# ALL LEO TOOLS
# ============================================================

tools = [

    # Built-in Gemini Search
    {
        "type": "google_search"
    },

    # Browser
    open_website_tool,

    # Time
    get_time_tool,

    # Date
    get_date_tool,

    # Calculator
    calculate_tool,

    # Weather
    weather_tool,

    # Memory
    remember_fact_tool,

    forget_fact_tool,

    get_memory_tool
]


# ============================================================
# TOOL EXECUTION
# ============================================================

def execute_tool(
    name,
    arguments
):

    print(
        f"\n[TOOL] {name}"
    )

    print(
        f"[ARGS] {arguments}"
    )


    # --------------------------------------------------------
    # WEBSITE
    # --------------------------------------------------------

    if name == "open_website":

        return open_website(
            arguments["website"]
        )


    # --------------------------------------------------------
    # TIME
    # --------------------------------------------------------

    elif name == "get_time":

        return get_time()


    # --------------------------------------------------------
    # DATE
    # --------------------------------------------------------

    elif name == "get_date":

        return get_date()


    # --------------------------------------------------------
    # CALCULATOR
    # --------------------------------------------------------

    elif name == "calculate":

        return calculate(
            arguments["expression"]
        )


    # --------------------------------------------------------
    # WEATHER
    # --------------------------------------------------------

    elif name == "get_weather":

        return get_weather(
            arguments["location"]
        )


    # --------------------------------------------------------
    # REMEMBER
    # --------------------------------------------------------

    elif name == "remember_fact":

        return remember_fact(
            arguments["key"],
            arguments["value"]
        )


    # --------------------------------------------------------
    # FORGET
    # --------------------------------------------------------

    elif name == "forget_fact":

        return forget_fact(
            arguments["key"]
        )


    # --------------------------------------------------------
    # GET MEMORY
    # --------------------------------------------------------

    elif name == "get_memory":

        value = get_memory(
            arguments["key"]
        )

        if value is None:

            return (
                f"I don't have anything saved "
                f"about {arguments['key']}."
            )

        return (
            f"Your {arguments['key']} "
            f"is {value}."
        )


    return "Unknown tool."


# ============================================================
# GEMINI AGENT
# ============================================================

def ask_ai(
    command,
    previous_interaction_id=None
):

    # --------------------------------------------------------
    # CREATE INTERACTION
    # --------------------------------------------------------

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
    # TOOL LOOP
    # --------------------------------------------------------

    while True:

        function_calls = []


        for step in interaction.steps:

            if step.type == "function_call":

                function_calls.append(
                    step
                )


        # ----------------------------------------------------
        # NORMAL GEMINI RESPONSE
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


                print(
                    "[RESULT]",
                    result
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


            except Exception as error:

                print(
                    "[TOOL ERROR]",
                    repr(error)
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
                                    "error": str(error)
                                }
                            )
                        }

                    ]

                })


        # ----------------------------------------------------
        # SEND RESULTS BACK TO GEMINI
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
        # WAIT FOR WAKE WORD
        # ----------------------------------------------------

        command = wait_for_wake_word()


        # ----------------------------------------------------
        # USER ONLY SAID LEO
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
        # GEMINI
        # ----------------------------------------------------

        try:

            answer, previous_interaction_id = ask_ai(

                command,

                previous_interaction_id

            )


            if answer:

                speak(
                    answer
                )

            else:

                speak(
                    "I couldn't generate a response."
                )


        except Exception as error:

            print(
                "\n================================"
            )

            print(
                "LEO ERROR:"
            )

            print(
                repr(error)
            )

            print(
                "================================"
            )


            speak(
                "Sorry, something went wrong."
            )


# ============================================================
# START LEO
# ============================================================

if __name__ == "__main__":

    main()
