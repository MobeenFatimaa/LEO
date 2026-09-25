
# =========================================================
# LEO 2.5E
# Autonomous Task Engine
# =========================================================

from datetime import datetime

from planner import TaskPlanner

from task_executor import (
    TaskExecutor,
    STATUS_COMPLETED,
    STATUS_FAILED,
    STATUS_STOPPED,
)


# =========================================================
# ENGINE STATUS
# =========================================================

ENGINE_IDLE = "IDLE"

ENGINE_PLANNING = "PLANNING"

ENGINE_EXECUTING = "EXECUTING"

ENGINE_COMPLETED = "COMPLETED"

ENGINE_FAILED = "FAILED"

ENGINE_STOPPED = "STOPPED"


# =========================================================
# AUTONOMOUS TASK ENGINE
# =========================================================

class AutonomousTaskEngine:

    def __init__(
        self,
        tool_executor,
        planner=None,
        max_retries=1,
        stop_on_failure=True
    ):

        # -------------------------------------------------
        # TOOL EXECUTOR
        # -------------------------------------------------

        self.tool_executor = (
            tool_executor
        )

        # -------------------------------------------------
        # PLANNER
        # -------------------------------------------------

        self.planner = (
            planner
            if planner is not None
            else TaskPlanner()
        )

        # -------------------------------------------------
        # EXECUTOR
        # -------------------------------------------------

        self.executor = TaskExecutor(

            tool_executor=
                tool_executor,

            stop_on_failure=
                stop_on_failure,

            max_retries=
                max_retries

        )

        # -------------------------------------------------
        # STATE
        # -------------------------------------------------

        self.status = ENGINE_IDLE

        self.current_request = ""

        self.current_plan = None

        self.current_report = None

        self.started_at = None

        self.finished_at = None


    # =====================================================
    # RESET
    # =====================================================

    def reset(self):

        self.status = ENGINE_IDLE

        self.current_request = ""

        self.current_plan = None

        self.current_report = None

        self.started_at = None

        self.finished_at = None

        self.executor.reset()


    # =====================================================
    # CREATE PLAN
    # =====================================================

    def create_plan(
        self,
        user_request
    ):

        self.status = ENGINE_PLANNING

        self.current_request = (
            user_request
        )

        print()

        print(
            "=" * 65
        )

        print(
            "LEO TASK PLANNING"
        )

        print(
            "=" * 65
        )

        print(
            f"Request: {user_request}"
        )

        print()

        try:

            plan = self.planner.create_plan(
                user_request
            )

        except Exception as error:

            self.status = ENGINE_FAILED

            self.finished_at = (
                datetime.now().isoformat()
            )

            print(
                f"[ENGINE] "
                f"Planning failed: {error}"
            )

            return None

        self.current_plan = plan

        # -------------------------------------------------
        # CHECK PLAN
        # -------------------------------------------------

        if not isinstance(
            plan,
            dict
        ):

            self.status = ENGINE_FAILED

            print(
                "[ENGINE] Planner returned "
                "an invalid plan."
            )

            return None

        if plan.get("error"):

            self.status = ENGINE_FAILED

            print(
                "[ENGINE] Planner error:"
            )

            print(
                plan.get("error")
            )

            return None

        steps = plan.get(
            "steps",
            []
        )

        print()

        print(
            "[ENGINE] Plan created."
        )

        print(
            f"[ENGINE] Steps: "
            f"{len(steps)}"
        )

        for step in steps:

            print(
                f"  Step "
                f"{step.get('step')}: "
                f"{step.get('description', '')}"
            )

        return plan


    # =====================================================
    # EXECUTE CURRENT PLAN
    # =====================================================

    def execute_current_plan(self):

        if not self.current_plan:

            self.status = ENGINE_FAILED

            return None

        self.status = ENGINE_EXECUTING

        print()

        print(
            "=" * 65
        )

        print(
            "LEO AUTONOMOUS EXECUTION"
        )

        print(
            "=" * 65
        )

        try:

            report = self.executor.execute_plan(
                self.current_plan
            )

        except Exception as error:

            self.status = ENGINE_FAILED

            self.finished_at = (
                datetime.now().isoformat()
            )

            self.current_report = {

                "status":
                    ENGINE_FAILED,

                "error":
                    str(error),

                "goal":
                    self.current_plan.get(
                        "goal",
                        ""
                    )

            }

            print(
                f"[ENGINE] "
                f"Execution exception: {error}"
            )

            return self.current_report

        self.current_report = report

        self.finished_at = (
            datetime.now().isoformat()
        )

        executor_status = report.get(
            "status"
        )

        if executor_status == STATUS_COMPLETED:

            self.status = ENGINE_COMPLETED

        elif executor_status == STATUS_STOPPED:

            self.status = ENGINE_STOPPED

        else:

            self.status = ENGINE_FAILED

        return report


    # =====================================================
    # RUN COMPLETE TASK
    # =====================================================

    def run(
        self,
        user_request
    ):

        self.reset()

        self.started_at = (
            datetime.now().isoformat()
        )

        # -------------------------------------------------
        # VALIDATE REQUEST
        # -------------------------------------------------

        if not user_request:

            self.status = ENGINE_FAILED

            self.finished_at = (
                datetime.now().isoformat()
            )

            return {

                "status":
                    ENGINE_FAILED,

                "error":
                    "No task request was provided."

            }

        user_request = str(
            user_request
        ).strip()

        if not user_request:

            self.status = ENGINE_FAILED

            self.finished_at = (
                datetime.now().isoformat()
            )

            return {

                "status":
                    ENGINE_FAILED,

                "error":
                    "The task request was empty."

            }

        # -------------------------------------------------
        # PLAN
        # -------------------------------------------------

        plan = self.create_plan(
            user_request
        )

        if plan is None:

            return self.build_engine_report()

        # -------------------------------------------------
        # EXECUTE
        # -------------------------------------------------

        self.execute_current_plan()

        # -------------------------------------------------
        # FINAL REPORT
        # -------------------------------------------------

        return self.build_engine_report()


    # =====================================================
    # CANCEL
    # =====================================================

    def cancel(self):

        self.executor.request_cancel()

        self.status = ENGINE_STOPPED

        print()

        print(
            "[ENGINE] "
            "Cancellation requested."
        )


    # =====================================================
    # GET TASK STATE
    # =====================================================

    def get_task_state(self):

        return self.executor.get_state()


    # =====================================================
    # GET EXECUTION SUMMARY
    # =====================================================

    def get_summary(self):

        return self.executor.get_summary()


    # =====================================================
    # GET CURRENT PLAN
    # =====================================================

    def get_plan(self):

        return self.current_plan


    # =====================================================
    # GET CURRENT REPORT
    # =====================================================

    def get_report(self):

        return self.current_report


    # =====================================================
    # BUILD ENGINE REPORT
    # =====================================================

    def build_engine_report(self):

        report = {

            "status":
                self.status,

            "request":
                self.current_request,

            "plan":
                self.current_plan,

            "execution":
                self.current_report,

            "task_state":
                self.executor.get_state(),

            "started_at":
                self.started_at,

            "finished_at":
                self.finished_at,

        }

        if self.current_report:

            if self.current_report.get(
                "error"
            ):

                report["error"] = (
                    self.current_report[
                        "error"
                    ]
                )

        return report


# =========================================================
# SIMPLE RUN FUNCTION
# =========================================================

def run_task(
    user_request,
    tool_executor,
    max_retries=1,
    stop_on_failure=True
):

    engine = AutonomousTaskEngine(

        tool_executor=
            tool_executor,

        max_retries=
            max_retries,

        stop_on_failure=
            stop_on_failure

    )

    return engine.run(
        user_request
    )


# =========================================================
# HUMAN-READABLE RESULT
# =========================================================

def print_engine_report(
    report
):

    print()

    print(
        "=" * 65
    )

    print(
        "LEO AUTONOMOUS TASK REPORT"
    )

    print(
        "=" * 65
    )

    print(
        f"Status: "
        f"{report.get('status', 'UNKNOWN')}"
    )

    print(
        f"Request: "
        f"{report.get('request', '')}"
    )

    plan = report.get(
        "plan"
    )

    if plan:

        print()

        print(
            f"Goal: "
            f"{plan.get('goal', '')}"
        )

        print(
            f"Steps: "
            f"{len(plan.get('steps', []))}"
        )

    execution = report.get(
        "execution"
    )

    if execution:

        print()

        print(
            f"Successful steps: "
            f"{execution.get('successful_steps', 0)}"
        )

        print(
            f"Failed steps: "
            f"{execution.get('failed_steps', 0)}"
        )

        print(
            f"Stopped steps: "
            f"{execution.get('stopped_steps', 0)}"
        )

        progress = execution.get(
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
        "LEO 2.5E - Autonomous Task Engine Test"
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
            "[FAKE TOOL EXECUTION]"
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
    # FAKE PLANNER
    # -----------------------------------------------------

    class FakePlanner:

        def create_plan(
            self,
            user_request
        ):

            return {

                "goal":
                    user_request,

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

                            "application":
                                "Chrome"

                        },

                        "description":
                            "Open Chrome"

                    },

                    {
                        "step": 3,

                        "tool":
                            "open_website",

                        "arguments": {

                            "website":
                                "github"

                        },

                        "description":
                            "Open GitHub"

                    }

                ]

            }


    # -----------------------------------------------------
    # CREATE ENGINE
    # -----------------------------------------------------

    engine = AutonomousTaskEngine(

        tool_executor=
            fake_tool_executor,

        planner=
            FakePlanner(),

        max_retries=1,

        stop_on_failure=True

    )


    # -----------------------------------------------------
    # RUN
    # -----------------------------------------------------

    report = engine.run(
        "Prepare my coding workspace"
    )


    # -----------------------------------------------------
    # PRINT REPORT
    # -----------------------------------------------------

    print_engine_report(
        report
    )

    print()

    print(
        "=" * 65
    )

    print(
        "Autonomous task engine test completed."
    )

    print(
        "=" * 65
    )

