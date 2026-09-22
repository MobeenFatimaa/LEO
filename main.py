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
    get_weather,
    take_screenshot,
    get_system_info,
    get_battery_status,
    volume_up,
    volume_down,
    mute_volume,
    lock_windows,
    search_files,
    create_note,
    read_text_file
)

from memory import (
    remember_fact,
    forget_fact,
    get_memory
)

from reminders import (
    create_reminder,
    list_reminders,
    cancel_reminder,
    ReminderMonitor
)

from conversation_history import (
    add_message,
    format_recent_history,
    clear_history
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
        "GEMINI_API_KEY was not found "
        "in your .env file."
    )


# ============================================================
# GEMINI
# ============================================================

client = genai.Client(
    api_key=GEMINI_API_KEY
)


# ============================================================
# VOICE ENGINE
# ============================================================

engine = pyttsx3.init()


# ============================================================
# SYSTEM INSTRUCTION
# ============================================================

SYSTEM_INSTRUCTION = """

You are LEO, a personal AI voice assistant
running on a Windows computer.

Your name is LEO.

You are helpful, concise, friendly, and natural.

Your responses are spoken aloud.

Keep responses reasonably short.

Avoid markdown and unnecessary formatting.

============================================================
CURRENT INFORMATION
============================================================

Use Google Search for:

- Latest information
- Current news
- Recent events
- Current prices
- Recent technology developments
- Up-to-date facts

============================================================
COMPUTER
============================================================

Use the application tool for:

- Chrome
- Notepad
- Calculator
- Paint
- Command Prompt
- PowerShell
- File Explorer
- Task Manager

Use the VS Code tool for:

- VS Code
- Visual Studio Code

Use the folder tool for:

- Desktop
- Documents
- Downloads
- Pictures
- Videos
- Music

============================================================
SYSTEM
============================================================

Use the screenshot tool for:

- Take a screenshot
- Screenshot the screen
- Capture the screen

Use the system information tool for:

- Computer specifications
- Operating system
- Processor
- RAM

Use the battery tool for:

- Battery percentage
- Charging status
- Battery state

Use volume tools for:

- Increase volume
- Decrease volume
- Mute volume

Use the lock tool when explicitly asked to lock Windows.

============================================================
FILES
============================================================

Use file search when asked to find a file.

Use the note tool to save notes.

Use the read-text-file tool only for:

- TXT
- MD
- CSV
- LOG

Do not claim to read files unless the tool actually succeeds.

============================================================
REMINDERS
============================================================

Use create_reminder when the user asks for a reminder.

The reminder time must be supplied as:

YYYY-MM-DD HH:MM

Use list_reminders when the user asks:

- What reminders do I have?
- List my reminders
- Show my reminders

Use cancel_reminder when the user explicitly asks
to cancel a reminder.

============================================================
MEMORY
============================================================

Use remember_fact only when the user explicitly asks
you to remember a personal fact.

Use forget_fact when the user explicitly asks
you to forget something.

Use get_memory when the user asks about stored memory.

============================================================
CONVERSATION HISTORY
============================================================

Use the conversation history tool when the user asks:

- What did we talk about?
- Show recent conversation
- What did I say earlier?
- Show conversation history

Use clear history only when explicitly requested.

============================================================
SAFETY
============================================================

Only perform actions through available tools.

Never claim an action succeeded if the tool did not
actually succeed.

Do not execute arbitrary shell commands.

Do not delete files.

Do not modify system settings without a dedicated tool.

Do not invent information.

============================================================
"""


# ============================================================
# SPEAK
# ============================================================

def speak(text):

    if not text:

        return

    print(
        "LEO:",
        text
    )

    engine.say(
        text
    )

    engine.runAndWait()


# ============================================================
# LISTEN
# ============================================================

def listen():

    recognizer = sr.Recognizer()

    with sr.Microphone() as source:

        print(
            "\nListening..."
        )

        try:

            recognizer.adjust_for_ambient_noise(
                source,
                duration=1
            )

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

        except Exception as e:

            print(
                "[MICROPHONE ERROR]",
                e
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
            "to speech recognition."
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
# REMINDER CALLBACK
# ============================================================

def reminder_callback(
    reminder
):

    message = reminder.get(
        "message",
        "You have a reminder."
    )

    print(
        "\n[REMINDER]",
        message
    )

    speak(
        f"Reminder. {message}"
    )


# ============================================================
# TOOL DEFINITIONS
# ============================================================

open_website_tool = {

    "type": "function",

    "name": "open_website",

    "description": (
        "Open a supported website."
    ),

    "parameters": {

        "type": "object",

        "properties": {

            "website": {

                "type": "string"
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

                "type": "string"
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
        "Open Visual Studio Code."
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
        "Open a supported Windows folder."
    ),

    "parameters": {

        "type": "object",

        "properties": {

            "folder": {

                "type": "string"
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

                "type": "string"
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
        "Get current weather for a location."
    ),

    "parameters": {

        "type": "object",

        "properties": {

            "location": {

                "type": "string"
            }
        },

        "required": [
            "location"
        ]
    }
}


screenshot_tool = {

    "type": "function",

    "name": "take_screenshot",

    "description": (
        "Take and save a screenshot."
    ),

    "parameters": {

        "type": "object",

        "properties": {},

        "required": []
    }
}


system_info_tool = {

    "type": "function",

    "name": "get_system_info",

    "description": (
        "Get computer system information."
    ),

    "parameters": {

        "type": "object",

        "properties": {},

        "required": []
    }
}


battery_tool = {

    "type": "function",

    "name": "get_battery_status",

    "description": (
        "Get laptop battery status."
    ),

    "parameters": {

        "type": "object",

        "properties": {},

        "required": []
    }
}


volume_up_tool = {

    "type": "function",

    "name": "volume_up",

    "description": (
        "Increase system volume."
    ),

    "parameters": {

        "type": "object",

        "properties": {},

        "required": []
    }
}


volume_down_tool = {

    "type": "function",

    "name": "volume_down",

    "description": (
        "Decrease system volume."
    ),

    "parameters": {

        "type": "object",

        "properties": {},

        "required": []
    }
}


mute_volume_tool = {

    "type": "function",

    "name": "mute_volume",

    "description": (
        "Mute system volume."
    ),

    "parameters": {

        "type": "object",

        "properties": {},

        "required": []
    }
}


lock_windows_tool = {

    "type": "function",

    "name": "lock_windows",

    "description": (
        "Lock the Windows computer."
    ),

    "parameters": {

        "type": "object",

        "properties": {},

        "required": []
    }
}


search_files_tool = {

    "type": "function",

    "name": "search_files",

    "description": (
        "Search the user's home directory for files."
    ),

    "parameters": {

        "type": "object",

        "properties": {

            "filename": {

                "type": "string"
            }
        },

        "required": [
            "filename"
        ]
    }
}


create_note_tool = {

    "type": "function",

    "name": "create_note",

    "description": (
        "Create a local text note."
    ),

    "parameters": {

        "type": "object",

        "properties": {

            "note": {

                "type": "string"
            }
        },

        "required": [
            "note"
        ]
    }
}


read_text_file_tool = {

    "type": "function",

    "name": "read_text_file",

    "description": (
        "Read a supported local text file."
    ),

    "parameters": {

        "type": "object",

        "properties": {

            "filepath": {

                "type": "string"
            }
        },

        "required": [
            "filepath"
        ]
    }
}


create_reminder_tool = {

    "type": "function",

    "name": "create_reminder",

    "description": (
        "Create a reminder for a specific date and time."
    ),

    "parameters": {

        "type": "object",

        "properties": {

            "message": {

                "type": "string",

                "description": (
                    "What the user wants to be reminded about."
                )
            },

            "reminder_time": {

                "type": "string",

                "description": (
                    "Reminder date and time in "
                    "YYYY-MM-DD HH:MM format."
                )
            }
        },

        "required": [
            "message",
            "reminder_time"
        ]
    }
}


list_reminders_tool = {

    "type": "function",

    "name": "list_reminders",

    "description": (
        "List all active reminders."
    ),

    "parameters": {

        "type": "object",

        "properties": {},

        "required": []
    }
}


cancel_reminder_tool = {

    "type": "function",

    "name": "cancel_reminder",

    "description": (
        "Cancel an existing reminder by its ID."
    ),

    "parameters": {

        "type": "object",

        "properties": {

            "reminder_id": {

                "type": "string"
            }
        },

        "required": [
            "reminder_id"
        ]
    }
}


remember_fact_tool = {

    "type": "function",

    "name": "remember_fact",

    "description": (
        "Save a personal fact explicitly "
        "provided by the user."
    ),

    "parameters": {

        "type": "object",

        "properties": {

            "key": {

                "type": "string"
            },

            "value": {

                "type": "string"
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
        "Forget a stored personal fact."
    ),

    "parameters": {

        "type": "object",

        "properties": {

            "key": {

                "type": "string"
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
        "Retrieve stored memory."
    ),

    "parameters": {

        "type": "object",

        "properties": {

            "key": {

                "type": "string"
            }
        },

        "required": [
            "key"
        ]
    }
}


get_history_tool = {

    "type": "function",

    "name": "get_recent_history",

    "description": (
        "Retrieve recent conversation history."
    ),

    "parameters": {

        "type": "object",

        "properties": {

            "count": {

                "type": "integer",

                "description": (
                    "Number of recent messages."
                )
            }
        },

        "required": [
            "count"
        ]
    }
}


clear_history_tool = {

    "type": "function",

    "name": "clear_history",

    "description": (
        "Clear locally stored conversation history."
    ),

    "parameters": {

        "type": "object",

        "properties": {},

        "required": []
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

    screenshot_tool,

    system_info_tool,

    battery_tool,

    volume_up_tool,

    volume_down_tool,

    mute_volume_tool,

    lock_windows_tool,

    search_files_tool,

    create_note_tool,

    read_text_file_tool,

    create_reminder_tool,

    list_reminders_tool,

    cancel_reminder_tool,

    remember_fact_tool,

    forget_fact_tool,

    get_memory_tool,

    get_history_tool,

    clear_history_tool
]


# ============================================================
# EXECUTE TOOL
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


    elif name == "take_screenshot":

        return take_screenshot()


    elif name == "get_system_info":

        return get_system_info()


    elif name == "get_battery_status":

        return get_battery_status()


    elif name == "volume_up":

        return volume_up()


    elif name == "volume_down":

        return volume_down()


    elif name == "mute_volume":

        return mute_volume()


    elif name == "lock_windows":

        return lock_windows()


    elif name == "search_files":

        return search_files(
            arguments["filename"]
        )


    elif name == "create_note":

        return create_note(
            arguments["note"]
        )


    elif name == "read_text_file":

        return read_text_file(
            arguments["filepath"]
        )


    elif name == "create_reminder":

        return create_reminder(

            arguments["message"],

            arguments["reminder_time"]

        )


    elif name == "list_reminders":

        return list_reminders()


    elif name == "cancel_reminder":

        return cancel_reminder(

            arguments["reminder_id"]

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


    elif name == "get_recent_history":

        count = arguments.get(
            "count",
            10
        )

        return format_recent_history(
            count
        )


    elif name == "clear_history":

        return clear_history()


    return "Unknown tool."


# ============================================================
# GEMINI
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


    while True:

        function_calls = []

        for step in interaction.steps:

            if step.type == "function_call":

                function_calls.append(
                    step
                )


        if not function_calls:

            return (

                interaction.output_text,

                interaction.id

            )


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

                            "text": json.dumps({

                                "result": result

                            })

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

                            "text": json.dumps({

                                "error": str(e)

                            })

                        }

                    ]

                })


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
# STARTUP
# ============================================================

def startup():

    print()
    print("=" * 60)
    print("                 LEO AI ASSISTANT")
    print("=" * 60)
    print()
    print("Status: Online")
    print("Voice: Ready")
    print("Gemini: Connected")
    print("Memory: Enabled")
    print("Reminders: Enabled")
    print("Conversation history: Enabled")
    print()
    print("=" * 60)
    print()


# ============================================================
# MAIN
# ============================================================

def main():

    startup()

    speak(
        "Hello. I am Leo. "
        "I am online and ready."
    )


    # --------------------------------------------------------
    # START REMINDER MONITOR
    # --------------------------------------------------------

    reminder_monitor = ReminderMonitor(
        reminder_callback
    )

    reminder_monitor.start()


    previous_interaction_id = None


    try:

        while True:

            command = wait_for_wake_word()


            if not command:

                command = listen()


            if not command:

                continue


            # ------------------------------------------------
            # EXIT
            # ------------------------------------------------

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


            # ------------------------------------------------
            # SAVE USER MESSAGE
            # ------------------------------------------------

            add_message(
                "user",
                command
            )


            # ------------------------------------------------
            # ASK GEMINI
            # ------------------------------------------------

            try:

                answer, previous_interaction_id = ask_ai(

                    command,

                    previous_interaction_id

                )


                if answer:

                    speak(
                        answer
                    )

                    add_message(
                        "leo",
                        answer
                    )

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


    finally:

        reminder_monitor.stop()


# ============================================================
# START
# ============================================================

if __name__ == "__main__":

    main()
