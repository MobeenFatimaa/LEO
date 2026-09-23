import json
import os
import threading
import time
import uuid
from datetime import datetime


ALARMS_FILE = "alarms.json"
# =========================================================
# LEO - Daily Alarm System
# =========================================================

import json
import threading
import time
import uuid

from datetime import datetime
from pathlib import Path


ALARMS_FILE = Path("alarms.json")


# =========================================================
# STORAGE
# =========================================================

def load_alarms():

    if not ALARMS_FILE.exists():

        return []

    try:

        with open(
            ALARMS_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    except Exception:

        return []


def save_alarms(alarms):

    with open(
        ALARMS_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            alarms,
            file,
            indent=4
        )


# =========================================================
# CREATE
# =========================================================

def create_alarm(
    alarm_time,
    message="Alarm."
):

    if not alarm_time:

        return "No alarm time was provided."

    try:

        parsed = datetime.strptime(
            alarm_time,
            "%H:%M"
        )

    except ValueError:

        return (
            "Alarm time must use HH:MM format."
        )

    alarm_id = str(uuid.uuid4())[:8]

    alarm = {
        "id": alarm_id,
        "time": parsed.strftime("%H:%M"),
        "message": message or "Alarm.",
        "active": True,
        "last_triggered_date": None
    }

    alarms = load_alarms()

    alarms.append(alarm)

    save_alarms(alarms)

    return (
        f"Daily alarm {alarm_id} set for "
        f"{alarm['time']}."
    )


# =========================================================
# LIST
# =========================================================

def list_alarms():

    alarms = load_alarms()

    active = [
        alarm
        for alarm in alarms
        if alarm.get("active", True)
    ]

    if not active:

        return "There are no active alarms."

    lines = []

    for alarm in active:

        lines.append(
            f"ID {alarm['id']}: "
            f"{alarm['time']} - "
            f"{alarm['message']}"
        )

    return "\n".join(lines)


# =========================================================
# CANCEL
# =========================================================

def cancel_alarm(alarm_id):

    if not alarm_id:

        return "No alarm ID was provided."

    alarms = load_alarms()

    found = False

    for alarm in alarms:

        if alarm["id"] == alarm_id:

            alarm["active"] = False

            found = True

            break

    if not found:

        return (
            f"Alarm {alarm_id} was not found."
        )

    save_alarms(alarms)

    return (
        f"Alarm {alarm_id} has been cancelled."
    )


# =========================================================
# DUE ALARMS
# =========================================================

def get_due_alarms():

    alarms = load_alarms()

    now = datetime.now()

    current_time = now.strftime(
        "%H:%M"
    )

    today = now.strftime(
        "%Y-%m-%d"
    )

    due = []

    changed = False

    for alarm in alarms:

        if not alarm.get("active", True):

            continue

        if alarm["time"] != current_time:

            continue

        if alarm.get(
            "last_triggered_date"
        ) == today:

            continue

        alarm[
            "last_triggered_date"
        ] = today

        due.append(alarm)

        changed = True

    if changed:

        save_alarms(alarms)

    return due


# =========================================================
# MONITOR
# =========================================================

class AlarmMonitor:

    def __init__(
        self,
        callback,
        interval=5
    ):

        self.callback = callback

        self.interval = interval

        self.running = False

        self.thread = None

    def start(self):

        if self.running:

            return

        self.running = True

        self.thread = threading.Thread(
            target=self._run,
            daemon=True
        )

        self.thread.start()

    def _run(self):

        while self.running:

            try:

                due = get_due_alarms()

                for alarm in due:

                    try:

                        self.callback(
                            alarm["id"],
                            alarm["message"]
                        )

                    except Exception as error:

                        print(
                            f"Alarm callback error: {error}"
                        )

            except Exception as error:

                print(
                    f"Alarm monitor error: {error}"
                )

            time.sleep(
                self.interval
            )

    def stop(self):

        self.running = False

def load_alarms():
    """Load alarms from JSON."""

    if not os.path.exists(ALARMS_FILE):
        return []

    try:
        with open(ALARMS_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except (json.JSONDecodeError, OSError):
        return []


def save_alarms(alarms):
    """Save alarms to JSON."""

    try:
        with open(ALARMS_FILE, "w", encoding="utf-8") as file:
            json.dump(alarms, file, indent=4)

        return True

    except OSError:
        return False


def create_alarm(alarm_time, message):
    """
    Create an alarm.

    alarm_time format:
    HH:MM

    Example:
    07:30
    """

    try:
        datetime.strptime(alarm_time, "%H:%M")
    except ValueError:
        return "Invalid alarm time. Please use HH:MM format."

    alarm_id = str(uuid.uuid4())[:8]

    alarm = {
        "id": alarm_id,
        "time": alarm_time,
        "message": message,
        "created_at": datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
        "enabled": True,
        "last_triggered": None
    }

    alarms = load_alarms()
    alarms.append(alarm)

    save_alarms(alarms)

    return (
        f"Alarm {alarm_id} set for {alarm_time}. "
        f"I'll notify you when it's time."
    )


def list_alarms():
    """Return active alarms."""

    alarms = load_alarms()

    active = [
        alarm
        for alarm in alarms
        if alarm.get("enabled", True)
    ]

    if not active:
        return "There are no active alarms."

    lines = []

    for alarm in active:

        lines.append(
            f"Alarm {alarm['id']}: "
            f"{alarm['time']} — "
            f"{alarm.get('message', 'Alarm')}"
        )

    return "\n".join(lines)


def cancel_alarm(alarm_id):
    """Disable an alarm."""

    alarms = load_alarms()

    for alarm in alarms:

        if alarm.get("id") == alarm_id:

            alarm["enabled"] = False
            save_alarms(alarms)

            return f"Alarm {alarm_id} has been cancelled."

    return f"I couldn't find alarm {alarm_id}."


class AlarmMonitor:
    """
    Background monitor for daily alarms.
    """

    def __init__(self, callback):
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

        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=2)

    def _monitor(self):

        while self.running:

            current_time = datetime.now().strftime("%H:%M")
            current_date = datetime.now().strftime("%Y-%m-%d")

            alarms = load_alarms()
            changed = False

            for alarm in alarms:

                if not alarm.get("enabled", True):
                    continue

                if alarm.get("time") != current_time:
                    continue

                if alarm.get("last_triggered") == current_date:
                    continue

                alarm["last_triggered"] = current_date
                changed = True

                try:
                    self.callback(
                        alarm.get("id"),
                        alarm.get(
                            "message",
                            "Your alarm is ringing."
                        )
                    )
                except Exception:
                    pass

            if changed:
                save_alarms(alarms)

            time.sleep(10)
