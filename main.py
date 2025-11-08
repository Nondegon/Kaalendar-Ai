# main.py (with Sleep Schedule button)

import os
from dotenv import load_dotenv
import tkinter as tk
from tkinter import simpledialog, messagebox, scrolledtext
import calendarAlgo
import gemini

# Load environment variables
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("GEMINI_API_KEY not set in environment variables.")

# --- Helper functions ---
def time_to_minutes(t):
    h, m = map(int, t.split(":"))
    return h * 60 + m

def minutes_to_time(m):
    h = m // 60
    m = m % 60
    return f"{h:02d}:{m:02d}"

# --- Main window ---
root = tk.Tk()
root.title("Schedule & Assignments")
root.geometry("450x600")

# Store events and assignments
events = []
assignments = []

# --- Planner display ---
planner_frame = tk.Frame(root)
planner_frame.pack(fill="both", expand=True, padx=5, pady=5)

planner_text = scrolledtext.ScrolledText(planner_frame, width=50, height=30)
planner_text.pack(fill="both", expand=True)

def update_planner_display():
    """Display all events and assignments in planner_text."""
    planner_text.delete("1.0", tk.END)
    items = []

    # Collect events
    for e in events:
        items.append((time_to_minutes(e["start"]), time_to_minutes(e["end"]), 
                      f"Event '{e['name']}': {e['start']} - {e['end']}"))

    # Collect assignments
    for a in assignments:
        start_min = a.get("scheduled_start", None)
        end_min = a.get("scheduled_end", None)
        if start_min is not None and end_min is not None:
            items.append((start_min, end_min, 
                          f"Assignment '{a['title']}': {minutes_to_time(start_min)} - {minutes_to_time(end_min)}"))
        else:
            items.append((0, 0, f"Assignment '{a['title']}': {a['time']} mins (not scheduled)"))

    # Sort by start time
    items.sort(key=lambda x: x[0])
    for _, _, line in items:
        planner_text.insert(tk.END, line + "\n")

# --- Buttons ---
def add_event():
    name = simpledialog.askstring("Event Name", "Enter event name/title:")
    start_time = simpledialog.askstring("Start Time", "Enter start time (HH:MM):")
    end_time = simpledialog.askstring("End Time", "Enter end time (HH:MM):")
    
    if name and start_time and end_time:
        events.append({"name": name, "start": start_time, "end": end_time})
        update_planner_display()
        messagebox.showinfo("Event Added", f"Event '{name}': {start_time} - {end_time}")

def add_sleep_schedule():
    """Add daily sleep event that spans overnight if needed."""
    start_time = simpledialog.askstring("Sleep Start", "Enter sleep start time (HH:MM):")
    if not start_time:
        return

    hours_str = simpledialog.askstring("Sleep Duration", "Enter number of hours to sleep (e.g., 8):")
    if not hours_str or not hours_str.isdigit():
        messagebox.showwarning("Invalid Input", "Please enter a valid number of hours.")
        return

    hours = int(hours_str)
    start_minutes = time_to_minutes(start_time)
    end_minutes = start_minutes + hours * 60

    if end_minutes <= 24*60:
        # Sleep does not cross midnight
        events.append({"name": "Sleep", "start": start_time, "end": minutes_to_time(end_minutes)})
    else:
        # Sleep crosses midnight: split into two intervals
        events.append({"name": "Sleep", "start": start_time, "end": "24:00"})
        events.append({"name": "Sleep", "start": "00:00", "end": minutes_to_time(end_minutes % (24*60))})

    update_planner_display()
    messagebox.showinfo("Sleep Scheduled", f"Sleep added from {start_time} for {hours} hours")

def add_assignments():
    title_string = simpledialog.askstring(
        "Assignment Titles", 
        "Enter assignment titles separated by ';' (semicolon):"
    )
    
    if title_string:
        title_list = [t.strip() for t in title_string.split(";") if t.strip()]
        if not title_list:
            messagebox.showwarning("No Assignments", "No valid assignment titles entered.")
            return
        
        desc_string = simpledialog.askstring(
            "Assignment Descriptions", 
            "Enter descriptions for assignments separated by ';' (semicolon), in the same order:"
        )
        if not desc_string:
            messagebox.showwarning("No Descriptions", "No valid descriptions entered.")
            return
        
        desc_list = [d.strip() for d in desc_string.split(";") if d.strip()]
        if len(desc_list) != len(title_list):
            messagebox.showwarning("Mismatch", "Number of descriptions must match number of titles.")
            return

        # Query Gemini for estimated durations
        durations = gemini.prompt_gemini(desc_list, API_KEY)
        
        # Store assignments
        for title, desc, time_est in zip(title_list, desc_list, durations):
            if isinstance(time_est, list):
                time_est = time_est[0]
            assignments.append({"title": title, "desc": desc, "time": time_est})
        
        update_planner_display()
        messagebox.showinfo(
            "Assignments Added", 
            "\n".join([f"{a['title']}: {a['time']} mins" for a in assignments])
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
    
    # Store scheduled times in assignments
    for a, (start, end) in zip(assignments, intervals):
        a["scheduled_start"] = start
        a["scheduled_end"] = end
    
    update_planner_display()
    messagebox.showinfo("Schedule Complete", "Assignments have been scheduled!")

# --- Buttons ---
tk.Button(root, text="Add Schedule Event", command=add_event).pack(pady=5)
tk.Button(root, text="Add Sleep Schedule", command=add_sleep_schedule).pack(pady=5)
tk.Button(root, text="Add Multiple Assignments", command=add_assignments).pack(pady=5)
tk.Button(root, text="Schedule Assignments", command=schedule_assignments).pack(pady=5)

# Run GUI
update_planner_display()
root.mainloop()
