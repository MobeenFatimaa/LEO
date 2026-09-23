# =========================================================
# LEO - Basic Windows Tools
# =========================================================

import os
import platform
import subprocess
import webbrowser

from datetime import datetime
from pathlib import Path
from urllib.parse import quote_plus

import psutil
import pyautogui
import requests


# =========================================================
# WEBSITE TOOLS
# =========================================================

WEBSITES = {
    "google": "https://www.google.com",
    "youtube": "https://www.youtube.com",
    "linkedin": "https://www.linkedin.com",
    "facebook": "https://www.facebook.com",
    "github": "https://github.com",
    "gmail": "https://mail.google.com",
    "kaggle": "https://www.kaggle.com",
    "chatgpt": "https://chatgpt.com",
    "gemini": "https://gemini.google.com",
    "stackoverflow": "https://stackoverflow.com",
    "reddit": "https://www.reddit.com",
    "wikipedia": "https://www.wikipedia.org",
}


def open_website(website):

    if not website:

        return "No website was provided."

    website = website.strip()

    key = website.lower()

    if key in WEBSITES:

        url = WEBSITES[key]

    elif website.startswith(
        ("http://", "https://")
    ):

        url = website

    else:

        url = (
            "https://www.google.com/search?q="
            + quote_plus(website)
        )

    try:

        webbrowser.open(url)

        return (
            f"Opened {website} in the browser."
        )

    except Exception as error:

        return (
            f"Could not open website: {error}"
        )


def search_web(query):

    if not query:

        return "No search query was provided."

    url = (
        "https://www.google.com/search?q="
        + quote_plus(query)
    )

    try:

        webbrowser.open(url)

        return (
            f"Opened Google search for {query}."
        )

    except Exception as error:

        return (
            f"Could not perform search: {error}"
        )


# =========================================================
# WINDOWS APPLICATIONS
# =========================================================

APPLICATIONS = {
    "chrome": "chrome",
    "google chrome": "chrome",

    "notepad": "notepad",

    "calculator": "calc",
    "calc": "calc",

    "paint": "mspaint",

    "command prompt": "cmd",
    "cmd": "cmd",

    "powershell": "powershell",

    "file explorer": "explorer",
    "explorer": "explorer",

    "task manager": "taskmgr",

    "wordpad": "write",

    "control panel": "control",

    "settings": "ms-settings:",
}


def open_application(application):

    if not application:

        return "No application was specified."

    application = application.strip()

    key = application.lower()

    executable = APPLICATIONS.get(key)

    if executable is None:

        return (
            f"I don't have '{application}' "
            "in my safe application list."
        )

    try:

        subprocess.Popen(
            executable,
            shell=True
        )

        return (
            f"Opened {application}."
        )

    except Exception as error:

        return (
            f"Could not open {application}: {error}"
        )


def close_application(application):

    if not application:

        return "No application was specified."

    application = application.strip()

    key = application.lower()

    process_map = {
        "chrome": ["chrome.exe"],
        "google chrome": ["chrome.exe"],
        "notepad": ["notepad.exe"],
        "calculator": ["CalculatorApp.exe", "calc.exe"],
        "calc": ["CalculatorApp.exe", "calc.exe"],
        "paint": ["mspaint.exe"],
        "wordpad": ["wordpad.exe"],
        "command prompt": ["cmd.exe"],
        "cmd": ["cmd.exe"],
        "powershell": ["powershell.exe"],
        "task manager": ["Taskmgr.exe"],
    }

    processes = process_map.get(key)

    if not processes:

        return (
            f"I cannot safely close '{application}' "
            "because it is not in my application list."
        )

    closed = False

    for process_name in processes:

        try:

            result = subprocess.run(
                [
                    "taskkill",
                    "/IM",
                    process_name,
                    "/F"
                ],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:

                closed = True

        except Exception:

            pass

    if closed:

        return (
            f"Closed {application}."
        )

    return (
        f"{application} does not appear to be running."
    )


def open_vscode():

    try:

        subprocess.Popen(
            "code",
            shell=True
        )

        return "Opened Visual Studio Code."

    except Exception as error:

        return (
            f"Could not open Visual Studio Code: {error}"
        )


# =========================================================
# FOLDERS
# =========================================================

def open_folder(folder):

    if not folder:

        return "No folder was specified."

    folder = folder.strip()

    home = Path.home()

    folders = {
        "desktop": home / "Desktop",
        "documents": home / "Documents",
        "downloads": home / "Downloads",
        "pictures": home / "Pictures",
        "videos": home / "Videos",
        "music": home / "Music",
    }

    key = folder.lower()

    path = folders.get(key)

    if path is None:

        path = Path(folder)

    if not path.exists():

        return (
            f"I couldn't find the folder {folder}."
        )

    try:

        os.startfile(str(path))

        return (
            f"Opened {folder}."
        )

    except Exception as error:

        return (
            f"Could not open folder: {error}"
        )


# =========================================================
# TIME / DATE
# =========================================================

def get_time():

    return datetime.now().strftime(
        "%I:%M %p"
    )


def get_date():

    return datetime.now().strftime(
        "%A, %B %d, %Y"
    )


# =========================================================
# CALCULATOR
# =========================================================

def calculate(expression):

    if not expression:

        return "No expression was provided."

    allowed = (
        "0123456789"
        "+-*/().% "
    )

    if not all(
        character in allowed
        for character in expression
    ):

        return (
            "The expression contains "
            "unsupported characters."
        )

    try:

        result = eval(
            expression,
            {
                "__builtins__": {}
            },
            {}
        )

        return (
            f"The answer is {result}."
        )

    except Exception as error:

        return (
            f"Could not calculate the expression: {error}"
        )


# =========================================================
# WEATHER
# =========================================================

def weather_description(code):

    descriptions = {
        0: "clear sky",
        1: "mainly clear",
        2: "partly cloudy",
        3: "overcast",
        45: "foggy",
        48: "depositing rime fog",
        51: "light drizzle",
        53: "moderate drizzle",
        55: "dense drizzle",
        61: "slight rain",
        63: "moderate rain",
        65: "heavy rain",
        71: "slight snow",
        73: "moderate snow",
        75: "heavy snow",
        80: "slight rain showers",
        81: "moderate rain showers",
        82: "violent rain showers",
        95: "thunderstorm",
        96: "thunderstorm with slight hail",
        99: "thunderstorm with heavy hail",
    }

    return descriptions.get(
        code,
        "unknown weather"
    )


def get_weather(location):

    if not location:

        return "Please provide a location."

    try:

        geo_response = requests.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={
                "name": location,
                "count": 1,
                "language": "en",
                "format": "json"
            },
            timeout=10
        )

        geo_response.raise_for_status()

        geo_data = geo_response.json()

        results = geo_data.get(
            "results",
            []
        )

        if not results:

            return (
                f"I couldn't find {location}."
            )

        place = results[0]

        latitude = place["latitude"]
        longitude = place["longitude"]

        name = place.get(
            "name",
            location
        )

        country = place.get(
            "country",
            ""
        )

        weather_response = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": latitude,
                "longitude": longitude,
                "current": (
                    "temperature_2m,"
                    "relative_humidity_2m,"
                    "apparent_temperature,"
                    "weather_code,"
                    "wind_speed_10m"
                ),
                "timezone": "auto"
            },
            timeout=10
        )

        weather_response.raise_for_status()

        weather_data = weather_response.json()

        current = weather_data.get(
            "current",
            {}
        )

        temperature = current.get(
            "temperature_2m"
        )

        feels_like = current.get(
            "apparent_temperature"
        )

        humidity = current.get(
            "relative_humidity_2m"
        )

        wind = current.get(
            "wind_speed_10m"
        )

        code = current.get(
            "weather_code"
        )

        description = weather_description(
            code
        )

        return (
            f"Weather in {name}, {country}: "
            f"{temperature}°C, {description}. "
            f"It feels like {feels_like}°C. "
            f"Humidity is {humidity} percent. "
            f"Wind speed is {wind} km/h."
        )

    except Exception as error:

        return (
            f"Could not retrieve weather: {error}"
        )


# =========================================================
# SCREENSHOT
# =========================================================

def take_screenshot():

    try:

        screenshot = pyautogui.screenshot()

        directory = (
            Path.home()
            / "Pictures"
            / "LEO Screenshots"
        )

        directory.mkdir(
            parents=True,
            exist_ok=True
        )

        filename = (
            datetime.now().strftime(
                "screenshot_%Y%m%d_%H%M%S.png"
            )
        )

        filepath = (
            directory / filename
        )

        screenshot.save(
            filepath
        )

        return (
            f"Screenshot saved to {filepath}"
        )

    except Exception as error:

        return (
            f"Could not take screenshot: {error}"
        )


# =========================================================
# SYSTEM INFORMATION
# =========================================================

def get_system_info():

    try:

        return (
            f"System: {platform.system()} "
            f"{platform.release()}\n"
            f"Version: {platform.version()}\n"
            f"Machine: {platform.machine()}\n"
            f"Processor: {platform.processor()}\n"
            f"Python: {platform.python_version()}"
        )

    except Exception as error:

        return (
            f"Could not retrieve system information: {error}"
        )


def get_battery_status():

    try:

        battery = psutil.sensors_battery()

        if battery is None:

            return (
                "Battery information is not available."
            )

        percentage = battery.percent

        if battery.power_plugged:

            state = "charging"

        else:

            state = "not charging"

        return (
            f"Battery is at {percentage} percent "
            f"and is {state}."
        )

    except Exception as error:

        return (
            f"Could not retrieve battery status: {error}"
        )


# =========================================================
# VOLUME
# =========================================================

def volume_up():

    try:

        pyautogui.press(
            "volumeup"
        )

        return "Volume increased."

    except Exception as error:

        return (
            f"Could not increase volume: {error}"
        )


def volume_down():

    try:

        pyautogui.press(
            "volumedown"
        )

        return "Volume decreased."

    except Exception as error:

        return (
            f"Could not decrease volume: {error}"
        )


def mute_volume():

    try:

        pyautogui.press(
            "volumemute"
        )

        return "Volume muted or unmuted."

    except Exception as error:

        return (
            f"Could not toggle mute: {error}"
        )


def set_volume_level(level):

    try:

        level = int(level)

    except (TypeError, ValueError):

        return "Volume must be a number."

    if level < 0 or level > 100:

        return (
            "Volume must be between 0 and 100."
        )

    try:

        # Windows does not expose a simple universal
        # built-in percentage command through pyautogui.
        # We normalize by first muting and then using
        # volume-up presses.

        pyautogui.press(
            "volumedown",
            presses=50,
            interval=0.01
        )

        presses = round(
            level / 2
        )

        pyautogui.press(
            "volumeup",
            presses=presses,
            interval=0.01
        )

        return (
            f"Volume adjusted toward {level} percent."
        )

    except Exception as error:

        return (
            f"Could not set volume: {error}"
        )


# =========================================================
# MEDIA
# =========================================================

def media_play_pause():

    try:

        pyautogui.press(
            "playpause"
        )

        return (
            "Media play/pause command sent."
        )

    except Exception as error:

        return (
            f"Could not control media: {error}"
        )


def media_next():

    try:

        pyautogui.press(
            "nexttrack"
        )

        return "Skipped to the next track."

    except Exception as error:

        return (
            f"Could not skip track: {error}"
        )


def media_previous():

    try:

        pyautogui.press(
            "prevtrack"
        )

        return "Went to the previous track."

    except Exception as error:

        return (
            f"Could not go to previous track: {error}"
        )


# =========================================================
# WINDOWS LOCK
# =========================================================

def lock_windows():

    try:

        subprocess.run(
            [
                "rundll32.exe",
                "user32.dll,LockWorkStation"
            ],
            check=False
        )

        return "Windows has been locked."

    except Exception as error:

        return (
            f"Could not lock Windows: {error}"
        )


# =========================================================
# FILE SEARCH
# =========================================================

def search_files(filename):

    if not filename:

        return "Please provide a filename."

    filename = filename.lower()

    home = Path.home()

    excluded = {
        ".git",
        ".venv",
        "node_modules",
        "__pycache__",
        "AppData"
    }

    matches = []

    try:

        for root, dirs, files in os.walk(
            home
        ):

            dirs[:] = [
                directory
                for directory in dirs
                if directory not in excluded
            ]

            for file in files:

                if filename in file.lower():

                    matches.append(
                        os.path.join(
                            root,
                            file
                        )
                    )

                    if len(matches) >= 10:

                        return "\n".join(
                            matches
                        )

    except Exception as error:

        return (
            f"File search failed: {error}"
        )

    if not matches:

        return (
            f"No files matching '{filename}' were found."
        )

    return "\n".join(
        matches
    )


# =========================================================
# NOTES
# =========================================================

def create_note(note):

    if not note:

        return "The note is empty."

    try:

        directory = (
            Path.home()
            / "Documents"
            / "LEO Notes"
        )

        directory.mkdir(
            parents=True,
            exist_ok=True
        )

        filename = (
            datetime.now().strftime(
                "note_%Y%m%d_%H%M%S.txt"
            )
        )

        filepath = (
            directory / filename
        )

        with open(
            filepath,
            "w",
            encoding="utf-8"
        ) as file:

            file.write(note)

        return (
            f"Note created at {filepath}"
        )

    except Exception as error:

        return (
            f"Could not create note: {error}"
        )


# =========================================================
# TEXT FILE READER
# =========================================================

def read_text_file(filepath):

    if not filepath:

        return "No file path was provided."

    allowed_extensions = {
        ".txt",
        ".md",
        ".csv",
        ".log"
    }

    path = Path(filepath)

    if path.suffix.lower() not in allowed_extensions:

        return (
            "For safety, LEO can only read "
            "TXT, MD, CSV and LOG files."
        )

    if not path.exists():

        return (
            f"File not found: {filepath}"
        )

    try:

        with open(
            path,
            "r",
            encoding="utf-8",
            errors="ignore"
        ) as file:

            content = file.read(
                8000
            )

        return content

    except Exception as error:

        return (
            f"Could not read file: {error}"
        )


# =========================================================
# CLIPBOARD
# =========================================================

def get_clipboard():

    try:

        content = pyperclip.paste()

        if not content:

            return "The clipboard is empty."

        return (
            f"Clipboard contents:\n{content[:5000]}"
        )

    except Exception as error:

        return (
            f"Could not read clipboard: {error}"
        )


def set_clipboard(text):

    try:

        pyperclip.copy(
            str(text)
        )

        return (
            "The clipboard has been updated."
        )

    except Exception as error:

        return (
            f"Could not update clipboard: {error}"
        )
