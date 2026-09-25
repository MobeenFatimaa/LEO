# LEO — Personal AI Voice Assistant

LEO is a Python-based personal AI voice assistant designed to provide natural voice interaction, AI-powered responses, memory, desktop control, utility tools, and contextual assistance from a local Windows environment.

LEO combines speech recognition, text-to-speech, Google's Gemini API, utility tools, memory functions, and desktop automation into a single extensible assistant.

---

## Overview

LEO is designed as a practical desktop AI assistant rather than a simple chatbot.

You can communicate with LEO using your voice, ask questions, perform calculations, open websites, retrieve useful information, store or retrieve memories, and interact with supported desktop functionality.

The project is built with Python and is designed to be modular so additional capabilities can be added over time.

---

##  Features

###  Voice Interaction

* Speech-to-text input
* Text-to-speech responses
* Natural conversational interaction
* Continuous assistant workflow

###  AI-Powered Responses

* Powered by Google's Gemini API
* Natural-language understanding
* Context-aware responses
* General-purpose question answering

###  Memory System

LEO includes a memory layer that allows supported information to be stored and retrieved.

Example capabilities include:

* Remembering user-provided facts
* Retrieving stored information
* Forgetting previously stored information
* Viewing stored memories

###  Desktop & Utility Control

LEO can perform supported utility actions such as:

* Opening websites
* Getting the current time
* Performing calculations
* Executing supported desktop actions

###  Tool-Based Architecture

LEO uses separate tools/functions for specific capabilities.

This makes the assistant easier to:

* Extend
* Debug
* Maintain
* Customize

###  Environment-Based Configuration

Sensitive configuration such as API keys is stored through environment variables rather than being hard-coded into the source code.

---

##  Technology Stack

| Technology            | Purpose                     |
| --------------------- | --------------------------- |
| Python                | Core application            |
| Google Gemini API     | AI responses                |
| SpeechRecognition     | Speech-to-text              |
| PyAudio               | Microphone input            |
| pyttsx3               | Text-to-speech              |
| python-dotenv         | Environment configuration   |
| Web/browser utilities | Website and desktop actions |

---

##  Requirements

Before installing LEO, make sure you have:

* Windows 10/11
* Python 3.10 or compatible Python version
* A working microphone
* Speakers or headphones
* Internet connection
* A Google Gemini API key

---

#  Installation

## 1. Clone the repository

```bash
git clone https://github.com/MobeenFatimaa/LEO.git
```

Move into the project directory:

```bash
cd LEO
```

---

## 2. Create a virtual environment

Create a Python virtual environment:

```bash
python -m venv .venv
```

Activate it in PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

If activation is successful, your terminal should show something similar to:

```text
(.venv)
```

---

## 3. Install dependencies

Install the required Python packages:

```bash
pip install -r requirements.txt
```

---

## 4. Configure the environment

Create a file named:

```text
.env
```

inside the project root.

Add your Gemini API key:

```env
GEMINI_API_KEY=your_api_key_here
```

Replace:

```text
your_api_key_here
```

with your actual API key.

### Important

Never publish your real API key to GitHub.

The `.env` file should remain private and should be excluded through `.gitignore`.

---

#  Running LEO

After completing the installation and environment configuration, run:

```bash
python main.py
```

LEO should initialize and begin its assistant workflow.

Make sure your microphone is connected and accessible by Windows.

---

#  Example Interactions

Depending on the enabled tools and configuration, you can interact with LEO using commands such as:

```text
What time is it?

Open YouTube.

Calculate 25 * 48.

Remember that my favorite programming language is Python.

What do you remember about me?

Forget that my favorite programming language is Python.
```

You can also ask general questions and have normal conversations with the AI assistant.

---

#  Memory

LEO includes a memory system that provides persistent storage for supported user-provided facts.

The memory functionality includes operations for:

* Remembering information
* Retrieving information
* Forgetting information
* Listing stored memories

This allows LEO to maintain useful information across interactions.

---

#  Project Architecture

LEO is organized around a modular assistant architecture.

```text
User
 │
 ▼
Microphone
 │
 ▼
Speech Recognition
 │
 ▼
LEO Core
 │
 ├── Gemini AI
 │
 ├── Memory System
 │
 ├── Utility Tools
 │
 └── Desktop Actions
 │
 ▼
Response
 │
 ▼
Text-to-Speech
 │
 ▼
User
```

The architecture is designed so additional tools and capabilities can be integrated without rewriting the entire assistant.

---

#  Project Structure

A simplified representation of the project:

```text
LEO/
│
├── main.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
│
├── tools/
│   └── ...
│
├── memory/
│   └── ...
│
└── ...
```

The exact structure may evolve as new capabilities are added.

---

#  Security

LEO requires an API key to access Gemini-powered functionality.

Do not commit sensitive credentials to GitHub.

Your `.env` file should contain your private credentials locally:

```env
GEMINI_API_KEY=your_private_key
```

Never replace the placeholder in `.env.example` with your real API key before committing it.

If an API key is accidentally exposed, revoke or rotate it immediately through the relevant provider.

---

#  Troubleshooting

## Microphone is not detected

Make sure:

1. Your microphone is connected.
2. Windows has microphone permissions enabled.
3. The correct microphone is selected as the Windows input device.
4. Required audio dependencies are installed.

You can verify the installed packages with:

```bash
pip list
```

---

## Python command is not recognized

Verify Python installation:

```bash
python --version
```

If Python is installed but the command is unavailable, check that Python has been added to your system PATH.

---

## Gemini API errors

Check that:

* Your `.env` file exists.
* The variable name is correct.
* Your API key is valid.
* Your internet connection is working.
* The required Gemini API access is available for your account.

---

## Dependency errors

Make sure the virtual environment is activated:

```powershell
.venv\Scripts\Activate.ps1
```

Then reinstall dependencies:

```bash
pip install -r requirements.txt
```

---

#  Future Improvements

Possible future development areas include:

* Expanded desktop automation
* More external tools
* Improved conversational context
* Additional memory capabilities
* Custom wake-word support
* More advanced system controls
* Local/offline AI capabilities
* Improved error handling
* Configurable assistant personality
* Plugin-style tool architecture

---

#  Author

**Mobeen Fatima**

AI / Machine Learning Developer

GitHub:
https://github.com/MobeenFatimaa

LinkedIn:
https://www.linkedin.com/in/mobeen-fatima-599a35347/

Portfolio:
https://mobeenfatima.netlify.app/

---

#  License

This project is distributed under the license included in this repository.

See the `LICENSE` file for details.

---

## ⭐ Support the Project

If you find LEO interesting or useful, consider giving the repository a ⭐ on GitHub.

Contributions, suggestions, and improvements are welcome.
