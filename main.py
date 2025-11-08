# main.py

import os
from dotenv import load_dotenv
import tkinter as tk
from tkinter import simpledialog, messagebox
import gemini
import calendarAlgo  # Ensure you have your interval scheduling logic here

# Load environment variables from .env file
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("GEMINI_API_KEY not set in environment variables.")

# Helper functions
def time_to_minutes(t):
    h, m = map(int, t.split(":"))
    return h * 60 + m

def minutes_to_time(m):
    h = m // 60
    m = m % 60
    return f"{h:02d}:{m:02d}"

# Main window
root = tk.Tk()
root.title("Schedule & Assignments")

# Store events and assignments
events = []
assignments = []

# --- Functions ---
def add_event():
    name = simpledialog.askstring("Event Name", "Enter event name:")
    start_time = simpledialog.askstring("Start Time", "Enter start time (HH:MM):")
    end_time = simpledialog.askstring("End Time", "Enter end time (HH:MM):")
    
    if name and start_time and end_time:
        events.append({"name": name, "start": start_time, "end": end_time})
        messagebox.showinfo("Event Added", f"{name}: {start_time} to {end_time}")

def add_assignments():
    desc_string = simpledialog.askstring(
        "Assignments", 
        "Enter assignment descriptions separated by ';' (semicolon):"
    )
    
    if not desc_string:
        return
    
    desc_list = [d.strip() for d in desc_string.split(";") if d.strip()]
    if not desc_list:
        messagebox.showwarning("No Assignments", "No valid assignments entered.")
        return

    # Get durations from Gemini API
    durations = gemini.prompt_gemini(desc_list, API_KEY)

    for desc, time_est in zip(desc_list, durations):
        if isinstance(time_est, list):
            time_est = time_est[0]
        assignments.append({"name": desc, "time": time_est})

    messagebox.showinfo(
        "Assignments Added",
        "\n".join([f"{a['name']}: {a['time']} mins" for a in assignments])
    )

def schedule_assignments():
    if not assignments:
        messagebox.showwarning("No Assignments", "Add assignments first!")
        return

    # Convert events to intervals in minutes
    taken_intervals = [(time_to_minutes(e["start"]), time_to_minutes(e["end"])) for e in events]
    durations = [a["time"] for a in assignments]

    # Generate intervals using your calendarAlgo
    intervals = calendarAlgo.generate_intervals(360, 24*60-1, taken_intervals, durations)
    
    if not intervals:
        messagebox.showinfo("Scheduling Failed", "Could not fit assignments into the day.")
        return

    # Combine events and scheduled assignments
    schedule_entries = []

    # Add scheduled assignments
    for a, (start, end) in zip(assignments, intervals):
        schedule_entries.append({
            "name": a["name"],
            "start": minutes_to_time(start),
            "end": minutes_to_time(end)
        })

    # Add events
    for e in events:
        schedule_entries.append({
            "name": e["name"],
            "start": e["start"],
            "end": e["end"]
        })

    # Sort by start time
    schedule_entries.sort(key=lambda x: time_to_minutes(x["start"]))

    # Display
    display_text = "\n".join([f"{entry['name']}: {entry['start']} to {entry['end']}" for entry in schedule_entries])
    messagebox.showinfo("Daily Planner", display_text)

# --- Buttons ---
tk.Button(root, text="Add Schedule Event", command=add_event).pack(pady=5)
tk.Button(root, text="Add Multiple Assignments", command=add_assignments).pack(pady=5)
tk.Button(root, text="Schedule Assignments", command=schedule_assignments).pack(pady=10)

root.mainloop()
