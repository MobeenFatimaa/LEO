# =========================================================
# LEO - Session Context
# =========================================================

from collections import deque


class SessionContext:
    """
    Maintains short-term conversational context during
    the current LEO session.
    """

    def __init__(self, max_items=12):

        self.max_items = max_items

        self.messages = deque(
            maxlen=max_items
        )

        self.last_tool = None

        self.last_tool_result = None

        self.last_user_command = None

        self.last_assistant_response = None

        self.last_opened_application = None

        self.last_opened_website = None

        self.last_file = None

        self.last_location = None

    # -----------------------------------------------------
    # MESSAGE MANAGEMENT
    # -----------------------------------------------------

    def add_user_message(self, message):

        self.last_user_command = message

        self.messages.append(
            {
                "role": "user",
                "content": message
            }
        )

    def add_assistant_message(self, message):

        self.last_assistant_response = message

        self.messages.append(
            {
                "role": "assistant",
                "content": message
            }
        )

    # -----------------------------------------------------
    # TOOL MANAGEMENT
    # -----------------------------------------------------

    def set_tool_result(
        self,
        tool_name,
        result
    ):

        self.last_tool = tool_name

        self.last_tool_result = str(result)

    # -----------------------------------------------------
    # ENTITY TRACKING
    # -----------------------------------------------------

    def set_application(self, application):

        self.last_opened_application = application

    def set_website(self, website):

        self.last_opened_website = website

    def set_file(self, filepath):

        self.last_file = filepath

    def set_location(self, location):

        self.last_location = location

    # -----------------------------------------------------
    # CONTEXT
    # -----------------------------------------------------

    def get_context(self):

        lines = []

        if self.last_user_command:

            lines.append(
                f"Last user command: "
                f"{self.last_user_command}"
            )

        if self.last_assistant_response:

            lines.append(
                f"Last LEO response: "
                f"{self.last_assistant_response}"
            )

        if self.last_tool:

            lines.append(
                f"Last tool used: "
                f"{self.last_tool}"
            )

        if self.last_tool_result:

            lines.append(
                f"Last tool result: "
                f"{self.last_tool_result}"
            )

        if self.last_opened_application:

            lines.append(
                f"Last opened application: "
                f"{self.last_opened_application}"
            )

        if self.last_opened_website:

            lines.append(
                f"Last opened website: "
                f"{self.last_opened_website}"
            )

        if self.last_file:

            lines.append(
                f"Last referenced file: "
                f"{self.last_file}"
            )

        if self.last_location:

            lines.append(
                f"Last referenced location: "
                f"{self.last_location}"
            )

        if not lines:

            return "No active session context."

        return "\n".join(lines)

    # -----------------------------------------------------
    # RECENT MESSAGES
    # -----------------------------------------------------

    def get_recent_messages(
        self,
        count=6
    ):

        messages = list(
            self.messages
        )

        messages = messages[-count:]

        if not messages:

            return "No recent messages."

        lines = []

        for message in messages:

            role = message["role"]

            content = message["content"]

            lines.append(
                f"{role.upper()}: {content}"
            )

        return "\n".join(lines)

    # -----------------------------------------------------
    # CLEAR
    # -----------------------------------------------------

    def clear(self):

        self.messages.clear()

        self.last_tool = None

        self.last_tool_result = None

        self.last_user_command = None

        self.last_assistant_response = None

        self.last_opened_application = None

        self.last_opened_website = None

        self.last_file = None

        self.last_location = None

    # -----------------------------------------------------
    # DEBUG
    # -----------------------------------------------------

    def summary(self):

        return {
            "messages": len(self.messages),
            "last_tool": self.last_tool,
            "last_application": self.last_opened_application,
            "last_website": self.last_opened_website,
            "last_file": self.last_file,
            "last_location": self.last_location
        }
