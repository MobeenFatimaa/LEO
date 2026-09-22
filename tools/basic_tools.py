import webbrowser
import requests

from datetime import datetime


# ============================================================
# WEBSITE TOOL
# ============================================================

def open_website(website):
    """
    Open a supported website in the default browser.
    """

    websites = {
        "google": "https://www.google.com",
        "youtube": "https://www.youtube.com",
        "linkedin": "https://www.linkedin.com",
        "facebook": "https://www.facebook.com",
        "github": "https://github.com"
    }

    website = website.lower().strip()

    if website in websites:

        webbrowser.open(
            websites[website]
        )

        return f"Opened {website}."

    return (
        f"I don't know the website {website}."
    )


# ============================================================
# TIME TOOL
# ============================================================

def get_time():
    """
    Return the current local time.
    """

    current_time = datetime.now().strftime(
        "%I:%M %p"
    )

    return (
        f"The current time is {current_time}."
    )


# ============================================================
# DATE TOOL
# ============================================================

def get_date():
    """
    Return the current local date.
    """

    current_date = datetime.now().strftime(
        "%A, %B %d, %Y"
    )

    return (
        f"Today is {current_date}."
    )


# ============================================================
# CALCULATOR TOOL
# ============================================================

def calculate(expression):
    """
    Calculate a basic mathematical expression.
    """

    try:

        result = eval(
            expression,
            {"__builtins__": {}},
            {}
        )

        return f"The answer is {result}."

    except Exception:

        return (
            "I couldn't calculate that."
        )


# ============================================================
# WEATHER CODE DESCRIPTION
# ============================================================

def weather_description(code):
    """
    Convert Open-Meteo weather codes into
    human-readable descriptions.
    """

    descriptions = {

        0: "clear sky",

        1: "mainly clear",

        2: "partly cloudy",

        3: "overcast",

        45: "fog",

        48: "depositing rime fog",

        51: "light drizzle",

        53: "moderate drizzle",

        55: "dense drizzle",

        56: "light freezing drizzle",

        57: "dense freezing drizzle",

        61: "slight rain",

        63: "moderate rain",

        65: "heavy rain",

        66: "light freezing rain",

        67: "heavy freezing rain",

        71: "slight snow",

        73: "moderate snow",

        75: "heavy snow",

        77: "snow grains",

        80: "slight rain showers",

        81: "moderate rain showers",

        82: "violent rain showers",

        85: "slight snow showers",

        86: "heavy snow showers",

        95: "thunderstorm",

        96: "thunderstorm with slight hail",

        99: "thunderstorm with heavy hail"
    }

    return descriptions.get(
        code,
        "unknown weather conditions"
    )


# ============================================================
# WEATHER TOOL
# ============================================================

def get_weather(location):
    """
    Get current weather for a city using Open-Meteo.

    No API key is required for normal non-commercial use.
    """

    try:

        # ----------------------------------------------------
        # STEP 1: FIND CITY COORDINATES
        # ----------------------------------------------------

        geocoding_url = (
            "https://geocoding-api.open-meteo.com/v1/search"
        )

        geocoding_params = {

            "name": location,

            "count": 1,

            "language": "en",

            "format": "json"
        }

        geocoding_response = requests.get(
            geocoding_url,
            params=geocoding_params,
            timeout=10
        )

        geocoding_response.raise_for_status()

        geocoding_data = (
            geocoding_response.json()
        )

        results = geocoding_data.get(
            "results"
        )

        if not results:

            return (
                f"I couldn't find the location "
                f"{location}."
            )


        place = results[0]

        latitude = place["latitude"]

        longitude = place["longitude"]

        city_name = place.get(
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

        weather_data = (
            weather_response.json()
        )


        current = weather_data.get(
            "current"
        )

        if not current:

            return (
                "I couldn't retrieve the "
                "current weather."
            )


        # ----------------------------------------------------
        # STEP 3: EXTRACT DATA
        # ----------------------------------------------------

        temperature = current.get(
            "temperature_2m"
        )

        humidity = current.get(
            "relative_humidity_2m"
        )

        feels_like = current.get(
            "apparent_temperature"
        )

        precipitation = current.get(
            "precipitation"
        )

        weather_code = current.get(
            "weather_code"
        )

        wind_speed = current.get(
            "wind_speed_10m"
        )


        description = weather_description(
            weather_code
        )


        # ----------------------------------------------------
        # STEP 4: RETURN NATURAL RESULT
        # ----------------------------------------------------

        return (
            f"The current weather in "
            f"{city_name}, {country} is "
            f"{description}. "
            f"The temperature is "
            f"{temperature} degrees Celsius, "
            f"feels like {feels_like} degrees, "
            f"humidity is {humidity} percent, "
            f"wind speed is {wind_speed} "
            f"kilometers per hour, and "
            f"precipitation is {precipitation} millimeters."
        )


    except requests.RequestException as error:

        print(
            "[WEATHER ERROR]",
            error
        )

        return (
            "I couldn't connect to the "
            "weather service right now."
        )


    except Exception as error:

        print(
            "[WEATHER ERROR]",
            error
        )

        return (
            "Something went wrong while "
            "getting the weather."
        )
