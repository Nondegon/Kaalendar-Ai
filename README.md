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
pip install -r requirements.txt

# Set your Gemini API key
export GEMINI_API_KEY="YOUR_API_KEY_HERE"

# Activate the environment
source venv/bin/activate

# Pull latest updates
git pull

# Run the main program
python3 main.py

# Activate the environment
source venv/bin/activate

# Pull latest updates
git pull

# Run the main program
python3 main.py
