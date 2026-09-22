import json
import os


PREFERENCES_FILE = "preferences.json"


DEFAULT_PREFERENCES = {
    "name": "User",
    "assistant_name": "LEO",
    "default_location": "",
    "voice_speed": 175,
    "continuous_mode": True
}


def load_preferences():

    if not os.path.exists(PREFERENCES_FILE):

        save_preferences(DEFAULT_PREFERENCES.copy())

        return DEFAULT_PREFERENCES.copy()

    try:

        with open(
            PREFERENCES_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            preferences = json.load(file)

        merged = DEFAULT_PREFERENCES.copy()
        merged.update(preferences)

        return merged

    except (json.JSONDecodeError, OSError):

        return DEFAULT_PREFERENCES.copy()


def save_preferences(preferences):

    try:

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

        return True

    except OSError:

        return False


def set_preference(key, value):

    preferences = load_preferences()

    preferences[key] = value

    save_preferences(preferences)

    return (
        f"Preference '{key}' has been set to '{value}'."
    )


def get_preference(key):

    preferences = load_preferences()

    return preferences.get(key)


def get_all_preferences():

    preferences = load_preferences()

    lines = []

    for key, value in preferences.items():

        lines.append(
            f"{key}: {value}"
        )

    return "\n".join(lines)


def reset_preferences():

    save_preferences(
        DEFAULT_PREFERENCES.copy()
    )

    return "Preferences have been reset."
