import json
import os
import threading
import time
import uuid
from datetime import datetime


TIMERS_FILE = "timers.json"


def load_timers():
    """Load timers from JSON."""
    if not os.path.exists(TIMERS_FILE):
        return []

    try:
        with open(TIMERS_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except (json.JSONDecodeError, OSError):
        return []


def save_timers(timers):
    """Save timers to JSON."""
    try:
        with open(TIMERS_FILE, "w", encoding="utf-8") as file:
            json.dump(timers, file, indent=4)
        return True
    except OSError:
        return False


def create_timer(seconds, message):
    """
    Create a timer.

    Args:
        seconds: Number of seconds.
        message: Message to announce when timer finishes.
    """

    try:
        seconds = int(seconds)
    except (TypeError, ValueError):
        return "Invalid timer duration."

    if seconds <= 0:
        return "Timer duration must be greater than zero."

    timer_id = str(uuid.uuid4())[:8]

    end_time = time.time() + seconds

    timer = {
        "id": timer_id,
        "message": message,
        "duration_seconds": seconds,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "end_timestamp": end_time,
        "status": "running"
    }

    timers = load_timers()
    timers.append(timer)
    save_timers(timers)

    return (
        f"Timer {timer_id} started for "
        f"{format_duration(seconds)}. "
        f"I'll notify you when it finishes."
    )


def list_timers():
    """Return active timers."""

    timers = load_timers()

    if not timers:
        return "There are no active timers."

    now = time.time()
    active = []

    for timer in timers:
        if timer.get("status") != "running":
            continue

        remaining = int(timer["end_timestamp"] - now)

        if remaining <= 0:
            continue

        active.append(
            f"Timer {timer['id']}: "
            f"{timer.get('message', 'Timer finished')} "
            f"({format_duration(remaining)} remaining)"
        )

    if not active:
        return "There are no active timers."

    return "\n".join(active)


def cancel_timer(timer_id):
    """Cancel a timer."""

    timers = load_timers()

    for timer in timers:
        if timer.get("id") == timer_id:
            if timer.get("status") != "running":
                return f"Timer {timer_id} is not active."

            timer["status"] = "cancelled"
            save_timers(timers)

            return f"Timer {timer_id} has been cancelled."

    return f"I couldn't find timer {timer_id}."


def cleanup_timers():
    """Remove completed/cancelled timers."""

    timers = load_timers()

    active = [
        timer
        for timer in timers
        if timer.get("status") == "running"
    ]

    save_timers(active)


def format_duration(seconds):
    """Convert seconds into human-readable duration."""

    seconds = int(seconds)

    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    remaining_seconds = seconds % 60

    parts = []

    if hours:
        parts.append(
            f"{hours} hour" + ("s" if hours != 1 else "")
        )

    if minutes:
        parts.append(
            f"{minutes} minute" + ("s" if minutes != 1 else "")
        )

    if remaining_seconds or not parts:
        parts.append(
            f"{remaining_seconds} second"
            + ("s" if remaining_seconds != 1 else "")
        )

    return " ".join(parts)


class TimerMonitor:
    """
    Background timer monitor.

    Checks active timers every second.
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

            timers = load_timers()
            changed = False

            for timer in timers:

                if timer.get("status") != "running":
                    continue

                if time.time() >= timer.get("end_timestamp", 0):

                    timer["status"] = "completed"
                    changed = True

                    message = timer.get(
                        "message",
                        "Your timer has finished."
                    )

                    try:
                        self.callback(
                            timer.get("id"),
                            message
                        )
                    except Exception:
                        pass

            if changed:
                save_timers(timers)

            time.sleep(1)
