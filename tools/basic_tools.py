import os
import webbrowser
import subprocess
import requests
import pyautogui

from datetime import datetime


# ============================================================
# WEBSITE TOOL
# ============================================================

def open_website(website):

    websites = {
        "google": "https://www.google.com",
        "youtube": "https://www.youtube.com",
        "linkedin": "https://www.linkedin.com",
        "facebook": "https://www.facebook.com",
        "github": "https://github.com",
        "gmail": "https://mail.google.com",
        "kaggle": "https://www.kaggle.com",
        "chatgpt": "https://chatgpt.com",
        "gemini": "https://gemini.google.com"
    }

    website = website.lower().strip()

    if website not in websites:

        return (
            f"I don't have a supported shortcut for {website}. "
            "Supported websites include Google, YouTube, LinkedIn, "
            "Facebook, GitHub, Gmail, Kaggle, ChatGPT, and Gemini."
        )

    webbrowser.open(
        websites[website]
    )

    return f"Opening {website}."


# ============================================================
# APPLICATION TOOL
# ============================================================

def open_application(application):

    application = application.lower().strip()

    applications = {

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

        "task manager": "taskmgr"
    }

    if application not in applications:

        return (
            f"I don't have a configured launcher for {application}. "
            "Supported applications include Chrome, Notepad, "
            "Calculator, Paint, Command Prompt, PowerShell, "
            "File Explorer, and Task Manager."
        )

    try:

        subprocess.Popen(
            applications[application],
            shell=True
        )

        return f"Opening {application}."

    except Exception as e:

        return (
            f"I couldn't open {application}. "
            f"Error: {str(e)}"
        )


# ============================================================
# VS CODE
# ============================================================

def open_vscode():

    try:

        subprocess.Popen(
            "code",
            shell=True
        )

        return "Opening Visual Studio Code."

    except Exception as e:

        return (
            "I couldn't open Visual Studio Code. "
            f"Error: {str(e)}"
        )


# ============================================================
# FOLDER TOOL
# ============================================================

def open_folder(folder):

    folder = folder.lower().strip()

    user_home = os.path.expanduser("~")

    folders = {

        "desktop": os.path.join(
            user_home,
            "Desktop"
        ),

        "documents": os.path.join(
            user_home,
            "Documents"
        ),

        "downloads": os.path.join(
            user_home,
            "Downloads"
        ),

        "pictures": os.path.join(
            user_home,
            "Pictures"
        ),

        "videos": os.path.join(
            user_home,
            "Videos"
        ),

        "music": os.path.join(
            user_home,
            "Music"
        )
    }

    if folder not in folders:

        return (
            f"I don't have a configured path for {folder}. "
            "You can ask me to open Desktop, Documents, "
            "Downloads, Pictures, Videos, or Music."
        )

    path = folders[folder]

    if not os.path.exists(path):

        return (
            f"The {folder} folder does not exist "
            "on this computer."
        )

    try:

        subprocess.Popen(
            ["explorer", path]
        )

        return f"Opening your {folder} folder."

    except Exception as e:

        return (
            f"I couldn't open the {folder} folder. "
            f"Error: {str(e)}"
        )


# ============================================================
# TIME
# ============================================================

def get_time():

    now = datetime.now()

    return now.strftime(
        "The current time is %I:%M %p."
    )


# ============================================================
# DATE
# ============================================================

def get_date():

    now = datetime.now()

    return now.strftime(
        "Today is %A, %B %d, %Y."
    )


# ============================================================
# CALCULATOR
# ============================================================

def calculate(expression):

    try:

        allowed_characters = (
            "0123456789"
            "+-*/().% "
        )

        if not all(
            character in allowed_characters
            for character in expression
        ):

            return (
                "I can only calculate basic "
                "mathematical expressions."
            )

        result = eval(
            expression,
            {
                "__builtins__": {}
            },
            {}
        )

        return f"The answer is {result}."

    except Exception:

        return (
            "I couldn't calculate that expression."
        )


# ============================================================
# WEATHER DESCRIPTION
# ============================================================

def weather_description(code):

    descriptions = {

        0: "Clear sky",

        1: "Mainly clear",
        2: "Partly cloudy",
        3: "Overcast",

        45: "Fog",
        48: "Depositing rime fog",

        51: "Light drizzle",
        53: "Moderate drizzle",
        55: "Dense drizzle",

        56: "Light freezing drizzle",
        57: "Dense freezing drizzle",

        61: "Slight rain",
        63: "Moderate rain",
        65: "Heavy rain",

        66: "Light freezing rain",
        67: "Heavy freezing rain",

        71: "Slight snow",
        73: "Moderate snow",
        75: "Heavy snow",

        77: "Snow grains",

        80: "Slight rain showers",
        81: "Moderate rain showers",
        82: "Violent rain showers",

        85: "Slight snow showers",
        86: "Heavy snow showers",

        95: "Thunderstorm",
        96: "Thunderstorm with slight hail",
        99: "Thunderstorm with heavy hail"
    }

    return descriptions.get(
        code,
        "Unknown weather conditions"
    )


# ============================================================
# WEATHER
# ============================================================

def get_weather(location):

    try:

        geocode_url = (
            "https://geocoding-api.open-meteo.com/v1/search"
        )

        geocode_params = {

            "name": location,

            "count": 1,

            "language": "en",

            "format": "json"
        }

        geocode_response = requests.get(
            geocode_url,
            params=geocode_params,
            timeout=10
        )

        geocode_response.raise_for_status()

        geocode_data = (
            geocode_response.json()
        )

        if not geocode_data.get("results"):

            return (
                f"I couldn't find the location {location}."
            )

        place = geocode_data["results"][0]

        latitude = place["latitude"]

        longitude = place["longitude"]

        place_name = place.get(
            "name",
            location
        )

        country = place.get(
            "country",
            ""
        )

        weather_url = (
            "https://api.open-meteo.com/v1/forecast"
        )

        weather_params = {

            "latitude": latitude,

            "longitude": longitude,

            "current": (
                "temperature_2m,"
                "relative_humidity_2m,"
                "apparent_temperature,"
                "precipitation,"
                "weather_code,"
                "wind_speed_10m"
            ),

            "temperature_unit": "celsius",

            "wind_speed_unit": "kmh",

            "timezone": "auto"
        }

        weather_response = requests.get(
            weather_url,
            params=weather_params,
            timeout=10
        )

        weather_response.raise_for_status()

        weather_data = (
            weather_response.json()
        )

        current = weather_data["current"]

        temperature = (
            current["temperature_2m"]
        )

        humidity = (
            current["relative_humidity_2m"]
        )

        feels_like = (
            current["apparent_temperature"]
        )

        precipitation = (
            current["precipitation"]
        )

        weather_code = (
            current["weather_code"]
        )

        wind_speed = (
            current["wind_speed_10m"]
        )

        description = weather_description(
            weather_code
        )

        return (

            f"Current weather in "
            f"{place_name}, {country}: "

            f"{description}. "

            f"Temperature is "
            f"{temperature} degrees Celsius, "

            f"feels like "
            f"{feels_like} degrees, "

            f"humidity is "
            f"{humidity} percent, "

            f"wind speed is "
            f"{wind_speed} kilometers per hour, "

            f"and precipitation is "
            f"{precipitation} millimeters."
        )

    except requests.RequestException:

        return (
            "I couldn't connect to "
            "the weather service."
        )

    except Exception as e:

        return (
            f"I couldn't get the weather. "
            f"Error: {str(e)}"
        )


# ============================================================
# SCREENSHOT TOOL
# ============================================================

def take_screenshot():

    try:

        screenshots_folder = os.path.join(
            os.path.expanduser("~"),
            "Pictures",
            "LEO Screenshots"
        )

        os.makedirs(
            screenshots_folder,
            exist_ok=True
        )

        timestamp = datetime.now().strftime(
            "%Y-%m-%d_%H-%M-%S"
        )

        filename = (
            f"LEO_Screenshot_{timestamp}.png"
        )

        filepath = os.path.join(
            screenshots_folder,
            filename
        )

        screenshot = pyautogui.screenshot()

        screenshot.save(
            filepath
        )

        return (
            f"Screenshot saved successfully "
            f"at {filepath}."
        )

    except Exception as e:

        return (
            f"I couldn't take a screenshot. "
            f"Error: {str(e)}"
        )


# ============================================================
# SYSTEM INFORMATION
# ============================================================

def get_system_info():

    try:

        import platform
        import psutil

        system = platform.system()

        release = platform.release()

        version = platform.version()

        processor = platform.processor()

        memory = psutil.virtual_memory()

        memory_used = round(
            memory.used / (1024 ** 3),
            2
        )

        memory_total = round(
            memory.total / (1024 ** 3),
            2
        )

        memory_percent = memory.percent

        return (

            f"System: {system}. "

            f"Windows version: {release}. "

            f"Processor: {processor}. "

            f"Memory usage: "
            f"{memory_used} GB of "
            f"{memory_total} GB, "
            f"which is {memory_percent} percent."
        )

    except Exception as e:

        return (
            f"I couldn't retrieve system information. "
            f"Error: {str(e)}"
        )


# ============================================================
# BATTERY
# ============================================================

def get_battery_status():

    try:

        import psutil

        battery = psutil.sensors_battery()

        if battery is None:

            return (
                "I couldn't detect a battery "
                "on this computer."
            )

        percentage = battery.percent

        if battery.power_plugged:

            status = "and the charger is connected."

        else:

            status = "and the computer is running on battery."

        return (
            f"Battery is at {percentage} percent, "
            f"{status}"
        )

    except Exception as e:

        return (
            f"I couldn't check the battery. "
            f"Error: {str(e)}"
        )


# ============================================================
# VOLUME UP
# ============================================================

def volume_up():

    try:

        import pyautogui

        for _ in range(5):

            pyautogui.press(
                "volumeup"
            )

        return "Volume increased."

    except Exception as e:

        return (
            f"I couldn't increase the volume. "
            f"Error: {str(e)}"
        )


# ============================================================
# VOLUME DOWN
# ============================================================

def volume_down():

    try:

        import pyautogui

        for _ in range(5):

            pyautogui.press(
                "volumedown"
            )

        return "Volume decreased."

    except Exception as e:

        return (
            f"I couldn't decrease the volume. "
            f"Error: {str(e)}"
        )


# ============================================================
# MUTE
# ============================================================

def mute_volume():

    try:

        pyautogui.press(
            "volumemute"
        )

        return "Volume muted."

    except Exception as e:

        return (
            f"I couldn't mute the volume. "
            f"Error: {str(e)}"
        )


# ============================================================
# LOCK WINDOWS
# ============================================================

def lock_windows():

    try:

        subprocess.Popen(
            [
                "rundll32.exe",
                "user32.dll,LockWorkStation"
            ]
        )

        return "Locking Windows."

    except Exception as e:

        return (
            f"I couldn't lock Windows. "
            f"Error: {str(e)}"
        )


# ============================================================
# SEARCH FILES
# ============================================================

def search_files(filename):

    try:

        filename = filename.lower().strip()

        home = os.path.expanduser("~")

        results = []

        excluded_directories = {
            ".git",
            ".venv",
            "node_modules",
            "__pycache__"
        }

        for root, directories, files in os.walk(home):

            directories[:] = [
                directory
                for directory in directories
                if directory.lower()
                not in excluded_directories
            ]

            for file in files:

                if filename in file.lower():

                    full_path = os.path.join(
                        root,
                        file
                    )

                    results.append(
                        full_path
                    )

                    if len(results) >= 10:

                        break

            if len(results) >= 10:

                break

        if not results:

            return (
                f"I couldn't find a file "
                f"matching {filename}."
            )

        response = (
            f"I found {len(results)} matching files."
        )

        for result in results:

            response += (
                f"\n{result}"
            )

        return response

    except Exception as e:

        return (
            f"I couldn't search for the file. "
            f"Error: {str(e)}"
        )


# ============================================================
# CREATE NOTE
# ============================================================

def create_note(note):

    try:

        notes_folder = os.path.join(
            os.path.expanduser("~"),
            "Documents",
            "LEO Notes"
        )

        os.makedirs(
            notes_folder,
            exist_ok=True
        )

        timestamp = datetime.now().strftime(
            "%Y-%m-%d_%H-%M-%S"
        )

        filename = (
            f"note_{timestamp}.txt"
        )

        filepath = os.path.join(
            notes_folder,
            filename
        )

        with open(
            filepath,
            "w",
            encoding="utf-8"
        ) as file:

            file.write(note)

        return (
            f"Your note was saved at "
            f"{filepath}."
        )

    except Exception as e:

        return (
            f"I couldn't create the note. "
            f"Error: {str(e)}"
        )


# ============================================================
# READ TEXT FILE
# ============================================================

def read_text_file(filepath):

    try:

        filepath = os.path.expanduser(
            filepath
        )

        if not os.path.isfile(filepath):

            return (
                f"I couldn't find the file "
                f"{filepath}."
            )

        extension = os.path.splitext(
            filepath
        )[1].lower()

        if extension not in {
            ".txt",
            ".md",
            ".csv",
            ".log"
        }:

            return (
                "For safety, I can only read "
                "text, markdown, CSV, and log files."
            )

        with open(
            filepath,
            "r",
            encoding="utf-8"
        ) as file:

            content = file.read()

        if not content.strip():

            return "The file is empty."

        max_characters = 6000

        if len(content) > max_characters:

            content = content[
                :max_characters
            ]

            content += (
                "\nThe file was truncated "
                "because it was very large."
            )

        return (
            f"Contents of {filepath}:\n"
            f"{content}"
        )

    except Exception as e:

        return (
            f"I couldn't read the file. "
            f"Error: {str(e)}"
        )
