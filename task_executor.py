
# =========================================================
# LEO 2.5D
# State-Aware Task Executor
# =========================================================

from datetime import datetime

from task_state import (
    TaskState,
    TASK_PENDING,
    TASK_RUNNING,
    TASK_PAUSED,
    TASK_COMPLETED,
    TASK_FAILED,
    TASK_CANCELLED,
    STEP_SUCCESS,
    STEP_FAILED,
)


# =========================================================
# EXECUTION STATUS
# =========================================================

STATUS_PENDING = "PENDING"
STATUS_RUNNING = "RUNNING"
STATUS_SUCCESS = "SUCCESS"
STATUS_FAILED = "FAILED"
STATUS_COMPLETED = "COMPLETED"
STATUS_STOPPED = "STOPPED"


# =========================================================
# TASK EXECUTOR
# =========================================================

class TaskExecutor:

    def __init__(
        self,
        tool_executor,
        stop_on_failure=True,
        max_retries=1
    ):
        """
        tool_executor:
            Function that receives:

                tool_name
                arguments

            and returns a tool result.

        stop_on_failure:
            Stop the entire plan when a step fails.

        max_retries:
            Number of extra attempts for a failed step.

            Example:

                max_retries=1

            means:

                first attempt
                +
                one retry
        """

        self.tool_executor = (
            tool_executor
        )

        self.stop_on_failure = (
            stop_on_failure
        )

        self.max_retries = max(
            0,
            int(max_retries)
        )

        self.current_plan = None

        self.execution_results = []

        self.status = STATUS_PENDING

        self.started_at = None

        self.finished_at = None

        self.task_state = TaskState()

        self.cancel_requested = False


    # =====================================================
    # RESET
    # =====================================================

    def reset(self):

        self.current_plan = None

        self.execution_results = []

        self.status = STATUS_PENDING

        self.started_at = None

        self.finished_at = None

        self.task_state.reset()

        self.cancel_requested = False


    # =====================================================
    # REQUEST CANCELLATION
    # =====================================================

    def request_cancel(self):

        self.cancel_requested = True

        print()

        print(
            "[EXECUTOR] "
            "Task cancellation requested."
        )


    # =====================================================
    # CHECK CANCELLATION
    # =====================================================

    def is_cancelled(self):

        return (
            self.cancel_requested
            or
            self.task_state.status
            == TASK_CANCELLED
        )


    # =====================================================
    # DETECT TOOL FAILURE
    # =====================================================

    def is_tool_failure(
        self,
        result
    ):

        if result is None:

            return True

        result_text = str(
            result
        ).lower()

        failure_indicators = [

            "failed",

            "error:",

            "tool error",

            "couldn't",

            "could not",

            "unable to",

            "exception",

        ]

        for indicator in failure_indicators:

            if indicator in result_text:

                return True

        return False


    # =====================================================
    # EXECUTE SINGLE ATTEMPT
    # =====================================================

    def execute_attempt(
        self,
        step
    ):

        step_number = step.get(
            "step"
        )

        tool_name = step.get(
            "tool"
        )

        arguments = step.get(
            "arguments",
            {}
        )

        description = step.get(
            "description",
            ""
        )

        print()

        print(
            "-" * 65
        )

        print(
            f"Executing step {step_number}"
        )

        print(
            f"Tool: {tool_name}"
        )

        print(
            f"Arguments: {arguments}"
        )

        print(
            f"Description: {description}"
        )

        print(
            "-" * 65
        )

        started_at = (
            datetime.now().isoformat()
        )

        # -------------------------------------------------
        # UPDATE STATE
        # -------------------------------------------------

        self.task_state.start_step(
            step_number
        )

        try:

            result = self.tool_executor(
                tool_name,
                arguments
            )

            success = not self.is_tool_failure(
                result
            )

        except Exception as error:

            result = (
                f"Tool execution exception: "
                f"{error}"
            )

            success = False

        finished_at = (
            datetime.now().isoformat()
        )

        if success:

            self.task_state.complete_step(
                step_number,
                result
            )

            step_status = STATUS_SUCCESS

        else:

            self.task_state.fail_step(
                step_number,
                result
            )

            step_status = STATUS_FAILED

        execution_record = {

            "step": step_number,

            "tool": tool_name,

            "arguments": arguments,

            "description": description,

            "status": step_status,

            "result": str(result),

            "started_at": started_at,

            "finished_at": finished_at,

        }

        self.execution_results.append(
            execution_record
        )

        print(
            f"Status: {step_status}"
        )

        print(
            f"Result: {result}"
        )

        return execution_record


    # =====================================================
    # EXECUTE SINGLE STEP WITH RETRIES
    # =====================================================

    def execute_step(
        self,
        step
    ):

        step_number = step.get(
            "step"
        )

        attempts = 0

        total_allowed_attempts = (
            1 + self.max_retries
        )

        while attempts < total_allowed_attempts:

            # ---------------------------------------------
            # CHECK CANCELLATION
            # ---------------------------------------------

            if self.is_cancelled():

                return {

                    "step": step_number,

                    "tool": step.get(
                        "tool"
                    ),

                    "arguments": step.get(
                        "arguments",
                        {}
                    ),

                    "description": step.get(
                        "description",
                        ""
                    ),

                    "status": STATUS_STOPPED,

                    "result": (
                        "Task was cancelled "
                        "before this step."
                    ),

                    "started_at": None,

                    "finished_at": (
                        datetime.now().isoformat()
                    ),

                }

            attempts += 1

            print()

            print(
                f"[EXECUTOR] "
                f"Attempt {attempts}/"
                f"{total_allowed_attempts}"
            )

            result = self.execute_attempt(
                step
            )

            if result["status"] == STATUS_SUCCESS:

                result["attempts"] = attempts

                return result

            # ---------------------------------------------
            # RETRY
            # ---------------------------------------------

            if attempts < total_allowed_attempts:

                print()

                print(
                    f"[EXECUTOR] "
                    f"Step {step_number} failed."
                )

                print(
                    "[EXECUTOR] Retrying..."
                )

        result["attempts"] = attempts

        return result


    # =====================================================
    # EXECUTE PLAN
    # =====================================================

    def execute_plan(
        self,
        plan
    ):

        self.reset()

        self.current_plan = plan

        self.started_at = (
            datetime.now().isoformat()
        )

        # -------------------------------------------------
        # BASIC PLAN VALIDATION
        # -------------------------------------------------

        if not isinstance(
            plan,
            dict
        ):

            self.status = STATUS_FAILED

            self.finished_at = (
                datetime.now().isoformat()
            )

            return self.build_report(
                error=(
                    "Plan must be a dictionary."
                )
            )

        if plan.get("error"):

            self.status = STATUS_FAILED

            self.finished_at = (
                datetime.now().isoformat()
            )

            return self.build_report(
                error=plan.get(
                    "error"
                )
            )

        steps = plan.get(
            "steps",
            []
        )

        if not isinstance(
            steps,
            list
        ):

            self.status = STATUS_FAILED

            self.finished_at = (
                datetime.now().isoformat()
            )

            return self.build_report(
                error=(
                    "Plan steps must be a list."
                )
            )

        if not steps:

            self.status = STATUS_COMPLETED

            self.finished_at = (
                datetime.now().isoformat()
            )

            return self.build_report(
                message=(
                    "No execution steps "
                    "were required."
                )
            )

        # -------------------------------------------------
        # CREATE TASK STATE
        # -------------------------------------------------

        self.task_state.create_task(
            goal=plan.get(
                "goal",
                ""
            ),
            steps=steps
        )

        self.task_state.start()

        self.status = STATUS_RUNNING

        # -------------------------------------------------
        # START MESSAGE
        # -------------------------------------------------

        print()

        print(
            "=" * 65
        )

        print(
            "LEO TASK EXECUTION STARTED"
        )

        print(
            "=" * 65
        )

        print(
            f"Goal: "
            f"{plan.get('goal', '')}"
        )

        print(
            f"Steps: "
            f"{len(steps)}"
        )

        print(
            f"Maximum retries per step: "
            f"{self.max_retries}"
        )

        print(
            "=" * 65
        )

        # -------------------------------------------------
        # EXECUTE EACH STEP
        # -------------------------------------------------

        for step in steps:

            # ---------------------------------------------
            # CHECK CANCELLATION
            # ---------------------------------------------

            if self.is_cancelled():

                self.task_state.cancel()

                self.status = STATUS_STOPPED

                self.finished_at = (
                    datetime.now().isoformat()
                )

                return self.build_report(
                    error=(
                        "Task was cancelled."
                    )
                )

            # ---------------------------------------------
            # EXECUTE STEP
            # ---------------------------------------------

            result = self.execute_step(
                step
            )

            # ---------------------------------------------
            # STOPPED
            # ---------------------------------------------

            if result["status"] == STATUS_STOPPED:

                self.task_state.cancel()

                self.status = STATUS_STOPPED

                self.finished_at = (
                    datetime.now().isoformat()
                )

                return self.build_report(
                    error=(
                        "Task was cancelled "
                        "before the step executed."
                    )
                )

            # ---------------------------------------------
            # FAILED
            # ---------------------------------------------

            if result["status"] == STATUS_FAILED:

                print()

                print(
                    f"[EXECUTOR] "
                    f"Step {result['step']} "
                    f"failed after "
                    f"{result.get('attempts', 1)} "
                    f"attempt(s)."
                )

                if self.stop_on_failure:

                    self.task_state.fail(
                        (
                            f"Step "
                            f"{result['step']} "
                            f"failed."
                        )
                    )

                    self.status = STATUS_FAILED

                    self.finished_at = (
                        datetime.now().isoformat()
                    )

                    return self.build_report(
                        error=(
                            f"Execution stopped "
                            f"because step "
                            f"{result['step']} "
                            f"failed."
                        )
                    )

        # -------------------------------------------------
        # ALL STEPS COMPLETE
        # -------------------------------------------------

        if self.task_state.all_steps_complete():

            self.task_state.complete()

            self.status = STATUS_COMPLETED

        else:

            self.task_state.fail(
                "Not all steps completed."
            )

            self.status = STATUS_FAILED

        self.finished_at = (
            datetime.now().isoformat()
        )

        # -------------------------------------------------
        # COMPLETION MESSAGE
        # -------------------------------------------------

        print()

        print(
            "=" * 65
        )

        if self.status == STATUS_COMPLETED:

            print(
                "LEO TASK EXECUTION COMPLETED"
            )

        else:

            print(
                "LEO TASK EXECUTION FAILED"
            )

        print(
            "=" * 65
        )

        return self.build_report()


    # =====================================================
    # BUILD EXECUTION REPORT
    # =====================================================

    def build_report(
        self,
        error=None,
        message=None
    ):

        successful_steps = 0

        failed_steps = 0

        stopped_steps = 0

        for result in self.execution_results:

            if result["status"] == STATUS_SUCCESS:

                successful_steps += 1

            elif result["status"] == STATUS_FAILED:

                failed_steps += 1

            elif result["status"] == STATUS_STOPPED:

                stopped_steps += 1

        state = self.task_state.get_state()

        report = {

            "task_id":
                state.get(
                    "task_id"
                ),

            "goal":
                state.get(
                    "goal",
                    ""
                ),

            "status":
                self.status,

            "total_steps":
                len(
                    state.get(
                        "steps",
                        []
                    )
                ),

            "successful_steps":
                successful_steps,

            "failed_steps":
                failed_steps,

            "stopped_steps":
                stopped_steps,

            "progress":
                state.get(
                    "progress",
                    {}
                ),

            "results":
                self.execution_results,

            "task_state":
                state,

            "started_at":
                self.started_at,

            "finished_at":
                self.finished_at,

        }

        if error:

            report["error"] = error

        if message:

            report["message"] = message

        return report


    # =====================================================
    # CURRENT STATE
    # =====================================================

    def get_state(self):

        return self.task_state.get_state()


    # =====================================================
    # CURRENT SUMMARY
    # =====================================================

    def get_summary(self):

        return self.task_state.summary()


# =========================================================
# SIMPLE EXECUTION FUNCTION
# =========================================================

def execute_plan(
    plan,
    tool_executor,
    stop_on_failure=True,
    max_retries=1
):

    executor = TaskExecutor(

        tool_executor=tool_executor,

        stop_on_failure=stop_on_failure,

        max_retries=max_retries

    )

    return executor.execute_plan(
        plan
    )


# =========================================================
# HUMAN-READABLE REPORT
# =========================================================

def print_execution_report(
    report
):

    print()

    print(
        "=" * 65
    )

    print(
        "LEO EXECUTION REPORT"
    )

    print(
        "=" * 65
    )

    print(
        f"Task ID: "
        f"{report.get('task_id', '')}"
    )

    print(
        f"Goal: "
        f"{report.get('goal', '')}"
    )

    print(
        f"Status: "
        f"{report.get('status', '')}"
    )

    print(
        f"Total steps: "
        f"{report.get('total_steps', 0)}"
    )

    print(
        f"Successful: "
        f"{report.get('successful_steps', 0)}"
    )

    print(
        f"Failed: "
        f"{report.get('failed_steps', 0)}"
    )

    print(
        f"Stopped: "
        f"{report.get('stopped_steps', 0)}"
    )

    progress = report.get(
        "progress",
        {}
    )

    print(
        f"Progress: "
        f"{progress.get('completed', 0)} / "
        f"{progress.get('total', 0)} "
        f"({progress.get('percentage', 0)}%)"
    )

    if report.get("error"):

        print()

        print(
            f"Error: "
            f"{report['error']}"
        )

    print()

    results = report.get(
        "results",
        []
    )

    for result in results:

        print(
            f"Step {result['step']}: "
            f"{result['status']}"
        )

        print(
            f"  Tool: "
            f"{result['tool']}"
        )

        print(
            f"  Attempts: "
            f"{result.get('attempts', 1)}"
        )

        print(
            f"  Result: "
            f"{result['result']}"
        )

    print()

    print(
        "=" * 65
    )


# =========================================================
# TEST MODE
# =========================================================

if __name__ == "__main__":

    print()

    print(
        "=" * 65
    )

    print(
        "LEO 2.5D - State-Aware Executor Test"
    )

    print(
        "=" * 65
    )

    # -----------------------------------------------------
    # FAKE TOOL EXECUTOR
    # -----------------------------------------------------

    def fake_tool_executor(
        tool_name,
        arguments
    ):

        print()

        print(
            "[FAKE TOOL]"
        )

        print(
            f"Tool: {tool_name}"
        )

        print(
            f"Arguments: {arguments}"
        )

        return (
            f"Successfully simulated "
            f"{tool_name}"
        )


    # -----------------------------------------------------
    # TEST PLAN
    # -----------------------------------------------------

    test_plan = {

        "goal":
            "Prepare a development workspace",

        "steps": [

            {
                "step": 1,

                "tool":
                    "open_vscode",

                "arguments": {},

                "description":
                    "Open Visual Studio Code"
            },

            {
                "step": 2,

                "tool":
                    "open_application",

                "arguments": {
                    "application": "Chrome"
                },

                "description":
                    "Open Google Chrome"
            },

            {
                "step": 3,

                "tool":
                    "open_website",

                "arguments": {
                    "website": "github"
                },

                "description":
                    "Open GitHub"
            }

        ]
    }


    # -----------------------------------------------------
    # EXECUTE TEST
    # -----------------------------------------------------

    executor = TaskExecutor(

        tool_executor=
            fake_tool_executor,

        stop_on_failure=True,

        max_retries=1

    )


    report = executor.execute_plan(
        test_plan
    )


    # -----------------------------------------------------
    # PRINT FINAL STATE
    # -----------------------------------------------------

    print()

    print(
        executor.get_summary()
    )


    # -----------------------------------------------------
    # PRINT REPORT
    # -----------------------------------------------------

    print_execution_report(
        report
    )

    print()

    print(
        "=" * 65
    )

    print(
        "State-aware executor test completed."
    )

    print(
        "=" * 65
    )
