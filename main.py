# =========================================================
# LEO 2.5F
# Gemini + Autonomous Task Engine
# =========================================================

import os
import time
import json
import threading

import speech_recognition as sr
import pyttsx3

from dotenv import load_dotenv
from google import genai

# =========================================================
# BASIC TOOLS
# =========================================================

from tools.basic_tools import (
    open_website,
    search_web,
    open_application,
    close_application,
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
    set_volume_level,
    media_play_pause,
    media_next,
    media_previous,
    lock_windows,
    search_files,
    create_note,
    read_text_file,
    get_clipboard,
    set_clipboard,
)

# =========================================================
# MEMORY
# =========================================================

from memory import (
    remember_fact,
    forget_fact,
    get_memory,
)

# =========================================================
# REMINDERS
# =========================================================

from reminders import (
    create_reminder,
    list_reminders,
    cancel_reminder,
    ReminderMonitor,
)

# =========================================================
# TIMERS
# =========================================================

from timers import (
    create_timer,
    list_timers,
    cancel_timer,
    TimerMonitor,
)

# =========================================================
# ALARMS
# =========================================================

from alarms import (
    create_alarm,
    list_alarms,
    cancel_alarm,
    AlarmMonitor,
)

# =========================================================
# PREFERENCES
# =========================================================

from preferences import (
    set_preference,
    get_preference,
    get_all_preferences,
    reset_preferences,
)

# =========================================================
# SESSION CONTEXT
# =========================================================

from session_context import SessionContext

# =========================================================
# AUTONOMOUS TASK ENGINE
# =========================================================

from task_engine import (
    AutonomousTaskEngine,
    ENGINE_IDLE,
    ENGINE_PLANNING,
    ENGINE_EXECUTING,
    ENGINE_COMPLETED,
    ENGINE_FAILED,
    ENGINE_STOPPED,
)

# =========================================================
# LOAD ENVIRONMENT
# =========================================================

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY was not found in the .env file."
    )

client = genai.Client(api_key=API_KEY)

# =========================================================
# VOICE ENGINE
# =========================================================

engine = pyttsx3.init()

engine.setProperty("rate", 175)
engine.setProperty("volume", 1.0)

recognizer = sr.Recognizer()

# =========================================================
# GLOBAL STATE
# =========================================================

previous_interaction_id = None

session = SessionContext()

task_engine = None

# =========================================================
# SYSTEM INSTRUCTION
# =========================================================

SYSTEM_INSTRUCTION = """
You are LEO, a personal desktop AI voice assistant.

You operate on the user's Windows computer through safe,
explicitly provided tools.

Your job is to understand natural language requests and either:

1. Answer normally.
2. Use a single tool for a simple action.
3. Use the autonomous task engine for a multi-step task.

=========================================================
GENERAL BEHAVIOR
=========================================================

Speak naturally and concisely.

Do not unnecessarily explain internal implementation details.

When a user asks for information, answer directly.

When a user asks you to perform an action, use the appropriate
tool instead of merely explaining how to do it.

=========================================================
NORMAL TOOL ACTIONS
=========================================================

Use normal tools for simple requests such as:

- Open Chrome
- Open YouTube
- Open VS Code
- Open a folder
- Search the web
- Get weather
- Get time
- Get date
- Calculate something
- Take a screenshot
- Control volume
- Control media
- Read clipboard
- Set clipboard
- Create a note
- Search files
- Remember something
- Forget something
- Create a reminder
- Create a timer
- Create an alarm
- Set a preference

=========================================================
AUTONOMOUS TASKS
=========================================================

Use the autonomous task engine when the user requests a
multi-step workflow or task.

Examples:

"Prepare my coding workspace."

"Set up my AI workspace."

"Prepare everything I need for research."

"Get my study workspace ready."

"Open everything I need for development."

"Prepare my machine learning environment."

A multi-step task should be handled as one autonomous task
rather than requiring the user to issue every command separately.

=========================================================
TASK STATUS
=========================================================

The user may ask:

"What is the current task?"

"What's the task status?"

"Show task progress."

"How far are you?"

Answer using the current task engine state provided by the
application.

=========================================================
TASK CANCELLATION
=========================================================

If the user says:

"Cancel the task."

"Stop the task."

"Cancel what you're doing."

"Stop what you're doing."

the application will handle cancellation.

=========================================================
MEMORY
=========================================================

Use memory tools when the user explicitly asks you to
remember or forget information.

=========================================================
SAFETY
=========================================================

Never execute arbitrary shell commands.

Never delete arbitrary files.

Never terminate arbitrary processes.

Only use the explicitly provided tools.

Do not claim an action succeeded unless the tool reports success.

=========================================================
RESPONSE STYLE
=========================================================

Keep spoken responses short and natural.

For example:

"Sure. I'm preparing your coding workspace."

"Done. Your coding workspace is ready."

"The task was cancelled."

"The task failed while opening Chrome."
"""

# =========================================================
# VOICE FUNCTIONS
# =========================================================


def speak(text):
    """Speak text using the local text-to-speech engine."""

    if not text:
        return

    print(f"\nLEO: {text}\n")

    engine.say(text)
    engine.runAndWait()


def listen():
    """Listen to microphone input and convert it to text."""

    with sr.Microphone() as source:

        print("\nListening...")

        recognizer.adjust_for_ambient_noise(
            source,
            duration=0.5
        )

        try:

            audio = recognizer.listen(
                source,
                timeout=5,
                phrase_time_limit=12
            )

        except sr.WaitTimeoutError:

            return ""

    try:

        text = recognizer.recognize_google(audio)

        print(f"You: {text}")

        return text

    except sr.UnknownValueError:

        print("Could not understand audio.")

        return ""

    except sr.RequestError as error:

        print(f"Speech recognition error: {error}")

        return ""


# =========================================================
# TEXT NORMALIZATION
# =========================================================


def normalize_text(text):
    """Normalize user input."""

    return text.strip().lower()


# =========================================================
# EXIT COMMAND
# =========================================================


def is_exit_command(text):

    exit_commands = [
        "exit",
        "quit",
        "shutdown",
        "goodbye",
        "stop leo",
        "close leo",
    ]

    return normalize_text(text) in exit_commands


# =========================================================
# CONTEXT CLEAR COMMAND
# =========================================================


def is_clear_context_command(text):

    commands = [
        "clear context",
        "clear conversation",
        "reset conversation",
        "forget conversation",
    ]

    return normalize_text(text) in commands


# =========================================================
# TASK COMMAND DETECTION
# =========================================================


def is_task_status_command(text):

    normalized = normalize_text(text)

    commands = [
        "what is the current task",
        "what's the current task",
        "what is the task",
        "what's the task",
        "task status",
        "show task status",
        "show task progress",
        "what is the task status",
        "how is the task going",
        "how far are you",
    ]

    return normalized in commands


def is_task_cancel_command(text):

    normalized = normalize_text(text)

    commands = [
        "cancel the task",
        "cancel task",
        "stop the task",
        "stop task",
        "cancel what you're doing",
        "cancel what you are doing",
        "stop what you're doing",
        "stop what you are doing",
    ]

    return normalized in commands


# =========================================================
# TASK STATUS RESPONSE
# =========================================================


def get_task_status_response():

    if task_engine is None:

        return "The task engine is not available."

    summary = task_engine.get_summary()

    if not summary:

        return "There is currently no active task."

    status = summary.get("status", "UNKNOWN")

    current_request = summary.get(
        "current_request",
        ""
    )

    progress = summary.get(
        "progress",
        {}
    )

    completed = progress.get(
        "completed",
        0
    )

    total = progress.get(
        "total",
        0
    )

    failed = progress.get(
        "failed",
        0
    )

    stopped = progress.get(
        "stopped",
        0
    )

    if total > 0:

        return (
            f"Task status is {status.lower()}. "
            f"{completed} of {total} steps are completed. "
            f"{failed} failed and {stopped} stopped."
        )

    if current_request:

        return (
            f"The current task is {current_request}. "
            f"Status: {status.lower()}."
        )

    return f"Task status is {status.lower()}."


# =========================================================
# TASK CANCELLATION
# =========================================================


def cancel_current_task():

    if task_engine is None:

        return "The task engine is not available."

    summary = task_engine.get_summary()

    status = summary.get(
        "status",
        ENGINE_IDLE
    )

    if status not in [
        ENGINE_PLANNING,
        ENGINE_EXECUTING,
    ]:

        return "There is no active task to cancel."

    task_engine.cancel()

    return "The current task has been cancelled."


# =========================================================
# TASK REQUEST DETECTION
# =========================================================


def looks_like_autonomous_task(text):

    normalized = normalize_text(text)

    task_phrases = [
        "prepare my coding workspace",
        "prepare my ai workspace",
        "prepare my research workspace",
        "prepare my study workspace",
        "prepare everything for coding",
        "prepare everything for development",
        "prepare everything for research",
        "prepare everything for study",
        "get my coding workspace ready",
        "get my ai workspace ready",
        "get my research workspace ready",
        "get my study workspace ready",
        "set up my coding workspace",
        "set up my ai workspace",
        "set up my research workspace",
        "set up my study workspace",
        "open everything i need for coding",
        "open everything i need for development",
        "open everything i need for research",
        "open everything i need for study",
    ]

    for phrase in task_phrases:

        if phrase in normalized:
            return True

    return False


# =========================================================
# TASK ENGINE EXECUTION
# =========================================================


def run_autonomous_task(user_request):

    if task_engine is None:

        return (
            "The autonomous task engine "
            "is not available."
        )

    print("\n" + "=" * 60)
    print("AUTONOMOUS TASK")
    print("=" * 60)

    print(f"Request: {user_request}")

    speak(
        "Sure. I'm starting the task now."
    )

    try:

        result = task_engine.run(
            user_request
        )

        print("\nTask finished.")

        print(result)

        status = task_engine.get_summary().get(
            "status",
            ENGINE_FAILED
        )

        if status == ENGINE_COMPLETED:

            return (
                "Done. The autonomous task "
                "completed successfully."
            )

        elif status == ENGINE_STOPPED:

            return (
                "The task was stopped."
            )

        else:

            return (
                "The task finished with an error. "
                "Please check the task report."
            )

    except Exception as error:

        print(
            f"Autonomous task error: {error}"
        )

        return (
            "The autonomous task failed. "
            f"Reason: {error}"
        )


# =========================================================
# REMINDER CALLBACK
# =========================================================


def reminder_callback(reminder):

    message = reminder.get(
        "message",
        "Reminder"
    )

    print(
        f"\nREMINDER: {message}\n"
    )

    speak(
        f"Reminder. {message}"
    )


# =========================================================
# TIMER CALLBACK
# =========================================================


def timer_callback(timer):

    message = timer.get(
        "message",
        "Timer finished"
    )

    print(
        f"\nTIMER: {message}\n"
    )

    speak(
        f"Timer finished. {message}"
    )


# =========================================================
# ALARM CALLBACK
# =========================================================


def alarm_callback(alarm):

    message = alarm.get(
        "message",
        "Alarm"
    )

    print(
        f"\nALARM: {message}\n"
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
        "description": "Open a website in the default browser.",
        "parameters": {
            "type": "object",
            "properties": {
                "site": {
                    "type": "string",
                    "description": "Website name or URL."
                }
            },
            "required": ["site"]
        }
    },

    {
        "name": "search_web",
        "description": "Search the web for information.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query."
                }
            },
            "required": ["query"]
        }
    },

    {
        "name": "open_application",
        "description": "Open a supported Windows application.",
        "parameters": {
            "type": "object",
            "properties": {
                "application": {
                    "type": "string",
                    "description": "Application name."
                }
            },
            "required": ["application"]
        }
    },

    {
        "name": "close_application",
        "description": "Close a supported application.",
        "parameters": {
            "type": "object",
            "properties": {
                "application": {
                    "type": "string",
                    "description": "Application name."
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
        "description": "Open a folder.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Folder path."
                }
            },
            "required": ["path"]
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
        "description": "Get the current date.",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    },

    {
        "name": "calculate",
        "description": "Perform a mathematical calculation.",
        "parameters": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "Mathematical expression."
                }
            },
            "required": ["expression"]
        }
    },

    {
        "name": "get_weather",
        "description": "Get weather information.",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "City or location."
                }
            },
            "required": ["location"]
        }
    },

    {
        "name": "take_screenshot",
        "description": "Take a screenshot.",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    },

    {
        "name": "get_system_info",
        "description": "Get computer system information.",
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
        "description": "Increase system volume.",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    },

    {
        "name": "volume_down",
        "description": "Decrease system volume.",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    },

    {
        "name": "mute_volume",
        "description": "Mute system volume.",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    },

    {
        "name": "set_volume_level",
        "description": "Set system volume level.",
        "parameters": {
            "type": "object",
            "properties": {
                "level": {
                    "type": "integer",
                    "description": "Volume percentage."
                }
            },
            "required": ["level"]
        }
    },

    {
        "name": "media_play_pause",
        "description": "Play or pause media.",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    },

    {
        "name": "media_next",
        "description": "Skip to next media track.",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    },

    {
        "name": "media_previous",
        "description": "Go to previous media track.",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    },

    {
        "name": "lock_windows",
        "description": "Lock the Windows computer.",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    },

    {
        "name": "search_files",
        "description": "Search for files.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "File search query."
                }
            },
            "required": ["query"]
        }
    },

    {
        "name": "create_note",
        "description": "Create a text note.",
        "parameters": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "Note title."
                },
                "content": {
                    "type": "string",
                    "description": "Note content."
                }
            },
            "required": [
                "title",
                "content"
            ]
        }
    },

    {
        "name": "read_text_file",
        "description": "Read a text file.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "File path."
                }
            },
            "required": ["path"]
        }
    },

    {
        "name": "get_clipboard",
        "description": "Read clipboard contents.",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    },

    {
        "name": "set_clipboard",
        "description": "Set clipboard contents.",
        "parameters": {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "Clipboard text."
                }
            },
            "required": ["text"]
        }
    },

    {
        "name": "remember_fact",
        "description": "Remember a user fact.",
        "parameters": {
            "type": "object",
            "properties": {
                "key": {
                    "type": "string",
                    "description": "Memory key."
                },
                "value": {
                    "type": "string",
                    "description": "Memory value."
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
                    "type": "string",
                    "description": "Memory key."
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

    {
        "name": "create_reminder",
        "description": "Create a reminder.",
        "parameters": {
            "type": "object",
            "properties": {
                "delay_seconds": {
                    "type": "integer",
                    "description": "Seconds until reminder."
                },
                "message": {
                    "type": "string",
                    "description": "Reminder message."
                }
            },
            "required": [
                "delay_seconds",
                "message"
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
        "description": "Cancel a reminder.",
        "parameters": {
            "type": "object",
            "properties": {
                "reminder_id": {
                    "type": "string",
                    "description": "Reminder ID."
                }
            },
            "required": ["reminder_id"]
        }
    },

    {
        "name": "create_timer",
        "description": "Create a timer.",
        "parameters": {
            "type": "object",
            "properties": {
                "seconds": {
                    "type": "integer",
                    "description": "Timer duration in seconds."
                },
                "message": {
                    "type": "string",
                    "description": "Timer message."
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
        "description": "List active timers.",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    },

    {
        "name": "cancel_timer",
        "description": "Cancel a timer.",
        "parameters": {
            "type": "object",
            "properties": {
                "timer_id": {
                    "type": "string",
                    "description": "Timer ID."
                }
            },
            "required": ["timer_id"]
        }
    },

    {
        "name": "create_alarm",
        "description": "Create a daily alarm.",
        "parameters": {
            "type": "object",
            "properties": {
                "alarm_time": {
                    "type": "string",
                    "description": "Alarm time in HH:MM format."
                },
                "message": {
                    "type": "string",
                    "description": "Alarm message."
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
        "description": "List alarms.",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    },

    {
        "name": "cancel_alarm",
        "description": "Cancel an alarm.",
        "parameters": {
            "type": "object",
            "properties": {
                "alarm_id": {
                    "type": "string",
                    "description": "Alarm ID."
                }
            },
            "required": ["alarm_id"]
        }
    },

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
        "description": "Get a user preference.",
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
        "description": "Get all saved preferences.",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    },

    {
        "name": "reset_preferences",
        "description": "Reset saved preferences.",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    },
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
            "parameters": definition["parameters"],
        }
    )


# =========================================================
# TOOL EXECUTION
# =========================================================


def execute_tool(name, arguments):

    try:

        if name == "open_website":
            return open_website(
                arguments["site"]
            )

        elif name == "search_web":
            return search_web(
                arguments["query"]
            )

        elif name == "open_application":
            return open_application(
                arguments["application"]
            )

        elif name == "close_application":
            return close_application(
                arguments["application"]
            )

        elif name == "open_vscode":
            return open_vscode()

        elif name == "open_folder":
            return open_folder(
                arguments["path"]
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

        elif name == "set_volume_level":
            return set_volume_level(
                arguments["level"]
            )

        elif name == "media_play_pause":
            return media_play_pause()

        elif name == "media_next":
            return media_next()

        elif name == "media_previous":
            return media_previous()

        elif name == "lock_windows":
            return lock_windows()

        elif name == "search_files":
            return search_files(
                arguments["query"]
            )

        elif name == "create_note":
            return create_note(
                arguments["title"],
                arguments["content"]
            )

        elif name == "read_text_file":
            return read_text_file(
                arguments["path"]
            )

        elif name == "get_clipboard":
            return get_clipboard()

        elif name == "set_clipboard":
            return set_clipboard(
                arguments["text"]
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
            return get_memory()

        elif name == "create_reminder":
            return create_reminder(
                arguments["delay_seconds"],
                arguments["message"]
            )

        elif name == "list_reminders":
            return list_reminders()

        elif name == "cancel_reminder":
            return cancel_reminder(
                arguments["reminder_id"]
            )

        elif name == "create_timer":
            return create_timer(
                arguments["seconds"],
                arguments["message"]
            )

        elif name == "list_timers":
            return list_timers()

        elif name == "cancel_timer":
            return cancel_timer(
                arguments["timer_id"]
            )

        elif name == "create_alarm":
            return create_alarm(
                arguments["alarm_time"],
                arguments["message"]
            )

        elif name == "list_alarms":
            return list_alarms()

        elif name == "cancel_alarm":
            return cancel_alarm(
                arguments["alarm_id"]
            )

        elif name == "set_preference":
            return set_preference(
                arguments["key"],
                arguments["value"]
            )

        elif name == "get_preference":
            return get_preference(
                arguments["key"]
            )

        elif name == "get_all_preferences":
            return get_all_preferences()

        elif name == "reset_preferences":
            return reset_preferences()

        else:

            return (
                f"Unknown tool '{name}'."
            )

    except Exception as error:

        return (
            f"The tool '{name}' failed. "
            f"Reason: {error}"
        )


# =========================================================
# AI REQUEST
# =========================================================


def ask_ai(user_text):

    global previous_interaction_id

    persistent_history = []

    try:

        from conversation_history import (
            get_recent_history
        )

        persistent_history = (
            get_recent_history(8)
        )

    except Exception:

        persistent_history = []

    context = session.get_context()

    recent_messages = (
        session.get_recent_messages(6)
    )

    enhanced_message = f"""
CURRENT SESSION CONTEXT:
{json.dumps(context, indent=2, default=str)}

RECENT SESSION MESSAGES:
{json.dumps(recent_messages, indent=2, default=str)}

PERSISTENT CONVERSATION HISTORY:
{json.dumps(persistent_history, indent=2, default=str)}

CURRENT USER REQUEST:
{user_text}
"""

    try:

        interaction = client.interactions.create(

            model="gemini-3.8-flash",

            input=enhanced_message,

            system_instruction=SYSTEM_INSTRUCTION,

            tools=tools,

            previous_interaction_id=(
                previous_interaction_id
            ),
        )

        previous_interaction_id = (
            interaction.id
        )

    except Exception as error:

        return (
            f"I couldn't connect to Gemini. "
            f"Reason: {error}"
        )

    # =====================================================
    # FUNCTION CALL LOOP
    # =====================================================

    max_tool_rounds = 5

    for _ in range(max_tool_rounds):

        function_calls = []

        for output in interaction.outputs:

            if getattr(output, "type", None) == "function_call":

                function_calls.append(output)

        if not function_calls:

            response_text = (
                getattr(
                    interaction,
                    "output_text",
                    ""
                )
                or "I completed the request."
            )

            session.record_assistant_message(
                response_text
            )

            return response_text

        function_results = []

        for call in function_calls:

            name = call.name

            arguments = call.arguments

            if isinstance(arguments, str):

                try:

                    arguments = json.loads(
                        arguments
                    )

                except json.JSONDecodeError:

                    arguments = {}

            print(
                f"\nExecuting tool: {name}"
            )

            print(
                f"Arguments: {arguments}"
            )

            result = execute_tool(
                name,
                arguments
            )

            print(
                f"Result: {result}"
            )

            session.record_tool_result(
                name,
                result
            )

            function_results.append(
                {
                    "type": "function_result",
                    "call_id": call.call_id,
                    "result": str(result),
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
                ),
            )

            previous_interaction_id = (
                interaction.id
            )

        except Exception as error:

            return (
                "The tool execution completed, "
                f"but Gemini could not continue. "
                f"Reason: {error}"
            )

    return (
        "I reached the maximum number of tool "
        "steps for this request."
    )


# =========================================================
# INITIALIZE TASK ENGINE
# =========================================================


def initialize_task_engine():

    global task_engine

    task_engine = AutonomousTaskEngine(
        tool_executor=execute_tool,
        max_retries=1,
        stop_on_failure=True,
    )

    print(
        "Autonomous Task Engine: Enabled"
    )


# =========================================================
# STARTUP
# =========================================================


def startup():

    print()
    print("=" * 60)
    print("LEO 2.5F - Autonomous AI Voice Agent")
    print("=" * 60)
    print()
    print("Gemini: Connected")
    print("Voice recognition: Enabled")
    print("Desktop control: Enabled")
    print("Application control: Enabled")
    print("Clipboard: Enabled")
    print("Media control: Enabled")
    print("Reminders: Enabled")
    print("Timers: Enabled")
    print("Alarms: Enabled")
    print("Memory: Enabled")
    print("Smart session context: Enabled")
    print("Persistent history: Enabled")
    print("Preferences: Enabled")
    print("Autonomous Task Engine: Enabled")
    print()
    print("=" * 60)
    print()

    initialize_task_engine()


# =========================================================
# MAIN
# =========================================================


def main():

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

        while True:

            user_text = listen()

            if not user_text:
                continue

            normalized = normalize_text(
                user_text
            )

            # =============================================
            # EXIT
            # =============================================

            if is_exit_command(user_text):

                speak(
                    "Goodbye."
                )

                break

            # =============================================
            # CLEAR CONTEXT
            # =============================================

            if is_clear_context_command(
                user_text
            ):

                session.clear()

                global previous_interaction_id

                previous_interaction_id = None

                speak(
                    "Conversation context cleared."
                )

                continue

            # =============================================
            # TASK STATUS
            # =============================================

            if is_task_status_command(
                user_text
            ):

                response = (
                    get_task_status_response()
                )

                speak(response)

                continue

            # =============================================
            # TASK CANCELLATION
            # =============================================

            if is_task_cancel_command(
                user_text
            ):

                response = (
                    cancel_current_task()
                )

                speak(response)

                continue

            # =============================================
            # RECORD USER MESSAGE
            # =============================================

            session.record_user_message(
                user_text
            )

            try:

                from conversation_history import (
                    add_message
                )

                add_message(
                    "user",
                    user_text
                )

            except Exception:

                pass

            # =============================================
            # AUTONOMOUS TASK
            # =============================================

            if looks_like_autonomous_task(
                user_text
            ):

                response = (
                    run_autonomous_task(
                        user_text
                    )
                )

            else:

                # =========================================
                # NORMAL GEMINI REQUEST
                # =========================================

                response = ask_ai(
                    user_text
                )

            # =============================================
            # SAVE RESPONSE
            # =============================================

            try:

                from conversation_history import (
                    add_message
                )

                add_message(
                    "assistant",
                    response
                )

            except Exception:

                pass

            # =============================================
            # SPEAK RESPONSE
            # =============================================

            speak(response)

    except KeyboardInterrupt:

        print(
            "\nLEO stopped by user."
        )

    finally:

        print(
            "\nStopping background monitors..."
        )

        reminder_monitor.stop()
        timer_monitor.stop()
        alarm_monitor.stop()

        print(
            "LEO shutdown complete."
        )


# =========================================================
# ENTRY POINT
# =========================================================

if __name__ == "__main__":

    main()
