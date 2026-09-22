import webbrowser
import subprocess
import requests
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

    webbrowser.open(websites[website])

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
        return f"I couldn't open {application}. Error: {str(e)}"


# ============================================================
# VS CODE TOOL
# ============================================================

def open_vscode():
    try:
        subprocess.Popen(
            "code",
            shell=True
        )

        return "Opening Visual Studio Code."

    except Exception as e:
        return f"I couldn't open Visual Studio Code. Error: {str(e)}"


# ============================================================
# FOLDER TOOL
# ============================================================

def open_folder(folder):
    folder = folder.lower().strip()

    folders = {
        "desktop": r"C:\Users\User\Desktop",
        "documents": r"C:\Users\User\Documents",
        "downloads": r"C:\Users\User\Downloads",
        "pictures": r"C:\Users\User\Pictures",
        "videos": r"C:\Users\User\Videos",
        "music": r"C:\Users\User\Music"
    }

    if folder not in folders:
        return (
            f"I don't have a configured path for {folder}. "
            "You can ask me to open Desktop, Documents, "
            "Downloads, Pictures, Videos, or Music."
        )

    try:
        subprocess.Popen(
            ["explorer", folders[folder]]
        )

        return f"Opening your {folder} folder."

    except Exception as e:
        return f"I couldn't open the {folder} folder. Error: {str(e)}"


# ============================================================
# TIME TOOL
# ============================================================

def get_time():
    now = datetime.now()

    return now.strftime(
        "The current time is %I:%M %p."
    )


# ============================================================
# DATE TOOL
# ============================================================

def get_date():
    now = datetime.now()

    return now.strftime(
        "Today is %A, %B %d, %Y."
    )


# ============================================================
# CALCULATOR TOOL
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
            return "I can only calculate basic mathematical expressions."

        result = eval(
            expression,
            {
                "__builtins__": {}
            },
            {}
        )

        return f"The answer is {result}."

    except Exception:
        return "I couldn't calculate that expression."


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
# WEATHER TOOL
# ============================================================

def get_weather(location):

    try:

        # ----------------------------------------------------
        # STEP 1: FIND LOCATION
        # ----------------------------------------------------

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

        geocode_data = geocode_response.json()

        if not geocode_data.get("results"):
            return f"I couldn't find the location {location}."

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

        # ----------------------------------------------------
        # STEP 2: GET WEATHER
        # ----------------------------------------------------

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

        weather_data = weather_response.json()

        current = weather_data["current"]

        temperature = current["temperature_2m"]
        humidity = current["relative_humidity_2m"]
        feels_like = current["apparent_temperature"]
        precipitation = current["precipitation"]
        weather_code = current["weather_code"]
        wind_speed = current["wind_speed_10m"]

        description = weather_description(
            weather_code
        )

        return (
            f"Current weather in {place_name}, {country}: "
            f"{description}. "
            f"Temperature is {temperature} degrees Celsius, "
            f"feels like {feels_like} degrees, "
            f"humidity is {humidity} percent, "
            f"wind speed is {wind_speed} kilometers per hour, "
            f"and precipitation is {precipitation} millimeters."
        )

    except requests.RequestException:
        return (
            "I couldn't connect to the weather service."
        )

    except Exception as e:
        return (
            f"I couldn't get the weather. Error: {str(e)}"
        )
