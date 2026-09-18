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

from memory import (
    remember_fact,
    forget_fact,
    get_memory
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
# LEO PERSONALITY / SYSTEM INSTRUCTION
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

Keep normal responses short and conversational.

------------------------------------------------------------
WEB SEARCH
------------------------------------------------------------

You have access to Google Search.

Use Google Search when the user asks for:
- Current information
- Latest news
- Recent events
- Current prices
- Recent technology developments
- Recent people or company information
- Information that may have changed recently
- Real-time or up-to-date facts

Do not use search unnecessarily for simple general questions.

------------------------------------------------------------
CUSTOM TOOLS
------------------------------------------------------------

You have access to custom Python tools.

Use the appropriate tool when the user asks you to perform
an action that a tool can handle.

If a tool can perform an action, perform the action instead
of simply explaining how the user could do it.

Never claim that an action was performed unless the tool was
actually executed successfully.

------------------------------------------------------------
PERSISTENT MEMORY
------------------------------------------------------------

You have access to persistent local memory.

Only save information when the user explicitly asks you
to remember, save, or keep something for later.

Examples:

"Remember that my favorite language is Python."

"Leo, remember that my project is called LEO."

When the user explicitly asks you to remember something,
use the remember_fact tool.

When the user explicitly asks you to forget something,
use the forget_fact tool.

When the user asks about information that may have been
saved previously, use the get_memory tool.

Do not invent memories.

Do not claim to remember something unless it was actually
saved.

------------------------------------------------------------
GENERAL BEHAVIOR
------------------------------------------------------------

Answer normal questions naturally.

If the user asks something that does not require a tool,
answer directly.

You are a voice assistant, so prioritize short,
clear, natural spoken responses.
"""


# ============================================================
# TEXT TO SPEECH
# ============================================================

engine = pyttsx3.init()


def speak(text):
    """
    Convert text into spoken audio.
    """

    if not text:
        return

    print("LEO:", text)

    engine.say(text)

    engine.runAndWait()


# ============================================================
# SPEECH RECOGNITION
# ============================================================

def listen():
    """
    Listen through the microphone and convert speech to text.
    """

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
    """
    Wait until the user says 'Leo'.
    """

    while True:

        command = listen()

        if not command:
            continue

        if "leo" in command:

            # Remove only the first occurrence
            # of the wake word.
            command = command.replace(
                "leo",
                "",
                1
            ).strip()

            # Example:
            # "Leo open YouTube"
            #
            # becomes:
            # "open youtube"

            if command:

                return command

            # User only said:
            # "Leo"

            speak("Yes?")

            return ""


# ============================================================
# CUSTOM TOOL DEFINITIONS
# ============================================================

# ------------------------------------------------------------
# OPEN WEBSITE
# ------------------------------------------------------------

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
                    "The website to open. "
                    "Supported websites are "
                    "google, youtube, linkedin, "
                    "facebook, and github."
                )

            }

        },

        "required": [
            "website"
        ]
    }
}


# ------------------------------------------------------------
# GET TIME
# ------------------------------------------------------------

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


# ------------------------------------------------------------
# CALCULATE
# ------------------------------------------------------------

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
                    "25 * 4, 100 / 5, or 10 + 20."
                )

            }

        },

        "required": [
            "expression"
        ]
    }
}


# ------------------------------------------------------------
# REMEMBER FACT
# ------------------------------------------------------------

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
                    "The category of information, "
                    "such as favorite language, "
                    "favorite color, project name, "
                    "or preferred editor."
                )
            },

            "value": {

                "type": "string",

                "description": (
                    "The information that should be remembered."
                )
            }

        },

        "required": [
            "key",
            "value"
        ]
    }
}


# ------------------------------------------------------------
# FORGET FACT
# ------------------------------------------------------------

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
                    "The category of information to forget."
                )
            }

        },

        "required": [
            "key"
        ]
    }
}


# ------------------------------------------------------------
# GET MEMORY
# ------------------------------------------------------------

get_memory_tool = {

    "type": "function",

    "name": "get_memory",

    "description": (
        "Retrieve a personal fact previously saved "
        "in LEO's persistent local memory."
    ),

    "parameters": {

        "type": "object",

        "properties": {

            "key": {

                "type": "string",

                "description": (
                    "The category of memory to retrieve."
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

    # Built-in Gemini tool
    {
        "type": "google_search"
    },

    # Custom Python tools
    open_website_tool,

    get_time_tool,

    calculate_tool,

    # Persistent memory tools
    remember_fact_tool,

    forget_fact_tool,

    get_memory_tool
]


# ============================================================
# TOOL EXECUTION
# ============================================================

def execute_tool(name, arguments):
    """
    Execute the Python function requested by Gemini.
    """

    print(
        f"\n[TOOL] {name}"
    )

    print(
        f"[ARGS] {arguments}"
    )


    # --------------------------------------------------------
    # OPEN WEBSITE
    # --------------------------------------------------------

    if name == "open_website":

        return open_website(
            arguments["website"]
        )


    # --------------------------------------------------------
    # GET TIME
    # --------------------------------------------------------

    elif name == "get_time":

        return get_time()


    # --------------------------------------------------------
    # CALCULATE
    # --------------------------------------------------------

    elif name == "calculate":

        return calculate(
            arguments["expression"]
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


    # --------------------------------------------------------
    # UNKNOWN TOOL
    # --------------------------------------------------------

    return "Unknown tool."


# ============================================================
# GEMINI AGENT
# ============================================================

def ask_ai(
    command,
    previous_interaction_id=None
):
    """
    Send the user's command to Gemini.

    Gemini can:
    - Answer normally
    - Search the web
    - Call our Python tools
    - Use persistent memory
    """

    # --------------------------------------------------------
    # FIRST GEMINI REQUEST
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


        # Find all custom function calls
        # requested by Gemini.

        for step in interaction.steps:

            if step.type == "function_call":

                function_calls.append(step)


        # ----------------------------------------------------
        # NO CUSTOM FUNCTION CALL
        # ----------------------------------------------------

        if not function_calls:

            return (
                interaction.output_text,
                interaction.id
            )


        # ----------------------------------------------------
        # EXECUTE FUNCTION CALLS
        # ----------------------------------------------------

        function_results = []


        for step in function_calls:

            try:

                arguments = step.arguments


                # Sometimes arguments can arrive
                # as a JSON string.

                if isinstance(
                    arguments,
                    str
                ):

                    arguments = json.loads(
                        arguments
                    )


                # Execute the requested Python tool.

                result = execute_tool(
                    step.name,
                    arguments
                )


                print(
                    f"[RESULT] {result}"
                )


                # Prepare result for Gemini.

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
                    "\n[TOOL ERROR]",
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
# MAIN PROGRAM
# ============================================================

def main():

    # --------------------------------------------------------
    # STARTUP
    # --------------------------------------------------------

    speak(
        "Hello. I am Leo. "
        "I am ready."
    )


    # This keeps the current Gemini conversation alive.

    previous_interaction_id = None


    # --------------------------------------------------------
    # MAIN LOOP
    # --------------------------------------------------------

    while True:

        # ----------------------------------------------------
        # WAIT FOR LEO
        # ----------------------------------------------------

        command = wait_for_wake_word()


        # ----------------------------------------------------
        # USER ONLY SAID "LEO"
        # ----------------------------------------------------

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
        # SEND COMMAND TO GEMINI
        # ----------------------------------------------------

        try:

            answer, previous_interaction_id = ask_ai(

                command,

                previous_interaction_id

            )


            # ------------------------------------------------
            # SPEAK RESPONSE
            # ------------------------------------------------

            if answer:

                speak(answer)

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
