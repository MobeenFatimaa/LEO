# =========================================================
# LEO - Persistent User Preferences
# =========================================================

import json

from pathlib import Path


PREFERENCES_FILE = Path(
    "preferences.json"
)


# =========================================================
# STORAGE
# =========================================================

def load_preferences():

    if not PREFERENCES_FILE.exists():

        return {}

    try:

        with open(
            PREFERENCES_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    except Exception:

        return {}


def save_preferences(
    preferences
):

    with open(
        PREFERENCES_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            preferences,
            file,
            indent=4
        )


# =========================================================
# SET
# =========================================================

def set_preference(
    key,
    value
):

    if not key:

        return "Preference name cannot be empty."

    preferences = load_preferences()

    preferences[
        str(key).strip()
    ] = str(value)

    save_preferences(
        preferences
    )

    return (
        f"Preference '{key}' has been saved."
    )


# =========================================================
# GET
# =========================================================

def get_preference(key):

    if not key:

        return "No preference name was provided."

    preferences = load_preferences()

    if key not in preferences:

        return (
            f"No preference named '{key}' was found."
        )

    return preferences[key]


# =========================================================
# GET ALL
# =========================================================

def get_all_preferences():

    preferences = load_preferences()

    if not preferences:

        return "There are no saved preferences."

    lines = []

    for key, value in preferences.items():

        lines.append(
            f"{key}: {value}"
        )

    return "\n".join(lines)


# =========================================================
# RESET
# =========================================================

def reset_preferences():

    save_preferences({})

    return "All preferences have been reset."
