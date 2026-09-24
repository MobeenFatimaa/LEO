
# =========================================================
# LEO 2.5A
# Intelligent Task Planner
# =========================================================

import json
import os

from dotenv import load_dotenv
from google import genai


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
# AVAILABLE TOOLS
# =========================================================

AVAILABLE_TOOLS = {

    # -----------------------------------------------------
    # WEB
    # -----------------------------------------------------

    "open_website": {
        "description": "Open a website or URL.",
        "arguments": [
            "website"
        ]
    },

    "search_web": {
        "description": "Open a Google search for a query.",
        "arguments": [
            "query"
        ]
    },

    # -----------------------------------------------------
    # APPLICATIONS
    # -----------------------------------------------------

    "open_application": {
        "description": "Open a supported Windows application.",
        "arguments": [
            "application"
        ]
    },

    "close_application": {
        "description": "Close a supported Windows application.",
        "arguments": [
            "application"
        ]
    },

    "open_vscode": {
        "description": "Open Visual Studio Code.",
        "arguments": []
    },

    "open_folder": {
        "description": "Open a supported Windows folder.",
        "arguments": [
            "folder"
        ]
    },

    # -----------------------------------------------------
    # INFORMATION
    # -----------------------------------------------------

    "get_time": {
        "description": "Get the current local time.",
        "arguments": []
    },

    "get_date": {
        "description": "Get today's date.",
        "arguments": []
    },

    "calculate": {
        "description": "Calculate a mathematical expression.",
        "arguments": [
            "expression"
        ]
    },

    "get_weather": {
        "description": "Get current weather for a location.",
        "arguments": [
            "location"
        ]
    },

    # -----------------------------------------------------
    # SYSTEM
    # -----------------------------------------------------

    "take_screenshot": {
        "description": "Take a screenshot of the desktop.",
        "arguments": []
    },

    "get_system_info": {
        "description": "Get Windows system information.",
        "arguments": []
    },

    "get_battery_status": {
        "description": "Get battery information.",
        "arguments": []
    },

    # -----------------------------------------------------
    # VOLUME
    # -----------------------------------------------------

    "volume_up": {
        "description": "Increase Windows volume.",
        "arguments": []
    },

    "volume_down": {
        "description": "Decrease Windows volume.",
        "arguments": []
    },

    "mute_volume": {
        "description": "Toggle Windows mute.",
        "arguments": []
    },

    "set_volume_level": {
        "description": "Set Windows volume toward a percentage from 0 to 100.",
        "arguments": [
            "level"
        ]
    },

    # -----------------------------------------------------
    # MEDIA
    # -----------------------------------------------------

    "media_play_pause": {
        "description": "Play or pause media.",
        "arguments": []
    },

    "media_next": {
        "description": "Skip to the next media track.",
        "arguments": []
    },

    "media_previous": {
        "description": "Go to the previous media track.",
        "arguments": []
    },

    # -----------------------------------------------------
    # WINDOWS
    # -----------------------------------------------------

    "lock_windows": {
        "description": "Lock the Windows computer.",
        "arguments": []
    },

    # -----------------------------------------------------
    # FILES
    # -----------------------------------------------------

    "search_files": {
        "description": "Search for files by filename.",
        "arguments": [
            "filename"
        ]
    },

    "create_note": {
        "description": "Create a text note.",
        "arguments": [
            "note"
        ]
    },

    "read_text_file": {
        "description": "Read a TXT, MD, CSV or LOG file.",
        "arguments": [
            "filepath"
        ]
    },

    # -----------------------------------------------------
    # CLIPBOARD
    # -----------------------------------------------------

    "get_clipboard": {
        "description": "Read the current clipboard contents.",
        "arguments": []
    },

    "set_clipboard": {
        "description": "Put text into the clipboard.",
        "arguments": [
            "text"
        ]
    },

    # -----------------------------------------------------
    # REMINDERS
    # -----------------------------------------------------

    "create_reminder": {
        "description": "Create a future reminder.",
        "arguments": [
            "message",
            "reminder_time"
        ]
    },

    "list_reminders": {
        "description": "List reminders.",
        "arguments": []
    },

    "cancel_reminder": {
        "description": "Cancel a reminder by ID.",
        "arguments": [
            "reminder_id"
        ]
    },

    # -----------------------------------------------------
    # TIMERS
    # -----------------------------------------------------

    "create_timer": {
        "description": "Create a countdown timer.",
        "arguments": [
            "seconds",
            "message"
        ]
    },

    "list_timers": {
        "description": "List active timers.",
        "arguments": []
    },

    "cancel_timer": {
        "description": "Cancel a timer by ID.",
        "arguments": [
            "timer_id"
        ]
    },

    # -----------------------------------------------------
    # ALARMS
    # -----------------------------------------------------

    "create_alarm": {
        "description": "Create a daily repeating alarm.",
        "arguments": [
            "alarm_time",
            "message"
        ]
    },

    "list_alarms": {
        "description": "List active alarms.",
        "arguments": []
    },

    "cancel_alarm": {
        "description": "Cancel an alarm by ID.",
        "arguments": [
            "alarm_id"
        ]
    },

    # -----------------------------------------------------
    # MEMORY
    # -----------------------------------------------------

    "remember_fact": {
        "description": "Remember an explicit user fact.",
        "arguments": [
            "key",
            "value"
        ]
    },

    "forget_fact": {
        "description": "Forget a stored fact.",
        "arguments": [
            "key"
        ]
    },

    "get_memory": {
        "description": "Retrieve stored memory.",
        "arguments": []
    },

    # -----------------------------------------------------
    # PREFERENCES
    # -----------------------------------------------------

    "set_preference": {
        "description": "Set a persistent user preference.",
        "arguments": [
            "key",
            "value"
        ]
    },

    "get_preference": {
        "description": "Get a user preference.",
        "arguments": [
            "key"
        ]
    },

    "get_all_preferences": {
        "description": "Get all user preferences.",
        "arguments": []
    },

    "reset_preferences": {
        "description": "Reset user preferences.",
        "arguments": []
    },

    # -----------------------------------------------------
    # WORKFLOWS
    # -----------------------------------------------------

    "run_workflow": {
        "description": (
            "Run a predefined multi-step desktop workflow. "
            "Available workflows: coding, AI, research and study."
        ),
        "arguments": [
            "workflow"
        ]
    }
}


# =========================================================
# PLANNER SYSTEM INSTRUCTION
# =========================================================

PLANNER_INSTRUCTION = """
You are the planning engine for LEO, a Windows desktop
voice assistant.

Your job is to convert a user's request into a safe,
structured execution plan.

You are NOT the executor.

You only create the plan.

AVAILABLE TOOLS:

{tools}

PLANNING RULES:

1. Only use tools from the available tool list.

2. Never invent a tool.

3. Never create shell commands.

4. Never create PowerShell commands.

5. Never create CMD commands.

6. Never delete arbitrary files.

7. Never terminate arbitrary processes.

8. Use the minimum number of steps required.

9. If the user's request can be completed with one tool,
   create one step.

10. If the request requires multiple actions, create
    multiple sequential steps.

11. Each step must contain:
    - step
    - tool
    - arguments
    - description

12. Arguments must be valid JSON values.

13. Do not execute anything.

14. Do not explain the plan outside the JSON response.

15. Return ONLY valid JSON.

JSON FORMAT:

{
    "goal": "short description of the user's goal",
    "steps": [
        {
            "step": 1,
            "tool": "tool_name",
            "arguments": {},
            "description": "what this step does"
        }
    ]
}

If the request cannot be safely completed with the
available tools, return:

{
    "goal": "short description",
    "steps": [],
    "error": "reason"
}

IMPORTANT:

The plan must contain only tools from the provided
AVAILABLE TOOLS list.
"""


# =========================================================
# TOOL CATALOG
# =========================================================

def build_tool_catalog():

    lines = []

    for name, information in AVAILABLE_TOOLS.items():

        arguments = information["arguments"]

        if arguments:

            argument_text = ", ".join(
                arguments
            )

        else:

            argument_text = "none"

        lines.append(
            f"- {name}: "
            f"{information['description']} "
            f"Arguments: {argument_text}"
        )

    return "\n".join(
        lines
    )


# =========================================================
# JSON CLEANING
# =========================================================

def clean_json_response(text):

    if not text:

        return ""

    text = text.strip()

    # Remove markdown code fences if Gemini returns them.
    if text.startswith("```json"):

        text = text[
            len("```json"):
        ].strip()

    elif text.startswith("```"):

        text = text[
            len("```"):
        ].strip()

    if text.endswith("```"):

        text = text[
            :-3
        ].strip()

    return text


# =========================================================
# PLAN VALIDATION
# =========================================================

def validate_plan(plan):

    if not isinstance(
        plan,
        dict
    ):

        return (
            False,
            "Planner response is not a JSON object."
        )

    if "goal" not in plan:

        return (
            False,
            "Planner response is missing 'goal'."
        )

    if "steps" not in plan:

        return (
            False,
            "Planner response is missing 'steps'."
        )

    steps = plan["steps"]

    if not isinstance(
        steps,
        list
    ):

        return (
            False,
            "'steps' must be a list."
        )

    if "error" in plan and not steps:

        return (
            True,
            ""
        )

    for index, step in enumerate(
        steps,
        start=1
    ):

        if not isinstance(
            step,
            dict
        ):

            return (
                False,
                f"Step {index} is not an object."
            )

        required_fields = {
            "step",
            "tool",
            "arguments",
            "description"
        }

        missing_fields = (
            required_fields
            - set(step.keys())
        )

        if missing_fields:

            return (
                False,
                (
                    f"Step {index} is missing "
                    f"fields: "
                    f"{', '.join(missing_fields)}"
                )
            )

        tool_name = step["tool"]

        if tool_name not in AVAILABLE_TOOLS:

            return (
                False,
                (
                    f"Step {index} uses "
                    f"unsupported tool: "
                    f"{tool_name}"
                )
            )

        if not isinstance(
            step["arguments"],
            dict
        ):

            return (
                False,
                f"Arguments for step {index} must be an object."
            )

    return (
        True,
        ""
    )


# =========================================================
# CREATE PLAN
# =========================================================

def create_plan(
    user_request,
    context=""
):

    if not user_request:

        return {
            "goal": "",
            "steps": [],
            "error": "No user request was provided."
        }

    tool_catalog = build_tool_catalog()

    planner_prompt = f"""
AVAILABLE TOOLS:

{tool_catalog}

CURRENT CONTEXT:

{context}

USER REQUEST:

{user_request}

Create a safe execution plan.

Return ONLY valid JSON.
"""

    system_instruction = PLANNER_INSTRUCTION.format(
        tools=tool_catalog
    )

    try:

        interaction = client.interactions.create(

            model="gemini-3.8-flash",

            input=planner_prompt,

            system_instruction=system_instruction
        )

    except Exception as error:

        print(
            f"[PLANNER GEMINI ERROR] {error}"
        )

        return {
            "goal": user_request,
            "steps": [],
            "error": (
                "Planner could not connect to Gemini: "
                f"{error}"
            )
        }

    try:

        response_text = (
            interaction.output_text
            or ""
        )

    except Exception as error:

        print(
            f"[PLANNER OUTPUT ERROR] {error}"
        )

        return {
            "goal": user_request,
            "steps": [],
            "error": (
                "Planner could not read Gemini's response."
            )
        }

    response_text = clean_json_response(
        response_text
    )

    if not response_text:

        return {
            "goal": user_request,
            "steps": [],
            "error": "Planner returned an empty response."
        }

    try:

        plan = json.loads(
            response_text
        )

    except json.JSONDecodeError as error:

        print(
            f"[PLANNER JSON ERROR] {error}"
        )

        print(
            f"[PLANNER RAW RESPONSE] {response_text}"
        )

        return {
            "goal": user_request,
            "steps": [],
            "error": (
                "Planner returned invalid JSON."
            )
        }

    valid, error_message = validate_plan(
        plan
    )

    if not valid:

        print(
            f"[PLANNER VALIDATION ERROR] "
            f"{error_message}"
        )

        return {
            "goal": user_request,
            "steps": [],
            "error": error_message
        }

    return plan


# =========================================================
# DISPLAY PLAN
# =========================================================

def print_plan(plan):

    print()

    print(
        "=" * 60
    )

    print(
        "LEO TASK PLAN"
    )

    print(
        "=" * 60
    )

    print(
        f"Goal: {plan.get('goal', '')}"
    )

    if plan.get("error"):

        print(
            f"Error: {plan['error']}"
        )

        print(
            "=" * 60
        )

        return

    steps = plan.get(
        "steps",
        []
    )

    if not steps:

        print(
            "No steps were generated."
        )

    else:

        for step in steps:

            print(
                f"\nStep {step['step']}"
            )

            print(
                f"Tool: {step['tool']}"
            )

            print(
                f"Arguments: "
                f"{step['arguments']}"
            )

            print(
                f"Description: "
                f"{step['description']}"
            )

    print()

    print(
        "=" * 60
    )


# =========================================================
# TEST MODE
# =========================================================

if __name__ == "__main__":

    print()
    print(
        "=" * 60
    )
    print(
        "LEO 2.5A - Intelligent Task Planner"
    )
    print(
        "=" * 60
    )

    request = input(
        "\nEnter a task for LEO: "
    ).strip()

    if not request:

        print(
            "No task provided."
        )

    else:

        plan = create_plan(
            request
        )

        print_plan(
            plan
        )

