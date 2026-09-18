### `tools/basic_hooks.py`


import webbrowser
from datetime import datetime


# ============================================================
# WEBSITE LIST
# ============================================================

WEBSITES = {

    "google":
        "https://www.google.com",

    "youtube":
        "https://www.youtube.com",

    "github":
        "https://github.com",

    "linkedin":
        "https://www.linkedin.com",

    "facebook":
        "https://www.facebook.com",

    "gmail":
        "https://mail.google.com",

    "chatgpt":
        "https://chatgpt.com"
}


# ============================================================
# OPEN WEBSITE
# ============================================================

def open_website(website: str) -> str:

    print(
        "DEBUG: open_website() called with:",
        repr(website)
    )

    if not website:

        return "You didn't specify a website."

    website = website.lower().strip()

    # --------------------------------------------------------
    # Check website
    # --------------------------------------------------------

    if website not in WEBSITES:

        return (
            f"I don't know the website {website}."
        )

    url = WEBSITES[website]

    print(
        "DEBUG: Opening URL:",
        url
    )

    # --------------------------------------------------------
    # Open browser
    # --------------------------------------------------------

    try:

        webbrowser.open_new_tab(url)

        return (
            f"Opened {website}."
        )

    except Exception as e:

        print(
            "BROWSER ERROR:",
            repr(e)
        )

        return (
            f"I couldn't open {website}."
        )


# ============================================================
# GET TIME
# ============================================================

def get_time() -> str:

    current_time = datetime.now().strftime(
        "%I:%M %p"
    )

    return (
        f"The current time is {current_time}."
    )


# ============================================================
# CALCULATOR
# ============================================================

def calculate(expression: str) -> str:

    if not expression:

        return "You didn't provide a calculation."

    try:

        result = eval(
            expression,
            {
                "__builtins__": {}
            },
            {}
        )

        return f"The answer is {result}."

    except Exception as e:

        print(
            "CALCULATOR ERROR:",
            repr(e)
        )

        return (
            "I couldn't calculate that."
        )
