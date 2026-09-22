import json
import os

from datetime import datetime


# ============================================================
# CONFIGURATION
# ============================================================

HISTORY_FILE = "conversation_history.json"

MAX_HISTORY = 100


# ============================================================
# LOAD HISTORY
# ============================================================

def load_history():

    if not os.path.exists(
        HISTORY_FILE
    ):

        return []

    try:

        with open(
            HISTORY_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

        if isinstance(data, list):

            return data

        return []

    except Exception:

        return []


# ============================================================
# SAVE HISTORY
# ============================================================

def save_history(history):

    with open(
        HISTORY_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            history,
            file,
            indent=4,
            ensure_ascii=False
        )


# ============================================================
# ADD MESSAGE
# ============================================================

def add_message(
    role,
    content
):

    history = load_history()

    message = {

        "timestamp": datetime.now().isoformat(
            timespec="seconds"
        ),

        "role": role,

        "content": content
    }

    history.append(
        message
    )

    if len(history) > MAX_HISTORY:

        history = history[
            -MAX_HISTORY:
        ]

    save_history(
        history
    )


# ============================================================
# GET RECENT HISTORY
# ============================================================

def get_recent_history(
    count=10
):

    history = load_history()

    return history[
        -count:
    ]


# ============================================================
# CLEAR HISTORY
# ============================================================

def clear_history():

    save_history([])

    return (
        "Conversation history "
        "has been cleared."
    )


# ============================================================
# FORMAT HISTORY
# ============================================================

def format_recent_history(
    count=10
):

    history = get_recent_history(
        count
    )

    if not history:

        return "There is no conversation history."

    result = ""

    for item in history:

        role = item.get(
            "role",
            "unknown"
        )

        content = item.get(
            "content",
            ""
        )

        result += (
            f"{role}: {content}\n"
        )

    return result
