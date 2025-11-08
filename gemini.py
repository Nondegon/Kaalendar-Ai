# gemini.py

import requests
import json
import re
import tkinter as tk
from tkinter import simpledialog, messagebox

def prompt_gemini(descriptions, api_key, model="gemini-2.0-flash"):
    """
    Ask Gemini API to estimate assignment lengths (minutes) for each description.
    If the API call or parsing fails, fallback to prompting the user.
    """

    # Build prompt string from descriptions
    string = "\n".join(f"{i+1}. {d}" for i, d in enumerate(descriptions))
    prompt_text = (
        "You are a smart planner for a high‐school student. "
        "You are given a series of descriptions of assignments, "
        "and your goal is to estimate the assignment lengths of each assignment.\n"
        "Return your estimations in the form of a list of integers (minutes). "
        "Important guidelines:\n"
        "1. Length of the list must match the number of assignments.\n"
        "2. Provide ONLY a list of integers. Example: [20,30,40,50]\n"
        "3. The list must correspond to the assignments in order.\n"
        "Assignments:\n" + string
    )

    # New endpoint (v1beta)
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent?key={api_key}"
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": api_key
        # Alternative: If docs require Authorization Bearer token, use:
        # "Authorization": f"Bearer {api_key}"
    }

    # Request body per Gemini docs
    data = {
        "contents": [
            {
                "parts": [
                    {"text": prompt_text}
                ]
            }
        ],
        "generationConfig": {
            "maxOutputTokens": 500,
            "temperature": 0.6
        }
    }

    # Send request
    resp = requests.post(url, headers=headers, data=json.dumps(data))
    if resp.status_code != 200:
        print("Gemini API error:", resp.status_code, resp.text)
        return fallback_durations(len(descriptions))

    resp_json = resp.json()
    # Extract the content of the first candidate
    try:
        candidate = resp_json["candidates"][0]
        # We expect the content as a string with list of ints
        text_output = candidate.get("content", "")
    except (KeyError, IndexError) as e:
        print("Gemini response parsing error:", resp_json)
        return fallback_durations(len(descriptions))

    # Try to parse list of integers
    match = re.search(r"\[\s*(\d+(?:\s*,\s*\d+)*)\s*\]", text_output)
    if match:
        numbers_str = match.group(1)
        numbers_list = [int(n) for n in re.findall(r"\d+", numbers_str)]
        if len(numbers_list) == len(descriptions):
            return numbers_list

    # If parsing failed
    print("Could not parse Gemini response:", text_output)
    return fallback_durations(len(descriptions))


def fallback_durations(count):
    """
    Ask user for default duration to use if API fails.
    """
    root = tk.Tk()
    root.withdraw()  # hide main window
    answer = simpledialog.askinteger(
        "Fallback Duration",
        f"Enter a default duration (in minutes) for each of the {count} assignments:",
        minvalue=1, maxvalue=480
    )
    root.destroy()

    if answer is None:
        answer = 30
    return [answer] * count
