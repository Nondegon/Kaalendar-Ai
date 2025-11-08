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
            # Make sure time_est is an integer
            if isinstance(time_est, list):
                time_est = time_est[0]
            assignments.append({"desc": desc, "time": time_est})
        
        # Display nicely
        messagebox.showinfo(
            "Assignments Added", 
            "\n".join([f"{a['desc']} - {a['time']} mins" for a in assignments])
        )

def schedule_assignments():
    if not assignments and not events:
        messagebox.showwarning("No Schedule", "Add assignments or events first!")
        return

    # Convert events to intervals in minutes
    taken_intervals = [(time_to_minutes(e["start"]), time_to_minutes(e["end"]), f"Event") for e in events]
    durations = [a["time"] for a in assignments]

    # Generate assignment intervals using your calendarAlgo
    assignment_intervals = calendarAlgo.generate_intervals(360, 24*60-1, [(s, e) for s, e, _ in taken_intervals], durations)
    if not assignment_intervals:
        messagebox.showinfo("Scheduling Failed", "Could not fit assignments into the day.")
        return

    # Combine assignments with events
    schedule_list = []

    for a, (start, end) in zip(assignments, assignment_intervals):
        schedule_list.append({
            "start": start,
            "end": end,
            "name": a["desc"]
        })

    # Add events
    for s, e, name in taken_intervals:
        schedule_list.append({
            "start": s,
            "end": e,
            "name": name
        })

    # Sort by start time
    schedule_list.sort(key=lambda x: x["start"])

    # Display in HH:MM to HH:MM format
    display_strings = [
        f"{item['name']}: {minutes_to_time(item['start'])} to {minutes_to_time(item['end'])}"
        for item in schedule_list
    ]

    # Show in messagebox
    messagebox.showinfo("Daily Schedule", "\n".join(display_strings))


def show_daily_planner(assignments, events):
    """
    Display a daily planner with hourly breakdown.
    """
    planner_root = tk.Toplevel()
    planner_root.title("Daily Planner")

    canvas = tk.Canvas(planner_root, width=400, height=600)
    scrollbar = tk.Scrollbar(planner_root, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    
    canvas.create_window((0,0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    # Convert events start/end to minutes
    events_minutes = [
        (time_to_minutes(e["start"]), time_to_minutes(e["end"]), e)
        for e in events
    ]

    # Convert assignments start/end to minutes
    assignments_minutes = [
        (a["start"], a["start"] + a["time"], a)
        for a in assignments if "start" in a
    ]

    for hour in range(24):
        frame = tk.Frame(scrollable_frame, borderwidth=1, relief="solid")
        frame.pack(fill="x")
        tk.Label(frame, text=f"{hour:02d}:00", width=10, anchor="w").pack(side="left")
        
        # Items in this hour
        items = []
        for start, end, a in assignments_minutes:
            if start // 60 <= hour < end // 60:
                items.append(f"[A] {a['desc']}")
        for start, end, e in events_minutes:
            if start // 60 <= hour < end // 60:
                items.append(f"[E] {e.get('title', 'Event')}")
        
        tk.Label(frame, text=", ".join(items)).pack(side="left")

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

# --- Buttons ---
tk.Button(root, text="Add Schedule Event", command=add_event).pack(pady=5)
tk.Button(root, text="Add Multiple Assignments", command=add_assignments).pack(pady=5)
tk.Button(root, text="Schedule Assignments", command=schedule_assignments).pack(pady=5)
tk.Button(root, text="View Daily Planner", command=lambda: show_daily_planner(assignments, events)).pack(pady=5)

# Run the GUI
root.mainloop()
