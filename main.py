import os
from dotenv import load_dotenv
import tkinter as tk
from tkinter import simpledialog, messagebox
import calendarAlgo
import gemini

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

# Create main window
root = tk.Tk()
root.title("Schedule & Assignments")

# Store events and assignments
events = []
assignments = []

# --- Functions ---

def add_event():
    start_time = simpledialog.askstring("Start Time", "Enter start time (HH:MM):")
    end_time = simpledialog.askstring("End Time", "Enter end time (HH:MM):")
    
    if start_time and end_time:
        events.append({"start": start_time, "end": end_time})
        messagebox.showinfo("Event Added", f"Event: {start_time} - {end_time}")

def add_assignments():
    desc_string = simpledialog.askstring(
        "Assignments", 
        "Enter assignment descriptions separated by ';' (semicolon):"
    )
    
    if desc_string:
        desc_list = [d.strip() for d in desc_string.split(";") if d.strip()]
        if not desc_list:
            messagebox.showwarning("No Assignments", "No valid assignments entered.")
            return
        
        # Query Gemini for estimated durations
        durations = gemini.prompt_gemini(desc_list, API_KEY)
        
        # Store assignments
        for desc, time_est in zip(desc_list, durations):
            # Make sure time_est is an integer, not a list
            if isinstance(time_est, list):
                time_est = time_est[0]
            assignments.append({"desc": desc, "time": time_est})
        
        # Display nicely
        messagebox.showinfo(
            "Assignments Added", 
            "\n".join([f"{a['desc']} - {a['time']} mins" for a in assignments])
        )

def schedule_assignments():
    if not assignments:
        messagebox.showwarning("No Assignments", "Add assignments first!")
        return
    
    # Convert events to taken intervals in minutes
    taken_intervals = [(time_to_minutes(e["start"]), time_to_minutes(e["end"])) for e in events]
    durations = [a["time"] for a in assignments]
    
    # Generate intervals using calendarAlgo
    intervals = calendarAlgo.generate_intervals(0, 24*60-1, taken_intervals, durations)
    
    if not intervals:
        messagebox.showinfo("Scheduling Failed", "Could not fit assignments into the day.")
        return
    
    # Show scheduled assignments
    schedule_strings = []
    for a, (start, end) in zip(assignments, intervals):
        schedule_strings.append(f"{minutes_to_time(start)} - {minutes_to_time(end)}: {a['desc']}")
    
    messagebox.showinfo("Schedule", "\n".join(schedule_strings))

# --- Buttons ---
tk.Button(root, text="Add Schedule Event", command=add_event).pack(pady=5)
tk.Button(root, text="Add Multiple Assignments", command=add_assignments).pack(pady=5)
tk.Button(root, text="Schedule Assignments", command=schedule_assignments).pack(pady=10)

# Run the GUI
root.mainloop()
