
# =========================================================
# LEO 2.5B
# Task Executor
# =========================================================

from datetime import datetime


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
        stop_on_failure=True
    ):
        """
        tool_executor:
            A function that receives:

                tool_name
                arguments

            and returns the tool result.

        stop_on_failure:
            If True, execution stops when a step fails.
        """

        self.tool_executor = tool_executor

        self.stop_on_failure = (
            stop_on_failure
        )

        self.current_plan = None

        self.execution_results = []

        self.status = STATUS_PENDING

        self.started_at = None

        self.finished_at = None


    # =====================================================
    # RESET
    # =====================================================

    def reset(self):

        self.current_plan = None

        self.execution_results = []

        self.status = STATUS_PENDING

        self.started_at = None

        self.finished_at = None


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
    # EXECUTE SINGLE STEP
    # =====================================================

    def execute_step(
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
            "-" * 60
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
            "-" * 60
        )

        started_at = datetime.now().isoformat()

        try:

            result = self.tool_executor(
                tool_name,
                arguments
            )

            success = not self.is_tool_failure(
                result
            )

            if success:

                step_status = STATUS_SUCCESS

            else:

                step_status = STATUS_FAILED

        except Exception as error:

            result = (
                f"Tool execution exception: {error}"
            )

            success = False

            step_status = STATUS_FAILED

        finished_at = datetime.now().isoformat()

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
                error="Plan must be a dictionary."
            )

        if plan.get("error"):

            self.status = STATUS_FAILED

            self.finished_at = (
                datetime.now().isoformat()
            )

            return self.build_report(
                error=plan.get("error")
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
                error="Plan steps must be a list."
            )

        if not steps:

            self.status = STATUS_COMPLETED

            self.finished_at = (
                datetime.now().isoformat()
            )

            return self.build_report(
                message="No execution steps were required."
            )

        # -------------------------------------------------
        # START EXECUTION
        # -------------------------------------------------

        self.status = STATUS_RUNNING

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
            f"Goal: {plan.get('goal', '')}"
        )

        print(
            f"Steps: {len(steps)}"
        )

        print(
            "=" * 65
        )

        # -------------------------------------------------
        # EXECUTE EACH STEP
        # -------------------------------------------------

        for step in steps:

            result = self.execute_step(
                step
            )

            if result["status"] == STATUS_FAILED:

                print()

                print(
                    f"[EXECUTOR] "
                    f"Step {result['step']} failed."
                )

                if self.stop_on_failure:

                    self.status = STATUS_FAILED

                    self.finished_at = (
                        datetime.now().isoformat()
                    )

                    return self.build_report(
                        error=(
                            f"Execution stopped because "
                            f"step {result['step']} failed."
                        )
                    )

        # -------------------------------------------------
        # ALL STEPS COMPLETED
        # -------------------------------------------------

        self.status = STATUS_COMPLETED

        self.finished_at = (
            datetime.now().isoformat()
        )

        print()

        print(
            "=" * 65
        )

        print(
            "LEO TASK EXECUTION COMPLETED"
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

        for result in self.execution_results:

            if result["status"] == STATUS_SUCCESS:

                successful_steps += 1

            elif result["status"] == STATUS_FAILED:

                failed_steps += 1

        report = {
            "goal": (
                self.current_plan.get(
                    "goal",
                    ""
                )
                if isinstance(
                    self.current_plan,
                    dict
                )
                else ""
            ),

            "status": self.status,

            "total_steps": len(
                self.current_plan.get(
                    "steps",
                    []
                )
            )
            if isinstance(
                self.current_plan,
                dict
            )
            else 0,

            "successful_steps": successful_steps,

            "failed_steps": failed_steps,

            "results": self.execution_results,

            "started_at": self.started_at,

            "finished_at": self.finished_at,
        }

        if error:

            report["error"] = error

        if message:

            report["message"] = message

        return report


# =========================================================
# SIMPLE EXECUTION FUNCTION
# =========================================================

def execute_plan(
    plan,
    tool_executor,
    stop_on_failure=True
):

    executor = TaskExecutor(
        tool_executor=tool_executor,
        stop_on_failure=stop_on_failure
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
        "LEO 2.5B - Task Executor Test"
    )

    print(
        "=" * 65
    )

    # -----------------------------------------------------
    # FAKE TOOL EXECUTOR
    # -----------------------------------------------------
    #
    # This is intentionally NOT connected to Windows.
    #
    # We first test the executor's logic safely.
    #

    def fake_tool_executor(
        tool_name,
        arguments
    ):

        print(
            f"\n[FAKE TOOL]"
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

        "goal": (
            "Prepare a development workspace"
        ),

        "steps": [

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

                "tool": "open_application",

                "arguments": {
                    "application": "Chrome"
                },

                "description": (
                    "Open Google Chrome"
                )
            },

            {
                "step": 3,

                "tool": "open_website",

                "arguments": {
                    "website": "github"
                },

                "description": (
                    "Open GitHub"
                )
            }
        ]
    }


    # -----------------------------------------------------
    # EXECUTE TEST
    # -----------------------------------------------------

    report = execute_plan(
        test_plan,
        fake_tool_executor
    )


    # -----------------------------------------------------
    # DISPLAY REPORT
    # -----------------------------------------------------

    print_execution_report(
        report
    )

