import webbrowser
from datetime import datetime


def open_website(website: str) -> str:
    """
    Open a supported website in the user's default browser.

    Args:
        website: Website name such as google, youtube, linkedin,
                 facebook, or github.

    Returns:
        A message describing the result.
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
        webbrowser.open(websites[website])
        return f"Opened {website}."

    return f"I don't know the website {website}."


def get_time() -> str:
    """
    Get the current local time.

    Returns:
        The current time.
    """

    current_time = datetime.now().strftime("%I:%M %p")

    return f"The current time is {current_time}."


def calculate(expression: str) -> str:
    """
    Calculate a mathematical expression.

    Args:
        expression: A basic mathematical expression.

    Returns:
        The calculation result.
    """

    try:
        result = eval(
            expression,
            {"__builtins__": {}},
            {}
        )

        return f"The answer is {result}."

    except Exception:
        return "I couldn't calculate that."
