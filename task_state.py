# =========================================================
# LEO 2.5C
# Task State Manager
# =========================================================

from datetime import datetime
from copy import deepcopy


# =========================================================
# TASK STATUS
# =========================================================

TASK_PENDING = "PENDING"
TASK_RUNNING = "RUNNING"
TASK_PAUSED = "PAUSED"
TASK_COMPLETED = "COMPLETED"
TASK_FAILED = "FAILED"
TASK_CANCELLED = "CANCELLED"


# =========================================================
# STEP STATUS
# =========================================================

STEP_PENDING = "PENDING"
STEP_RUNNING = "RUNNING"
STEP_SUCCESS = "SUCCESS"
STEP_FAILED = "FAILED"
STEP_SKIPPED = "SKIPPED"


# =========================================================
# TASK STATE
# =========================================================

class TaskState:

    def __init__(self):

        self.reset()


    # =====================================================
    # RESET
    # =====================================================

    def reset(self):

        self.task_id = None

        self.goal = ""

        self.status = TASK_PENDING

        self.steps = []

        self.current_step_index = None

        self.started_at = None

        self.updated_at = None

        self.finished_at = None

        self.error = None


    # =====================================================
    # CREATE TASK
    # =====================================================

    def create_task(
        self,
        goal,
        steps
    ):

        self.reset()

        self.task_id = (
            datetime.now()
            .strftime("%Y%m%d%H%M%S")
        )

        self.goal = (
            goal or ""
        )

        self.steps = []

        for index, step in enumerate(
            steps or [],
            start=1
        ):

            step_data = {

                "step": step.get(
                    "step",
                    index
                ),

                "tool": step.get(
                    "tool",
                    ""
                ),

                "arguments": step.get(
                    "arguments",
                    {}
                ),

                "description": step.get(
                    "description",
                    ""
                ),

                "status": STEP_PENDING,

                "result": None,

                "started_at": None,

                "finished_at": None,
            }

            self.steps.append(
                step_data
            )

        self.status = TASK_PENDING

        self.started_at = None

        self.updated_at = (
            datetime.now().isoformat()
        )

        return self.get_state()


    # =====================================================
    # START TASK
    # =====================================================

    def start(self):

        if not self.steps:

            self.status = TASK_COMPLETED

            self.finished_at = (
                datetime.now().isoformat()
            )

            self.updated_at = (
                datetime.now().isoformat()
            )

            return

        self.status = TASK_RUNNING

        self.started_at = (
            self.started_at
            or
            datetime.now().isoformat()
        )

        self.updated_at = (
            datetime.now().isoformat()
        )


    # =====================================================
    # START STEP
    # =====================================================

    def start_step(
        self,
        step_number
    ):

        index = self.find_step_index(
            step_number
        )

        if index is None:

            return False

        self.current_step_index = index

        self.steps[index]["status"] = (
            STEP_RUNNING
        )

        self.steps[index]["started_at"] = (
            datetime.now().isoformat()
        )

        self.updated_at = (
            datetime.now().isoformat()
        )

        return True


    # =====================================================
    # COMPLETE STEP
    # =====================================================

    def complete_step(
        self,
        step_number,
        result
    ):

        index = self.find_step_index(
            step_number
        )

        if index is None:

            return False

        self.steps[index]["status"] = (
            STEP_SUCCESS
        )

        self.steps[index]["result"] = (
            str(result)
        )

        self.steps[index]["finished_at"] = (
            datetime.now().isoformat()
        )

        self.updated_at = (
            datetime.now().isoformat()
        )

        return True


    # =====================================================
    # FAIL STEP
    # =====================================================

    def fail_step(
        self,
        step_number,
        result
    ):

        index = self.find_step_index(
            step_number
        )

        if index is None:

            return False

        self.steps[index]["status"] = (
            STEP_FAILED
        )

        self.steps[index]["result"] = (
            str(result)
        )

        self.steps[index]["finished_at"] = (
            datetime.now().isoformat()
        )

        self.error = str(
            result
        )

        self.updated_at = (
            datetime.now().isoformat()
        )

        return True


    # =====================================================
    # SKIP STEP
    # =====================================================

    def skip_step(
        self,
        step_number,
        reason=""
    ):

        index = self.find_step_index(
            step_number
        )

        if index is None:

            return False

        self.steps[index]["status"] = (
            STEP_SKIPPED
        )

        self.steps[index]["result"] = (
            reason
        )

        self.steps[index]["finished_at"] = (
            datetime.now().isoformat()
        )

        self.updated_at = (
            datetime.now().isoformat()
        )

        return True


    # =====================================================
    # PAUSE TASK
    # =====================================================

    def pause(self):

        if self.status != TASK_RUNNING:

            return False

        self.status = TASK_PAUSED

        self.updated_at = (
            datetime.now().isoformat()
        )

        return True


    # =====================================================
    # RESUME TASK
    # =====================================================

    def resume(self):

        if self.status != TASK_PAUSED:

            return False

        self.status = TASK_RUNNING

        self.updated_at = (
            datetime.now().isoformat()
        )

        return True


    # =====================================================
    # CANCEL TASK
    # =====================================================

    def cancel(self):

        if self.status in {
            TASK_COMPLETED,
            TASK_FAILED,
            TASK_CANCELLED
        }:

            return False

        self.status = TASK_CANCELLED

        self.finished_at = (
            datetime.now().isoformat()
        )

        self.updated_at = (
            datetime.now().isoformat()
        )

        return True


    # =====================================================
    # COMPLETE TASK
    # =====================================================

    def complete(self):

        self.status = TASK_COMPLETED

        self.current_step_index = None

        self.finished_at = (
            datetime.now().isoformat()
        )

        self.updated_at = (
            datetime.now().isoformat()
        )


    # =====================================================
    # FAIL TASK
    # =====================================================

    def fail(
        self,
        error=""
    ):

        self.status = TASK_FAILED

        self.error = (
            str(error)
        )

        self.finished_at = (
            datetime.now().isoformat()
        )

        self.updated_at = (
            datetime.now().isoformat()
        )


    # =====================================================
    # FIND STEP
    # =====================================================

    def find_step_index(
        self,
        step_number
    ):

        for index, step in enumerate(
            self.steps
        ):

            if step["step"] == step_number:

                return index

        return None


    # =====================================================
    # GET CURRENT STEP
    # =====================================================

    def get_current_step(self):

        if (
            self.current_step_index
            is None
        ):

            return None

        if (
            self.current_step_index
            >= len(self.steps)
        ):

            return None

        return self.steps[
            self.current_step_index
        ]


    # =====================================================
    # GET NEXT PENDING STEP
    # =====================================================

    def get_next_pending_step(self):

        for step in self.steps:

            if step["status"] == STEP_PENDING:

                return step

        return None


    # =====================================================
    # PROGRESS
    # =====================================================

    def get_progress(self):

        total = len(
            self.steps
        )

        completed = 0

        for step in self.steps:

            if step["status"] in {
                STEP_SUCCESS,
                STEP_SKIPPED
            }:

                completed += 1

        if total == 0:

            percentage = 100

        else:

            percentage = int(
                (completed / total) * 100
            )

        return {
            "completed": completed,
            "total": total,
            "percentage": percentage
        }


    # =====================================================
    # CHECK ALL STEPS COMPLETE
    # =====================================================

    def all_steps_complete(self):

        if not self.steps:

            return True

        for step in self.steps:

            if step["status"] not in {
                STEP_SUCCESS,
                STEP_SKIPPED
            }:

                return False

        return True


    # =====================================================
    # CHECK FAILED STEPS
    # =====================================================

    def has_failed_steps(self):

        for step in self.steps:

            if step["status"] == STEP_FAILED:

                return True

        return False


    # =====================================================
    # GET STATE
    # =====================================================

    def get_state(self):

        return deepcopy(
            {
                "task_id": self.task_id,

                "goal": self.goal,

                "status": self.status,

                "steps": self.steps,

                "current_step_index":
                    self.current_step_index,

                "started_at":
                    self.started_at,

                "updated_at":
                    self.updated_at,

                "finished_at":
                    self.finished_at,

                "error":
                    self.error,

                "progress":
                    self.get_progress()
            }
        )


    # =====================================================
    # SUMMARY
    # =====================================================

    def summary(self):

        progress = self.get_progress()

        lines = []

        lines.append(
            "LEO TASK STATUS"
        )

        lines.append(
            "=" * 50
        )

        lines.append(
            f"Goal: {self.goal}"
        )

        lines.append(
            f"Status: {self.status}"
        )

        lines.append(
            f"Progress: "
            f"{progress['completed']} / "
            f"{progress['total']} "
            f"({progress['percentage']}%)"
        )

        lines.append("")

        for step in self.steps:

            status = step["status"]

            if status == STEP_SUCCESS:

                symbol = "✓"

            elif status == STEP_FAILED:

                symbol = "✗"

            elif status == STEP_RUNNING:

                symbol = "→"

            elif status == STEP_SKIPPED:

                symbol = "-"

            else:

                symbol = "○"

            lines.append(
                f"{symbol} Step {step['step']}: "
                f"{step['description']} "
                f"[{status}]"
            )

        if self.error:

            lines.append("")

            lines.append(
                f"Error: {self.error}"
            )

        return "\n".join(
            lines
        )


# =========================================================
# GLOBAL TASK STATE
# =========================================================

task_state = TaskState()


# =========================================================
# SIMPLE HELPERS
# =========================================================

def create_task_state(
    goal,
    steps
):

    return task_state.create_task(
        goal,
        steps
    )


def start_task():

    task_state.start()

    return task_state.get_state()


def start_step(
    step_number
):

    return task_state.start_step(
        step_number
    )


def complete_step(
    step_number,
    result
):

    return task_state.complete_step(
        step_number,
        result
    )


def fail_step(
    step_number,
    result
):

    return task_state.fail_step(
        step_number,
        result
    )


def pause_task():

    return task_state.pause()


def resume_task():

    return task_state.resume()


def cancel_task():

    return task_state.cancel()


def complete_task():

    task_state.complete()

    return task_state.get_state()


def fail_task(
    error
):

    task_state.fail(
        error
    )

    return task_state.get_state()


def get_task_state():

    return task_state.get_state()


def get_task_summary():

    return task_state.summary()


# =========================================================
# TEST MODE
# =========================================================

if __name__ == "__main__":

    print()

    print(
        "=" * 65
    )

    print(
        "LEO 2.5C - Task State Manager Test"
    )

    print(
        "=" * 65
    )

    test_steps = [

        {
            "step": 1,

            "tool": "open_vscode",

            "arguments": {},

            "description": (
                "Open Visual Studio Code"
            )
        },

        {
            "step": 2,

            "tool": "open_folder",

            "arguments": {
                "folder": (
                    r"C:\Users\User\Desktop"
                )
            },

            "description": (
                "Open the Desktop folder"
            )
        },

        {
            "step": 3,

            "tool": "open_application",

            "arguments": {
                "application": "Chrome"
            },

            "description": (
                "Open Google Chrome"
            )
        }
    ]


    # -----------------------------------------------------
    # CREATE
    # -----------------------------------------------------

    create_task_state(
        "Prepare my coding workspace",
        test_steps
    )

    print()

    print(
        get_task_summary()
    )


    # -----------------------------------------------------
    # START
    # -----------------------------------------------------

    print()

    print(
        "Starting task..."
    )

    start_task()


    # -----------------------------------------------------
    # STEP 1
    # -----------------------------------------------------

    start_step(1)

    complete_step(
        1,
        "Visual Studio Code opened successfully."
    )


    # -----------------------------------------------------
    # STEP 2
    # -----------------------------------------------------

    start_step(2)

    complete_step(
        2,
        "Desktop folder opened successfully."
    )


    # -----------------------------------------------------
    # SHOW PROGRESS
    # -----------------------------------------------------

    print()

    print(
        get_task_summary()
    )


    # -----------------------------------------------------
    # STEP 3
    # -----------------------------------------------------

    start_step(3)

    fail_step(
        3,
        "Chrome could not be opened."
    )


    # -----------------------------------------------------
    # FAIL TASK
    # -----------------------------------------------------

    fail_task(
        "Step 3 failed."
    )


    # -----------------------------------------------------
    # FINAL STATE
    # -----------------------------------------------------

    print()

    print(
        get_task_summary()
    )

    print()

    print(
        "=" * 65
    )

    print(
        "Task State Manager test completed."
    )

    print(
        "=" * 65
    )
