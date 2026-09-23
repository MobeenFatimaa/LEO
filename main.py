
# =========================================================
# LEO 2.0
# Advanced Desktop Control + Smart Context + Agent Workflows
# =========================================================

import os

import speech_recognition as sr
import pyttsx3

from dotenv import load_dotenv
from google import genai

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

from session_context import (
    SessionContext,
)

from agent_workflows import (
    run_workflow,
)


# =========================================================
# ENVIRONMENT
# =========================================================

load_dotenv()

GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY"
)

if not GEMINI_API_KEY:

    raise RuntimeError(
        "GEMINI_API_KEY was not found in .env"
    )


client = genai.Client(
    api_key=GEMINI_API_KEY
)


# =========================================================
# VOICE
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
# STATE
# =========================================================

previous_interaction_id = None

session = SessionContext()


# =========================================================
# SYSTEM INSTRUCTION
# =========================================================

SYSTEM_INSTRUCTION = """
You are LEO, a personal Windows desktop voice assistant.

Your job is to understand natural spoken language and
perform useful actions on the user's Windows computer.

You should behave like a conversational assistant.

IMPORTANT:

- Understand natural language.
- Do not require exact command wording.
- Use tools when the user requests an actual action.
- Never claim an action succeeded if the tool failed.
- Never invent tool results.
- Keep spoken responses concise.
- Use previous conversation context.
- Use current session context.
- Use Google Search for current web information.
- Ask for clarification when a requested action is ambiguous.

CONTEXT:

The user may say:

"open it"
"close it"
"search that"
"read that"
"what about tomorrow?"
"what about Lahore?"
"do it again"
"cancel that"
"show me that"
"remember this"

Use the provided context to understand references.

APPLICATIONS:

The user may ask you to open or close applications.

Use open_application or close_application.

Do not invent applications that are not supported.

WEBSITES:

Use open_website for direct websites.

Use search_web when the user wants a browser search.

For questions requiring current information, use Google Search.

MEDIA:

Use media_play_pause, media_next or media_previous
for media control.

VOLUME:

Use volume_up, volume_down, mute_volume or set_volume_level.

FILES:

Use search_files, read_text_file and create_note.

CLIPBOARD:

Use get_clipboard when the user explicitly asks about
their clipboard.

Use set_clipboard when the user asks you to put text
into the clipboard.

MEMORY:

Use remember_fact only when the user explicitly asks
you to remember something.

Use get_memory when the user asks what you remember.

Use forget_fact when requested.

REMINDERS:

Use create_reminder for calendar-like future reminders.

TIMERS:

Use create_timer for countdowns.

Examples:

"timer for 30 seconds"
"timer for 5 minutes"
"remind me in 2 hours"

Convert durations into seconds.

ALARMS:

Use create_alarm for daily repeating alarms.

Example:

"wake me at 7 AM"

Convert the time to 24-hour HH:MM format.

PREFERENCES:

Use preference tools for persistent preferences.

Examples:

"call me Mobeen"
"my default location is Rawalpindi"
"set my voice speed to 160"

WORKFLOWS:

You can perform predefined multi-step workflows.

If the user asks you to prepare a coding workspace,
use run_workflow with "coding".

Examples:

"prepare my coding workspace"
"set up my development workspace"
"open my coding environment"

If the user asks you to prepare an AI or machine
learning workspace, use run_workflow with "AI".

Examples:

"prepare my AI workspace"
"set up my machine learning workspace"
"open my AI environment"

If the user asks you to prepare a research workspace,
use run_workflow with "research".

Examples:

"prepare a research workspace"
"set up my research environment"

If the user asks you to prepare a study workspace,
use run_workflow with "study".

Examples:

"prepare my study workspace"
"set up my study environment"

A workflow performs several safe desktop actions
in sequence.

Do not claim that a workflow succeeded if its result
reports an error.

Do not invent workflow results.

SAFETY:

Do not execute arbitrary shell commands.

Do not delete arbitrary files.

Do not terminate arbitrary processes.

Only use supported tools.

Keep responses natural and concise.
"""


# =========================================================
# SPEECH
# =========================================================

def speak(text):

    if not text:

        return

    print(
        f"LEO: {text}"
    )

    try:

        engine.say(
            text
        )

        engine.runAndWait()

    except Exception as error:

        print(
            f"Speech error: {error}"
        )


# =========================================================
# LISTEN
# =========================================================

recognizer = sr.Recognizer()

recognizer.energy_threshold = 300

recognizer.dynamic_energy_threshold = True


def listen(
    timeout=10,
    phrase_time_limit=15
):

    try:

        with sr.Microphone() as source:

            print(
                "\nListening..."
            )

            recognizer.adjust_for_ambient_noise(
                source,
                duration=0.4
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

        if text:

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

    if not command:

        return ""

    command = command.strip()

    prefixes = [
        "hey leo",
        "okay leo",
        "ok leo",
        "leo",
    ]

    lower = command.lower()

    for prefix in prefixes:

        if lower.startswith(prefix):

            return command[
                len(prefix):
            ].strip()

    return command


# =========================================================
# EXIT / SPECIAL COMMANDS
# =========================================================

def is_exit_command(command):

    command = command.lower().strip()

    return command in {
        "exit",
        "quit",
        "goodbye",
        "shutdown leo",
        "shut down leo",
        "stop leo"
    }


def is_clear_context_command(command):

    command = command.lower().strip()

    return command in {
        "clear context",
        "forget this conversation",
        "reset context",
        "start fresh"
    }


# =========================================================
# REMINDER CALLBACK
# =========================================================

def reminder_callback(
    reminder_id,
    message
):

    print(
        f"\n[REMINDER] {message}"
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
        f"\n[TIMER] {message}"
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
        f"\n[ALARM] {message}"
    )

    speak(
        f"Alarm. {message}"
    )


# =========================================================
# TOOL DEFINITIONS
# =========================================================

TOOL_DEFINITIONS = [

    # -----------------------------------------------------
    # WEB
    # -----------------------------------------------------

    {
        "name": "open_website",
        "description": "Open a website or URL.",
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
        "name": "search_web",
        "description": "Open a Google browser search for a query.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string"
                }
            },
            "required": ["query"]
        }
    },

    # -----------------------------------------------------
    # APPLICATIONS
    # -----------------------------------------------------

    {
        "name": "open_application",
        "description": "Open a supported Windows application.",
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
        "name": "close_application",
        "description": "Close a supported Windows application.",
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
        "description": "Open a supported Windows folder.",
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

    # -----------------------------------------------------
    # TIME
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # CALCULATION
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # WEATHER
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # SYSTEM
    # -----------------------------------------------------

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
        "description": "Get battery information.",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    },

    # -----------------------------------------------------
    # VOLUME
    # -----------------------------------------------------

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
        "description": "Toggle Windows mute.",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    },

    {
        "name": "set_volume_level",
        "description": "Set Windows volume toward a percentage from 0 to 100.",
        "parameters": {
            "type": "object",
            "properties": {
                "level": {
                    "type": "integer"
                }
            },
            "required": ["level"]
        }
    },

    # -----------------------------------------------------
    # MEDIA
    # -----------------------------------------------------

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
        "description": "Skip to the next media track.",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    },

    {
        "name": "media_previous",
        "description": "Go to the previous media track.",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    },

    # -----------------------------------------------------
    # WINDOWS
    # -----------------------------------------------------

    {
        "name": "lock_windows",
        "description": "Lock the Windows computer.",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    },

    # -----------------------------------------------------
    # FILES
    # -----------------------------------------------------

    {
        "name": "search_files",
        "description": "Search for files by filename.",
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
        "description": "Read a TXT, MD, CSV or LOG file.",
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

    # -----------------------------------------------------
    # CLIPBOARD
    # -----------------------------------------------------

    {
        "name": "get_clipboard",
        "description": "Read the current clipboard contents.",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    },

    {
        "name": "set_clipboard",
        "description": "Put text into the clipboard.",
        "parameters": {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string"
                }
            },
            "required": ["text"]
        }
    },

    # -----------------------------------------------------
    # REMINDERS
    # -----------------------------------------------------

    {
        "name": "create_reminder",
        "description": "Create a reminder for YYYY-MM-DD HH:MM.",
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
        "description": "Cancel a reminder by ID.",
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

    # -----------------------------------------------------
    # TIMERS
    # -----------------------------------------------------

    {
        "name": "create_timer",
        "description": "Create a countdown timer in seconds.",
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
        "description": "List active timers.",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    },

    {
        "name": "cancel_timer",
        "description": "Cancel a timer by ID.",
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

    # -----------------------------------------------------
    # ALARMS
    # -----------------------------------------------------

    {
        "name": "create_alarm",
        "description": "Create a daily alarm using HH:MM.",
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
        "description": "Cancel an alarm by ID.",
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

    # -----------------------------------------------------
    # MEMORY
    # -----------------------------------------------------

    {
        "name": "remember_fact",
        "description": "Remember an explicit user fact.",
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

    # -----------------------------------------------------
    # HISTORY
    # -----------------------------------------------------

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
        "description": "Clear persistent conversation history.",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    },

    # -----------------------------------------------------
    # PREFERENCES
    # -----------------------------------------------------

    {
        "name": "set_preference",
        "description": "Set a persistent user preference.",
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
        "description": "Get all user preferences.",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    },

    {
        "name": "reset_preferences",
        "description": "Reset user preferences.",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    },

    # -----------------------------------------------------
    # AGENT WORKFLOWS
    # -----------------------------------------------------

    {
        "name": "run_workflow",
        "description": (
            "Run a predefined multi-step desktop workflow. "
            "Available workflows are coding, AI, research and study."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "workflow": {
                    "type": "string",
                    "description": (
                        "Workflow name such as coding, AI, "
                        "research or study."
                    )
                }
            },
            "required": ["workflow"]
        }
    }
]


# =========================================================
# GEMINI TOOL LIST
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

        # -------------------------------------------------
        # WEB
        # -------------------------------------------------

        if tool_name == "open_website":

            result = open_website(
                arguments.get("website")
            )

            session.set_website(
                arguments.get("website")
            )

            return result

        if tool_name == "search_web":

            return search_web(
                arguments.get("query")
            )

        # -------------------------------------------------
        # APPLICATIONS
        # -------------------------------------------------

        if tool_name == "open_application":

            application = arguments.get(
                "application"
            )

            result = open_application(
                application
            )

            session.set_application(
                application
            )

            return result

        if tool_name == "close_application":

            return close_application(
                arguments.get("application")
            )

        if tool_name == "open_vscode":

            session.set_application(
                "Visual Studio Code"
            )

            return open_vscode()

        if tool_name == "open_folder":

            folder = arguments.get(
                "folder"
            )

            result = open_folder(
                folder
            )

            return result

        # -------------------------------------------------
        # TIME
        # -------------------------------------------------

        if tool_name == "get_time":

            return get_time()

        if tool_name == "get_date":

            return get_date()

        # -------------------------------------------------
        # CALCULATION
        # -------------------------------------------------

        if tool_name == "calculate":

            return calculate(
                arguments.get("expression")
            )

        # -------------------------------------------------
        # WEATHER
        # -------------------------------------------------

        if tool_name == "get_weather":

            location = arguments.get(
                "location"
            )

            session.set_location(
                location
            )

            return get_weather(
                location
            )

        # -------------------------------------------------
        # SYSTEM
        # -------------------------------------------------

        if tool_name == "take_screenshot":

            return take_screenshot()

        if tool_name == "get_system_info":

            return get_system_info()

        if tool_name == "get_battery_status":

            return get_battery_status()

        # -------------------------------------------------
        # VOLUME
        # -------------------------------------------------

        if tool_name == "volume_up":

            return volume_up()

        if tool_name == "volume_down":

            return volume_down()

        if tool_name == "mute_volume":

            return mute_volume()

        if tool_name == "set_volume_level":

            return set_volume_level(
                arguments.get("level")
            )

        # -------------------------------------------------
        # MEDIA
        # -------------------------------------------------

        if tool_name == "media_play_pause":

            return media_play_pause()

        if tool_name == "media_next":

            return media_next()

        if tool_name == "media_previous":

            return media_previous()

        # -------------------------------------------------
        # WINDOWS
        # -------------------------------------------------

        if tool_name == "lock_windows":

            return lock_windows()

        # -------------------------------------------------
        # FILES
        # -------------------------------------------------

        if tool_name == "search_files":

            return search_files(
                arguments.get("filename")
            )

        if tool_name == "create_note":

            return create_note(
                arguments.get("note")
            )

        if tool_name == "read_text_file":

            filepath = arguments.get(
                "filepath"
            )

            session.set_file(
                filepath
            )

            return read_text_file(
                filepath
            )

        # -------------------------------------------------
        # CLIPBOARD
        # -------------------------------------------------

        if tool_name == "get_clipboard":

            return get_clipboard()

        if tool_name == "set_clipboard":

            return set_clipboard(
                arguments.get("text")
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
        # HISTORY
        # -------------------------------------------------

        if tool_name == "get_recent_history":

            count = arguments.get(
                "count",
                8
            )

            return get_recent_history(
                count
            )

        if tool_name == "clear_history":

            clear_history()

            session.clear()

            return (
                "Conversation history and "
                "session context have been cleared."
            )

        # -------------------------------------------------
        # PREFERENCES
        # -------------------------------------------------

        if tool_name == "set_preference":

            return set_preference(
                arguments.get("key"),
                arguments.get("value")
            )

        if tool_name == "get_preference":

            value = get_preference(
                arguments.get("key")
            )

            return str(value)

        if tool_name == "get_all_preferences":

            return get_all_preferences()

        if tool_name == "reset_preferences":

            return reset_preferences()

        # -------------------------------------------------
        # AGENT WORKFLOWS
        # -------------------------------------------------

        if tool_name == "run_workflow":

            workflow = arguments.get(
                "workflow"
            )

            print(
                f"\n[WORKFLOW] {workflow}"
            )

            result = run_workflow(
                workflow
            )

            return result

        # -------------------------------------------------
        # UNKNOWN TOOL
        # -------------------------------------------------

        return (
            f"Unknown tool: {tool_name}"
        )

    except Exception as error:

        print(
            f"[TOOL ERROR] {tool_name}: {error}"
        )

        return (
            f"The tool '{tool_name}' failed. "
            f"Reason: {error}"
        )


# =========================================================
# GEMINI
# =========================================================

def ask_ai(user_message):

    global previous_interaction_id

    persistent_history = get_recent_history(
        8
    )

    active_context = session.get_context()

    recent_messages = session.get_recent_messages(
        6
    )

    enhanced_message = f"""
ACTIVE SESSION CONTEXT:

{active_context}

RECENT SESSION:

{recent_messages}

PERSISTENT CONVERSATION HISTORY:

{persistent_history}

CURRENT USER REQUEST:

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
                if previous_interaction_id
                else None
            )
        )

    except Exception as error:

        print(
            f"[GEMINI ERROR] {error}"
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
                f"[OUTPUT ERROR] {error}"
            )

        # -------------------------------------------------
        # NORMAL RESPONSE
        # -------------------------------------------------

        if not function_calls:

            try:

                response = (
                    interaction.output_text
                    or
                    "I'm ready."
                )

                session.add_assistant_message(
                    response
                )

                return response

            except Exception:

                return "I'm ready."

        # -------------------------------------------------
        # EXECUTE FUNCTION CALLS
        # -------------------------------------------------

        function_results = []

        for call in function_calls:

            tool_name = call.name

            arguments = (
                call.arguments
                if call.arguments
                else {}
            )

            print(
                f"\n[TOOL] {tool_name}"
            )

            print(
                f"[ARGUMENTS] {arguments}"
            )

            result = execute_tool(
                tool_name,
                arguments
            )

            session.set_tool_result(
                tool_name,
                result
            )

            print(
                f"[RESULT] {result}"
            )

            function_results.append(
                {
                    "type": "function_result",
                    "call_id": call.id,
                    "result": str(result)
                }
            )

        # -------------------------------------------------
        # CONTINUE GEMINI INTERACTION
        # -------------------------------------------------

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
                f"[GEMINI CONTINUATION ERROR] {error}"
            )

            return (
                "The requested action was attempted, "
                "but I couldn't finish processing it."
            )


# =========================================================
# STARTUP
# =========================================================

def startup():

    print()

    print(
        "=" * 70
    )

    print(
        "LEO 2.0 - Agentic Desktop Assistant"
    )

    print(
        "=" * 70
    )

    print(
        "Gemini: Connected"
    )

    print(
        "Voice recognition: Enabled"
    )

    print(
        "Desktop control: Enabled"
    )

    print(
        "Application control: Enabled"
    )

    print(
        "Clipboard: Enabled"
    )

    print(
        "Media control: Enabled"
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
        "Smart session context: Enabled"
    )

    print(
        "Persistent history: Enabled"
    )

    print(
        "Preferences: Enabled"
    )

    print(
        "Agent workflows: Enabled"
    )

    print(
        "=" * 70
    )

    print()


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

            command = listen()

            if not command:

                continue

            command = normalize_command(
                command
            )

            if not command:

                continue

            # ---------------------------------------------
            # EXIT
            # ---------------------------------------------

            if is_exit_command(
                command
            ):

                speak(
                    "Goodbye."
                )

                break

            # ---------------------------------------------
            # CLEAR CURRENT CONTEXT
            # ---------------------------------------------

            if is_clear_context_command(
                command
            ):

                session.clear()

                speak(
                    "Current session context cleared."
                )

                continue

            # ---------------------------------------------
            # SAVE USER MESSAGE
            # ---------------------------------------------

            session.add_user_message(
                command
            )

            add_message(
                "user",
                command
            )

            # ---------------------------------------------
            # ASK GEMINI
            # ---------------------------------------------

            response = ask_ai(
                command
            )

            # ---------------------------------------------
            # PERSIST RESPONSE
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
            "\nLEO stopped by keyboard."
        )

    except Exception as error:

        print(
            f"\nUnexpected error: {error}"
        )

    finally:

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

