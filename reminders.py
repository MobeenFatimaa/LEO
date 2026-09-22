import json
import os
import threading
import time
import uuid

from datetime import datetime


# ============================================================
# CONFIGURATION
# ============================================================

REMINDERS_FILE = "reminders.json"


# ============================================================
# FILE HELPERS
# ============================================================

def load_reminders():

    if not os.path.exists(REMINDERS_FILE):

        return []

    try:

        with open(
            REMINDERS_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

        if isinstance(data, list):

            return data

        return []

    except Exception:

        return []


def save_reminders(reminders):

    with open(
        REMINDERS_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            reminders,
            file,
            indent=4,
            ensure_ascii=False
        )


# ============================================================
# CREATE REMINDER
# ============================================================

def create_reminder(
    message,
    reminder_time
):

    try:

        datetime.strptime(
            reminder_time,
            "%Y-%m-%d %H:%M"
        )

    except ValueError:

        return (
            "The reminder time must use this format: "
            "YYYY-MM-DD HH:MM."
        )

    reminders = load_reminders()

    reminder = {

        "id": str(
            uuid.uuid4()
        )[:8],

        "message": message,

        "time": reminder_time,

        "completed": False
    }

    reminders.append(
        reminder
    )

    save_reminders(
        reminders
    )

    return (
        f"Reminder created successfully "
        f"for {reminder_time}: {message}"
    )


# ============================================================
# LIST REMINDERS
# ============================================================

def list_reminders():

    reminders = load_reminders()

    active = [

        reminder
        for reminder in reminders

        if not reminder.get(
            "completed",
            False
        )
    ]

    if not active:

        return "You currently have no active reminders."

    result = (
        f"You have {len(active)} active reminder"
    )

    if len(active) != 1:

        result += "s"

    result += "."

    for reminder in active:

        result += (

            f"\nReminder ID "
            f"{reminder['id']}: "

            f"{reminder['time']} - "

            f"{reminder['message']}"
        )

    return result


# ============================================================
# CANCEL REMINDER
# ============================================================

def cancel_reminder(reminder_id):

    reminders = load_reminders()

    found = False

    for reminder in reminders:

        if reminder.get("id") == reminder_id:

            reminder["completed"] = True

            found = True

            break

    if not found:

        return (
            f"I couldn't find reminder "
            f"{reminder_id}."
        )

    save_reminders(
        reminders
    )

    return (
        f"Reminder {reminder_id} "
        "has been cancelled."
    )


# ============================================================
# REMOVE COMPLETED REMINDERS
# ============================================================

def cleanup_reminders():

    reminders = load_reminders()

    active = [

        reminder
        for reminder in reminders

        if not reminder.get(
            "completed",
            False
        )
    ]

    save_reminders(
        active
    )


# ============================================================
# CHECK DUE REMINDERS
# ============================================================

def get_due_reminders():

    reminders = load_reminders()

    now = datetime.now()

    due = []

    changed = False

    for reminder in reminders:

        if reminder.get(
            "completed",
            False
        ):

            continue

        try:

            reminder_time = datetime.strptime(

                reminder["time"],

                "%Y-%m-%d %H:%M"
            )

        except Exception:

            continue

        if reminder_time <= now:

            due.append(
                reminder
            )

            reminder["completed"] = True

            changed = True

    if changed:

        save_reminders(
            reminders
        )

    return due


# ============================================================
# REMINDER BACKGROUND MONITOR
# ============================================================

class ReminderMonitor:

    def __init__(
        self,
        callback
    ):

        self.callback = callback

        self.running = False

        self.thread = None


    def start(self):

        if self.running:

            return

        self.running = True

        self.thread = threading.Thread(

            target=self._monitor,

            daemon=True
        )

        self.thread.start()


    def stop(self):

        self.running = False


    def _monitor(self):

        while self.running:

            try:

                due = get_due_reminders()

                for reminder in due:

                    self.callback(
                        reminder
                    )

            except Exception as e:

                print(
                    "[REMINDER ERROR]",
                    e
                )

            time.sleep(10)
