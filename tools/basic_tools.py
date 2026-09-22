import os
import webbrowser
import subprocess
import requests
import pyautogui

from datetime import datetime


# ============================================================
# WEBSITE
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
            f"I don't have a supported shortcut "
            f"for {website}."
        )

    webbrowser.open(
        websites[website]
    )

    return f"Opening {website}."


# ============================================================
# APPLICATION
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
            f"I don't have a configured launcher "
            f"for {application}."
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

        return (
            "Opening Visual Studio Code."
        )

    except Exception as e:

        return (
            "I couldn't open Visual Studio Code. "
            f"Error: {str(e)}"
        )


# ============================================================
# FOLDERS
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
            f"I don't have a configured path "
            f"for {folder}."
        )

    path = folders[folder]

    if not os.path.exists(path):

        return (
            f"The {folder} folder does not exist."
        )

    try:

        subprocess.Popen(
            [
                "explorer",
                path
            ]
        )

        return (
            f"Opening your {folder} folder."
        )

    except Exception as e:

        return (
            f"I couldn't open the folder. "
            f"Error: {str(e)}"
        )


# ============================================================
# TIME
# ============================================================

def get_time():

    return datetime.now().strftime(
        "The current time is %I:%M %p."
    )


# ============================================================
# DATE
# ============================================================

def get_date():

    return datetime.now().strftime(
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
                "I can only calculate "
                "basic mathematical expressions."
            )

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

        response = requests.get(

            geocode_url,

            params=geocode_params,

            timeout=10
        )

        response.raise_for_status()

        data = response.json()

        if not data.get("results"):

            return (
                f"I couldn't find {location}."
            )

        place = data["results"][0]

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

        weather = weather_response.json()

        current = weather["current"]

        temperature = current[
            "temperature_2m"
        ]

        humidity = current[
            "relative_humidity_2m"
        ]

        feels_like = current[
            "apparent_temperature"
        ]

        precipitation = current[
            "precipitation"
        ]

        weather_code = current[
            "weather_code"
        ]

        wind_speed = current[
            "wind_speed_10m"
        ]

        description = weather_description(
            weather_code
        )

        return (

            f"Current weather in "
            f"{name}, {country}: "

            f"{description}. "

            f"Temperature is "
            f"{temperature} degrees Celsius. "

            f"It feels like "
            f"{feels_like} degrees. "

            f"Humidity is "
            f"{humidity} percent. "

            f"Wind speed is "
            f"{wind_speed} kilometers per hour."
        )

    except Exception as e:

        return (
            f"I couldn't get the weather. "
            f"Error: {str(e)}"
        )


# ============================================================
# SCREENSHOT
# ============================================================

def take_screenshot():

    try:

        folder = os.path.join(

            os.path.expanduser("~"),

            "Pictures",

            "LEO Screenshots"
        )

        os.makedirs(
            folder,
            exist_ok=True
        )

        timestamp = datetime.now().strftime(
            "%Y-%m-%d_%H-%M-%S"
        )

        filename = (
            f"LEO_Screenshot_{timestamp}.png"
        )

        path = os.path.join(
            folder,
            filename
        )

        image = pyautogui.screenshot()

        image.save(
            path
        )

        return (
            f"Screenshot saved successfully "
            f"at {path}."
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

        processor = platform.processor()

        memory = psutil.virtual_memory()

        used = round(
            memory.used / (1024 ** 3),
            2
        )

        total = round(
            memory.total / (1024 ** 3),
            2
        )

        return (

            f"Operating system: "
            f"{system} {release}. "

            f"Processor: "
            f"{processor}. "

            f"Memory usage: "
            f"{used} GB of {total} GB, "

            f"which is {memory.percent} percent."
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
                "I couldn't detect a battery."
            )

        percentage = battery.percent

        if battery.power_plugged:

            status = (
                "the charger is connected."
            )

        else:

            status = (
                "the computer is running on battery."
            )

        return (

            f"Battery is at "
            f"{percentage} percent, "
            f"and {status}"
        )

    except Exception as e:

        return (
            f"I couldn't check the battery. "
            f"Error: {str(e)}"
        )


# ============================================================
# VOLUME
# ============================================================

def volume_up():

    try:

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


def volume_down():

    try:

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

        excluded = {

            ".git",

            ".venv",

            "node_modules",

            "__pycache__"
        }

        for root, directories, files in os.walk(
            home
        ):

            directories[:] = [

                directory

                for directory in directories

                if directory.lower()
                not in excluded
            ]

            for file in files:

                if filename in file.lower():

                    results.append(

                        os.path.join(
                            root,
                            file
                        )
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

        result = (
            f"I found {len(results)} matching files."
        )

        for path in results:

            result += (
                f"\n{path}"
            )

        return result

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

        folder = os.path.join(

            os.path.expanduser("~"),

            "Documents",

            "LEO Notes"
        )

        os.makedirs(
            folder,
            exist_ok=True
        )

        timestamp = datetime.now().strftime(
            "%Y-%m-%d_%H-%M-%S"
        )

        filename = (
            f"note_{timestamp}.txt"
        )

        path = os.path.join(
            folder,
            filename
        )

        with open(
            path,
            "w",
            encoding="utf-8"
        ) as file:

            file.write(note)

        return (
            f"Your note was saved at {path}."
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

        if not os.path.isfile(
            filepath
        ):

            return (
                f"I couldn't find {filepath}."
            )

        extension = os.path.splitext(
            filepath
        )[1].lower()

        allowed = {
            ".txt",
            ".md",
            ".csv",
            ".log"
        }

        if extension not in allowed:

            return (
                "For safety, I can only read "
                "TXT, MD, CSV, and LOG files."
            )

        with open(
            filepath,
            "r",
            encoding="utf-8"
        ) as file:

            content = file.read()

        if not content.strip():

            return "The file is empty."

        if len(content) > 6000:

            content = content[:6000]

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
