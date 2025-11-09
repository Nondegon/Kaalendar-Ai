# Kaalendar-AI

A daily planner and assignment scheduler for high-school students, integrating Google Gemini API to estimate assignment durations. Provides a visual schedule of events, assignments, and sleep blocks in a Tkinter GUI.

## Features

- Add assignments with Gemini AI estimated durations.
- Add custom events with start/end times.
- Schedule assignments around existing events.
- Daily sleep schedule blocking both night and morning.
- Displays schedule in format: `Name: HH:MM to HH:MM`.
- Interactive Tkinter GUI.

## Requirements

- Python 3.13+
- Dependencies:
  - `requests`
  - `python-dotenv`

Tkinter comes built-in with Python.

## Setup (One-Time)

```bash
# Clone the repo
git clone https://github.com/Nondegon/Kaalendar-Ai.git
cd Kaalendar-Ai

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install requests python-dotenv

# Set your Gemini API key
export GEMINI_API_KEY="YOUR_API_KEY_HERE"
```

## Running the App
```bash
# Activate the environment
source venv/bin/activate

# Pull latest updates
git pull

# Run the main program
python3 main.py
```
## Getting a Gemini API Key

1. Go to [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project (or select an existing one).
3. Enable the **Generative Language API** for your project.
4. Go to **APIs & Services > Credentials** and create an **API key**.
5. Copy the API key and set it in your environment:

```bash
export GEMINI_API_KEY="YOUR_API_KEY_HERE"
