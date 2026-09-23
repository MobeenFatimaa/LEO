# =========================================================
# LEO 2.0 - Agent Workflows
# =========================================================

from tools.basic_tools import (
    open_application,
    open_folder,
    open_website,
    open_vscode,
)


# =========================================================
# CODING WORKSPACE
# =========================================================

def prepare_coding_workspace():

    results = []

    # -----------------------------------------------------
    # 1. VS CODE
    # -----------------------------------------------------

    result = open_vscode()

    results.append(
        f"VS Code: {result}"
    )

    # -----------------------------------------------------
    # 2. PROJECT FOLDER
    # -----------------------------------------------------

    result = open_folder(
        r"C:\Users\User\Desktop\LEO-my voice agent"
    )

    results.append(
        f"LEO project folder: {result}"
    )

    # -----------------------------------------------------
    # 3. CHROME
    # -----------------------------------------------------

    result = open_application(
        "Chrome"
    )

    results.append(
        f"Chrome: {result}"
    )

    # -----------------------------------------------------
    # 4. GITHUB
    # -----------------------------------------------------

    result = open_website(
        "github"
    )

    results.append(
        f"GitHub: {result}"
    )

    return (
        "Coding workspace preparation complete.\n\n"
        +
        "\n".join(results)
    )


# =========================================================
# AI / ML WORKSPACE
# =========================================================

def prepare_ai_workspace():

    results = []

    result = open_vscode()

    results.append(
        f"VS Code: {result}"
    )

    result = open_application(
        "Chrome"
    )

    results.append(
        f"Chrome: {result}"
    )

    result = open_website(
        "kaggle"
    )

    results.append(
        f"Kaggle: {result}"
    )

    return (
        "AI/ML workspace preparation complete.\n\n"
        +
        "\n".join(results)
    )


# =========================================================
# RESEARCH WORKSPACE
# =========================================================

def prepare_research_workspace():

    results = []

    result = open_application(
        "Chrome"
    )

    results.append(
        f"Chrome: {result}"
    )

    result = open_website(
        "google"
    )

    results.append(
        f"Google: {result}"
    )

    result = open_application(
        "Notepad"
    )

    results.append(
        f"Notepad: {result}"
    )

    return (
        "Research workspace preparation complete.\n\n"
        +
        "\n".join(results)
    )


# =========================================================
# STUDY WORKSPACE
# =========================================================

def prepare_study_workspace():

    results = []

    result = open_application(
        "Chrome"
    )

    results.append(
        f"Chrome: {result}"
    )

    result = open_application(
        "Notepad"
    )

    results.append(
        f"Notepad: {result}"
    )

    result = open_folder(
        "Documents"
    )

    results.append(
        f"Documents: {result}"
    )

    return (
        "Study workspace preparation complete.\n\n"
        +
        "\n".join(results)
    )


# =========================================================
# WORKFLOW ROUTER
# =========================================================

def run_workflow(
    workflow
):

    if not workflow:

        return "No workflow was specified."

    workflow = workflow.lower().strip()

    workflows = {

        "coding":
            prepare_coding_workspace,

        "coding workspace":
            prepare_coding_workspace,

        "development":
            prepare_coding_workspace,

        "developer":
            prepare_coding_workspace,

        "ai":
            prepare_ai_workspace,

        "ai workspace":
            prepare_ai_workspace,

        "machine learning":
            prepare_ai_workspace,

        "research":
            prepare_research_workspace,

        "research workspace":
            prepare_research_workspace,

        "study":
            prepare_study_workspace,

        "study workspace":
            prepare_study_workspace,
    }

    function = workflows.get(
        workflow
    )

    if function is None:

        return (
            f"Unknown workflow '{workflow}'. "
            "Available workflows: coding, AI, "
            "research and study."
        )

    try:

        return function()

    except Exception as error:

        return (
            f"Workflow '{workflow}' failed: {error}"
        )
