# =========================================================
# LEO - Timer System
# =========================================================

import json
import threading
import time
import uuid

from datetime import datetime, timedelta
from pathlib import Path


TIMERS_FILE = Path("timers.json")


# =========================================================
# STORAGE
# =========================================================

def load_timers():

    if not TIMERS_FILE.exists():

        return []

    try:

        with open(
            TIMERS_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    except Exception:

        return []


def save_timers(timers):

    with open(
        TIMERS_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            timers,
            file,
            indent=4
        )


# =========================================================
# CREATE TIMER
# =========================================================

def create_timer(
    seconds,
    message="Timer finished."
):

    try:

        seconds = int(seconds)

    except (TypeError, ValueError):

        return "Timer duration must be a number of seconds."

    if seconds <= 0:

        return "Timer duration must be greater than zero."

    timer_id = str(uuid.uuid4())[:8]

    now = datetime.now()

    end_time = (
        now +
        timedelta(seconds=seconds)
    )

    timer = {
        "id": timer_id,
        "message": message or "Timer finished.",
        "seconds": seconds,
        "created_at": now.isoformat(),
        "end_time": end_time.isoformat(),
        "active": True
    }

    timers = load_timers()

    timers.append(timer)

    save_timers(timers)

    return (
        f"Timer {timer_id} created for "
        f"{seconds} seconds."
    )


# =========================================================
# LIST TIMERS
# =========================================================

def list_timers():

    timers = load_timers()

    active = [
        timer
        for timer in timers
        if timer.get("active", True)
    ]

    if not active:

        return "There are no active timers."

    lines = []

    now = datetime.now()

    for timer in active:

        try:

            end_time = datetime.fromisoformat(
                timer["end_time"]
            )

            remaining = (
                end_time - now
            ).total_seconds()

            if remaining < 0:

                remaining = 0

            lines.append(
                f"ID {timer['id']}: "
                f"{timer['message']} "
                f"({int(remaining)} seconds remaining)"
            )

        except Exception:

            lines.append(
                f"ID {timer['id']}: "
                f"{timer['message']}"
            )

    return "\n".join(lines)


# =========================================================
# CANCEL TIMER
# =========================================================

def cancel_timer(timer_id):

    if not timer_id:

        return "No timer ID was provided."

    timers = load_timers()

    found = False

    for timer in timers:

        if timer["id"] == timer_id:

            timer["active"] = False

            found = True

            break

    if not found:

        return (
            f"Timer {timer_id} was not found."
        )

    save_timers(timers)

    return (
        f"Timer {timer_id} has been cancelled."
    )


# =========================================================
# CLEANUP
# =========================================================

def cleanup_timers():

    timers = load_timers()

    now = datetime.now()

    changed = False

    for timer in timers:

        if not timer.get("active", True):

            continue

        try:

            end_time = datetime.fromisoformat(
                timer["end_time"]
            )

            if now >= end_time:

                timer["active"] = False

                changed = True

        except Exception:

            timer["active"] = False

            changed = True

    if changed:

        save_timers(timers)


# =========================================================
# GET DUE TIMERS
# =========================================================

def get_due_timers():

    timers = load_timers()

    now = datetime.now()

    due = []

    changed = False

    for timer in timers:

        if not timer.get("active", True):

            continue

        try:

            end_time = datetime.fromisoformat(
                timer["end_time"]
            )

            if now >= end_time:

                due.append(timer)

                timer["active"] = False

                changed = True

        except Exception:

            timer["active"] = False

            changed = True

    if changed:

        save_timers(timers)

    return due


# =========================================================
# BACKGROUND MONITOR
# =========================================================

class TimerMonitor:

    def __init__(
        self,
        callback,
        interval=1
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

                due_timers = get_due_timers()

                for timer in due_timers:

                    try:

                        self.callback(
                            timer["id"],
                            timer["message"]
                        )

                    except Exception as error:

                        print(
                            f"Timer callback error: {error}"
                        )

            except Exception as error:

                print(
                    f"Timer monitor error: {error}"
                )

            time.sleep(
                self.interval
            )

    def stop(self):

        self.running = False
