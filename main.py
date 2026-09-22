import os
import time
import threading

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
    read_text_file,
)

from memory import (
    remember_fact,
    forget_fact,
    get_memory,
)

from reminders import (
    create_reminder,
    list_reminders,
    cancel_reminder,
    ReminderMonitor,
)

from conversation_history import (
    add_message,
    get_recent_history,
    clear_history,
)

from timers import (
    create_timer,
    list_timers,
    cancel_timer,
    TimerMonitor,
)

from alarms import (
    create_alarm,
    list_alarms,
    cancel_alarm,
    AlarmMonitor,
)

from preferences import (
    set_preference,
    get_preference,
    get_all_preferences,
    reset_preferences,
)


# =========================================================
# ENVIRONMENT
# =========================================================

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:

    raise RuntimeError(
        "GEMINI_API_KEY was not found in .env"
    )


client = genai.Client(
    api_key=GEMINI_API_KEY
)


# =========================================================
# VOICE ENGINE
# =========================================================

engine = pyttsx3.init()

engine.setProperty(
    "rate",
    175
)

engine.setProperty(
    "volume",
    1.0
)


# =========================================================
# GLOBAL STATE
# =========================================================

previous_interaction_id = None

conversation_active = True

speaking = False

stop_requested = False


# =========================================================
# SYSTEM INSTRUCTION
# =========================================================

SYSTEM_INSTRUCTION = """
You are LEO, a personal Windows desktop voice assistant.

You are conversational, concise, helpful, and natural.

The user communicates with you primarily through voice.

IMPORTANT BEHAVIOR:

1. Understand natural language.
2. Do not require exact commands.
3. Use tools when a real action is requested.
4. Never claim an action succeeded if the tool failed.
5. If a tool returns an error, explain it briefly.
6. Remember information when the user explicitly asks you to remember it.
7. Use conversation history for follow-up questions.
8. Maintain conversational context.
9. Use Google Search when current web information is required.
10. Do not invent current information.
11. Prefer short spoken responses.
12. Avoid unnecessary long explanations.

CONTEXTUAL COMMANDS:

Understand commands such as:

"open it"
"close that"
"search that"
"remember this"
"what did I just say?"
"do that again"
"what about tomorrow?"
"cancel it"
"show me my reminders"
"set one for later"

Use previous conversation context when interpreting these.

TIME:

Understand natural timer requests:

"set a timer for 5 minutes"
"timer for 30 seconds"
"remind me in 2 hours"

For timers, use create_timer.

ALARMS:

Understand:

"set an alarm for 7 AM"
"wake me up at 6:30"
"set my daily alarm for 8 AM"

Use create_alarm.

REMINDERS:

For date/time reminders use create_reminder.

MEMORY:

Use remember_fact when the user explicitly tells you to remember something.

Use get_memory when the user asks what you remember.

Use forget_fact when the user asks you to forget something.

PREFERENCES:

The user may tell you preferences such as:

"my name is..."
"call me..."
"my default location is..."
"set my voice speed..."

Use preference tools.

WINDOWS:

You can open websites, applications, folders, VS Code,
take screenshots, control volume, lock Windows, inspect
system information and battery status.

FILES:

You can search files, create notes and read supported text files.

SAFETY:

Do not perform destructive or dangerous actions unless
the user explicitly requests them and the tool supports them.

Keep spoken responses concise.
"""


# =========================================================
# SPEAK
# =========================================================

def speak(text):

    global speaking
    global stop_requested

    if not text:
        return

    speaking = True
    stop_requested = False

    print(f"LEO: {text}")

    try:

        engine.say(text)

        engine.runAndWait()

    except Exception as error:

        print(
            f"Speech error: {error}"
        )

    finally:

        speaking = False


# =========================================================
# LISTEN
# =========================================================

recognizer = sr.Recognizer()

recognizer.energy_threshold = 300

recognizer.dynamic_energy_threshold = True


def listen(timeout=5, phrase_time_limit=12):

    with sr.Microphone() as source:

        try:

            print("\nListening...")

            recognizer.adjust_for_ambient_noise(
                source,
                duration=0.5
            )

            audio = recognizer.listen(
                source,
                timeout=timeout,
                phrase_time_limit=phrase_time_limit
            )

        except sr.WaitTimeoutError:

            return ""

        except Exception as error:

            print(
                f"Microphone error: {error}"
            )

            return ""

    try:

        text = recognizer.recognize_google(
            audio
        )

        text = text.strip()

        print(
            f"You: {text}"
        )

        return text

    except sr.UnknownValueError:

        return ""

    except sr.RequestError as error:

        print(
            f"Speech recognition error: {error}"
        )

        return ""


# =========================================================
# COMMAND NORMALIZATION
# =========================================================

def normalize_command(command):

    command = command.strip()

    prefixes = [
        "leo",
        "hey leo",
        "okay leo",
        "ok leo",
    ]

    lower = command.lower()

    for prefix in prefixes:

        if lower.startswith(prefix):

            command = command[
                len(prefix):
            ].strip()

            break

    return command


# =========================================================
# WAKE WORD
# =========================================================

def wait_for_wake_word():

    print(
        "\nWaiting for wake word: LEO..."
    )

    while True:

        command = listen(
            timeout=5,
            phrase_time_limit=8
        )

        if not command:
            continue

        lower = command.lower()

        if "leo" in lower:

            return normalize_command(
                command
            )


# =========================================================
# REMINDER CALLBACK
# =========================================================

def reminder_callback(
    reminder_id,
    message
):

    print(
        f"\nREMINDER: {message}"
    )

    speak(
        f"Reminder. {message}"
    )


# =========================================================
# TIMER CALLBACK
# =========================================================

def timer_callback(
    timer_id,
    message
):

    print(
        f"\nTIMER FINISHED: {message}"
    )

    speak(
        f"Timer finished. {message}"
    )


# =========================================================
# ALARM CALLBACK
# =========================================================

def alarm_callback(
    alarm_id,
    message
):

    print(
        f"\nALARM: {message}"
    )

    speak(
        f"Alarm. {message}"
    )


# =========================================================
# TOOL DEFINITIONS
# =========================================================

TOOL_DEFINITIONS = [

    {
        "name": "open_website",
        "description": "Open a website in the browser.",
        "parameters": {
            "type": "object",
            "properties": {
                "website": {
                    "type": "string"
                }
            },
            "required": ["website"]
        }
    },

    {
        "name": "open_application",
        "description": "Open a Windows application.",
        "parameters": {
            "type": "object",
            "properties": {
                "application": {
                    "type": "string"
                }
            },
            "required": ["application"]
        }
    },

    {
        "name": "open_vscode",
        "description": "Open Visual Studio Code.",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    },

    {
        "name": "open_folder",
        "description": "Open a Windows folder.",
        "parameters": {
            "type": "object",
            "properties": {
                "folder": {
                    "type": "string"
                }
            },
            "required": ["folder"]
        }
    },

    {
        "name": "get_time",
        "description": "Get the current local time.",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    },

    {
        "name": "get_date",
        "description": "Get today's date.",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    },

    {
        "name": "calculate",
        "description": "Calculate a mathematical expression.",
        "parameters": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string"
                }
            },
            "required": ["expression"]
        }
    },

    {
        "name": "get_weather",
        "description": "Get current weather for a location.",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string"
                }
            },
            "required": ["location"]
        }
    },

    {
        "name": "take_screenshot",
        "description": "Take a screenshot of the desktop.",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    },

    {
        "name": "get_system_info",
        "description": "Get Windows system information.",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    },

    {
        "name": "get_battery_status",
        "description": "Get battery status.",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    },

    {
        "name": "volume_up",
        "description": "Increase Windows volume.",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    },

    {
        "name": "volume_down",
        "description": "Decrease Windows volume.",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    },

    {
        "name": "mute_volume",
        "description": "Mute Windows volume.",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    },

    {
        "name": "lock_windows",
        "description": "Lock Windows.",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    },

    {
        "name": "search_files",
        "description": "Search for files on the user's computer.",
        "parameters": {
            "type": "object",
            "properties": {
                "filename": {
                    "type": "string"
                }
            },
            "required": ["filename"]
        }
    },

    {
        "name": "create_note",
        "description": "Create a text note.",
        "parameters": {
            "type": "object",
            "properties": {
                "note": {
                    "type": "string"
                }
            },
            "required": ["note"]
        }
    },

    {
        "name": "read_text_file",
        "description": "Read a supported text file.",
        "parameters": {
            "type": "object",
            "properties": {
                "filepath": {
                    "type": "string"
                }
            },
            "required": ["filepath"]
        }
    },

    # =====================================================
    # REMINDERS
    # =====================================================

    {
        "name": "create_reminder",
        "description": "Create a reminder for a specific date and time. Use YYYY-MM-DD HH:MM.",
        "parameters": {
            "type": "object",
            "properties": {
                "message": {
                    "type": "string"
                },
                "reminder_time": {
                    "type": "string"
                }
            },
            "required": [
                "message",
                "reminder_time"
            ]
        }
    },

    {
        "name": "list_reminders",
        "description": "List reminders.",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    },

    {
        "name": "cancel_reminder",
        "description": "Cancel a reminder using its ID.",
        "parameters": {
            "type": "object",
            "properties": {
                "reminder_id": {
                    "type": "string"
                }
            },
            "required": ["reminder_id"]
        }
    },

    # =====================================================
    # TIMERS
    # =====================================================

    {
        "name": "create_timer",
        "description": "Start a countdown timer in seconds.",
        "parameters": {
            "type": "object",
            "properties": {
                "seconds": {
                    "type": "integer"
                },
                "message": {
                    "type": "string"
                }
            },
            "required": [
                "seconds",
                "message"
            ]
        }
    },

    {
        "name": "list_timers",
        "description": "List active countdown timers.",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    },

    {
        "name": "cancel_timer",
        "description": "Cancel a countdown timer using its ID.",
        "parameters": {
            "type": "object",
            "properties": {
                "timer_id": {
                    "type": "string"
                }
            },
            "required": ["timer_id"]
        }
    },

    # =====================================================
    # ALARMS
    # =====================================================

    {
        "name": "create_alarm",
        "description": "Create a daily repeating alarm using HH:MM 24-hour format.",
        "parameters": {
            "type": "object",
            "properties": {
                "alarm_time": {
                    "type": "string"
                },
                "message": {
                    "type": "string"
                }
            },
            "required": [
                "alarm_time",
                "message"
            ]
        }
    },

    {
        "name": "list_alarms",
        "description": "List active alarms.",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    },

    {
        "name": "cancel_alarm",
        "description": "Cancel a daily alarm using its ID.",
        "parameters": {
            "type": "object",
            "properties": {
                "alarm_id": {
                    "type": "string"
                }
            },
            "required": ["alarm_id"]
        }
    },

    # =====================================================
    # MEMORY
    # =====================================================

    {
        "name": "remember_fact",
        "description": "Remember a fact explicitly provided by the user.",
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
    },

    {
        "name": "forget_fact",
        "description": "Forget a stored fact.",
        "parameters": {
            "type": "object",
            "properties": {
                "key": {
                    "type": "string"
                }
            },
            "required": ["key"]
        }
    },

    {
        "name": "get_memory",
        "description": "Retrieve stored memory.",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    },

    # =====================================================
    # CONVERSATION
    # =====================================================

    {
        "name": "get_recent_history",
        "description": "Retrieve recent conversation history.",
        "parameters": {
            "type": "object",
            "properties": {
                "count": {
                    "type": "integer"
                }
            }
        }
    },

    {
        "name": "clear_history",
        "description": "Clear stored conversation history.",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    },

    # =====================================================
    # PREFERENCES
    # =====================================================

    {
        "name": "set_preference",
        "description": "Set a user preference.",
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
    },

    {
        "name": "get_preference",
        "description": "Get one user preference.",
        "parameters": {
            "type": "object",
            "properties": {
                "key": {
                    "type": "string"
                }
            },
            "required": ["key"]
        }
    },

    {
        "name": "get_all_preferences",
        "description": "Get all user preferences.",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    },

    {
        "name": "reset_preferences",
        "description": "Reset preferences to defaults.",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    }
]


# =========================================================
# GEMINI TOOLS
# =========================================================

tools = [
    {
        "type": "google_search"
    }
]

for definition in TOOL_DEFINITIONS:

    tools.append(
        {
            "type": "function",
            "name": definition["name"],
            "description": definition["description"],
            "parameters": definition["parameters"]
        }
    )


# =========================================================
# TOOL EXECUTION
# =========================================================

def execute_tool(
    tool_name,
    arguments
):

    try:

        if tool_name == "open_website":

            return open_website(
                arguments.get("website")
            )

        if tool_name == "open_application":

            return open_application(
                arguments.get("application")
            )

        if tool_name == "open_vscode":

            return open_vscode()

        if tool_name == "open_folder":

            return open_folder(
                arguments.get("folder")
            )

        if tool_name == "get_time":

            return get_time()

        if tool_name == "get_date":

            return get_date()

        if tool_name == "calculate":

            return calculate(
                arguments.get("expression")
            )

        if tool_name == "get_weather":

            return get_weather(
                arguments.get("location")
            )

        if tool_name == "take_screenshot":

            return take_screenshot()

        if tool_name == "get_system_info":

            return get_system_info()

        if tool_name == "get_battery_status":

            return get_battery_status()

        if tool_name == "volume_up":

            return volume_up()

        if tool_name == "volume_down":

            return volume_down()

        if tool_name == "mute_volume":

            return mute_volume()

        if tool_name == "lock_windows":

            return lock_windows()

        if tool_name == "search_files":

            return search_files(
                arguments.get("filename")
            )

        if tool_name == "create_note":

            return create_note(
                arguments.get("note")
            )

        if tool_name == "read_text_file":

            return read_text_file(
                arguments.get("filepath")
            )

        # -------------------------------------------------
        # REMINDERS
        # -------------------------------------------------

        if tool_name == "create_reminder":

            return create_reminder(
                arguments.get("message"),
                arguments.get("reminder_time")
            )

        if tool_name == "list_reminders":

            return list_reminders()

        if tool_name == "cancel_reminder":

            return cancel_reminder(
                arguments.get("reminder_id")
            )

        # -------------------------------------------------
        # TIMERS
        # -------------------------------------------------

        if tool_name == "create_timer":

            return create_timer(
                arguments.get("seconds"),
                arguments.get("message")
            )

        if tool_name == "list_timers":

            return list_timers()

        if tool_name == "cancel_timer":

            return cancel_timer(
                arguments.get("timer_id")
            )

        # -------------------------------------------------
        # ALARMS
        # -------------------------------------------------

        if tool_name == "create_alarm":

            return create_alarm(
                arguments.get("alarm_time"),
                arguments.get("message")
            )

        if tool_name == "list_alarms":

            return list_alarms()

        if tool_name == "cancel_alarm":

            return cancel_alarm(
                arguments.get("alarm_id")
            )

        # -------------------------------------------------
        # MEMORY
        # -------------------------------------------------

        if tool_name == "remember_fact":

            return remember_fact(
                arguments.get("key"),
                arguments.get("value")
            )

        if tool_name == "forget_fact":

            return forget_fact(
                arguments.get("key")
            )

        if tool_name == "get_memory":

            return get_memory()

        # -------------------------------------------------
        # CONVERSATION
        # -------------------------------------------------

        if tool_name == "get_recent_history":

            count = arguments.get(
                "count",
                10
            )

            return get_recent_history(
                count
            )

        if tool_name == "clear_history":

            return clear_history()

        # -------------------------------------------------
        # PREFERENCES
        # -------------------------------------------------

        if tool_name == "set_preference":

            return set_preference(
                arguments.get("key"),
                arguments.get("value")
            )

        if tool_name == "get_preference":

            return str(
                get_preference(
                    arguments.get("key")
                )
            )

        if tool_name == "get_all_preferences":

            return get_all_preferences()

        if tool_name == "reset_preferences":

            return reset_preferences()

        return (
            f"Unknown tool: {tool_name}"
        )

    except Exception as error:

        print(
            f"Tool error [{tool_name}]: {error}"
        )

        return (
            f"The tool '{tool_name}' failed: "
            f"{error}"
        )


# =========================================================
# ASK GEMINI
# =========================================================

def ask_ai(user_message):

    global previous_interaction_id

    recent_context = get_recent_history(8)

    enhanced_message = f"""
Recent conversation context:

{recent_context}

Current user request:

{user_message}
"""

    try:

        interaction = client.interactions.create(

            model="gemini-3.8-flash",

            input=enhanced_message,

            system_instruction=SYSTEM_INSTRUCTION,

            tools=tools,

            previous_interaction_id=(
                previous_interaction_id
            ) if previous_interaction_id else None
        )

    except Exception as error:

        print(
            f"Gemini request error: {error}"
        )

        return (
            "I couldn't connect to Gemini right now."
        )

    while True:

        previous_interaction_id = (
            interaction.id
        )

        function_calls = []

        try:

            for output in interaction.outputs:

                if getattr(
                    output,
                    "type",
                    None
                ) == "function_call":

                    function_calls.append(
                        output
                    )

        except Exception as error:

            print(
                f"Output processing error: {error}"
            )

        if not function_calls:

            try:

                return (
                    interaction.output_text
                    or
                    "I'm ready."
                )

            except Exception:

                return "I'm ready."

        function_results = []

        for call in function_calls:

            tool_name = call.name

            arguments = (
                call.arguments
                if call.arguments
                else {}
            )

            print(
                f"\n[Tool] {tool_name}"
            )

            print(
                f"[Arguments] {arguments}"
            )

            result = execute_tool(
                tool_name,
                arguments
            )

            print(
                f"[Result] {result}"
            )

            function_results.append(
                {
                    "type": "function_result",
                    "call_id": call.id,
                    "result": str(result)
                }
            )

        try:

            interaction = client.interactions.create(

                model="gemini-3.8-flash",

                input=function_results,

                system_instruction=SYSTEM_INSTRUCTION,

                tools=tools,

                previous_interaction_id=(
                    previous_interaction_id
                )
            )

        except Exception as error:

            print(
                f"Gemini continuation error: {error}"
            )

            return (
                "The action was attempted, "
                "but I couldn't complete the response."
            )


# =========================================================
# COMMAND CLASSIFICATION
# =========================================================

def is_exit_command(command):

    command = command.lower().strip()

    exit_commands = [
        "exit",
        "quit",
        "goodbye",
        "shut down",
        "shutdown",
        "stop leo"
    ]

    return command in exit_commands


def is_stop_command(command):

    command = command.lower().strip()

    stop_commands = [
        "stop",
        "stop speaking",
        "be quiet",
        "quiet",
        "cancel speech"
    ]

    return command in stop_commands


# =========================================================
# STARTUP
# =========================================================

def startup():

    print("=" * 60)

    print(
        "LEO 1.4 — Natural Voice + Agent Intelligence"
    )

    print("=" * 60)

    print(
        "Gemini: Connected"
    )

    print(
        "Voice: Ready"
    )

    print(
        "Reminders: Enabled"
    )

    print(
        "Timers: Enabled"
    )

    print(
        "Alarms: Enabled"
    )

    print(
        "Memory: Enabled"
    )

    print(
        "Conversation history: Enabled"
    )

    print(
        "Preferences: Enabled"
    )

    print("=" * 60)


# =========================================================
# MAIN
# =========================================================

def main():

    global conversation_active

    startup()

    reminder_monitor = ReminderMonitor(
        reminder_callback
    )

    timer_monitor = TimerMonitor(
        timer_callback
    )

    alarm_monitor = AlarmMonitor(
        alarm_callback
    )

    reminder_monitor.start()

    timer_monitor.start()

    alarm_monitor.start()

    speak(
        "LEO is online. How can I help you?"
    )

    try:

        while conversation_active:

            # ---------------------------------------------
            # LISTEN
            # ---------------------------------------------

            command = listen(
                timeout=10,
                phrase_time_limit=15
            )

            if not command:

                continue

            normalized = normalize_command(
                command
            )

            if not normalized:

                continue

            # ---------------------------------------------
            # EXIT
            # ---------------------------------------------

            if is_exit_command(normalized):

                speak(
                    "Goodbye."
                )

                break

            # ---------------------------------------------
            # STOP SPEECH
            # ---------------------------------------------

            if is_stop_command(normalized):

                engine.stop()

                speak(
                    "Okay."
                )

                continue

            # ---------------------------------------------
            # STORE USER MESSAGE
            # ---------------------------------------------

            add_message(
                "user",
                normalized
            )

            # ---------------------------------------------
            # GEMINI
            # ---------------------------------------------

            response = ask_ai(
                normalized
            )

            # ---------------------------------------------
            # STORE RESPONSE
            # ---------------------------------------------

            add_message(
                "assistant",
                response
            )

            # ---------------------------------------------
            # SPEAK
            # ---------------------------------------------

            speak(
                response
            )

    except KeyboardInterrupt:

        print(
            "\nLEO stopped by user."
        )

    except Exception as error:

        print(
            f"\nUnexpected error: {error}"
        )

    finally:

        conversation_active = False

        reminder_monitor.stop()

        timer_monitor.stop()

        alarm_monitor.stop()

        print(
            "\nLEO has shut down."
        )


# =========================================================
# ENTRY POINT
# =========================================================

if __name__ == "__main__":

    main()
