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

# --- Tkinter setup ---
root = tk.Tk()
root.title("Kaalendar AI — Daily Planner")
root.geometry("600x700")

# --- Data storage ---
events = []
assignments = []
sleep_block = None
downtime = 5  # default downtime in minutes

# --- UI Elements ---
tk.Label(root, text="Assignments (one per line):", font=("Arial", 12, "bold")).pack(pady=5)
assignment_text = scrolledtext.ScrolledText(root, width=60, height=8, wrap=tk.WORD)
assignment_text.pack(pady=5)

# Buttons frame
button_frame = tk.Frame(root)
button_frame.pack(pady=10)

planner_box = scrolledtext.ScrolledText(root, width=60, height=20, wrap=tk.WORD, state="disabled")
planner_box.pack(pady=10)

# --- Core Functions ---
def refresh_planner_display():
    """Refresh the daily planner UI with events, assignments, and sleep."""
    planner_box.config(state="normal")
    planner_box.delete("1.0", tk.END)
    
    all_items = []
    if sleep_block:
        all_items.append({
            "name": "Sleep",
            "start": sleep_block["start"],
            "end": sleep_block["end"]
        })
    all_items.extend(events)
    all_items.extend(assignments)
    
    # Sort by start time
    all_items.sort(key=lambda x: time_to_minutes(x["start"]))
    
    for item in all_items:
        planner_box.insert(tk.END, f"{item['name']}: {item['start']} to {item['end']}\n")
    
    planner_box.config(state="disabled")

def add_event():
    start_time = simpledialog.askstring("Start Time", "Enter start time (HH:MM):")
    end_time = simpledialog.askstring("End Time", "Enter end time (HH:MM):")
    name = simpledialog.askstring("Event Name", "Enter event name:")
    
    if start_time and end_time and name:
        events.append({"name": name, "start": start_time, "end": end_time})
        refresh_planner_display()
        messagebox.showinfo("Event Added", f"{name}: {start_time} - {end_time}")

def add_sleep_schedule():
    start = simpledialog.askstring("Sleep Start", "Enter sleep start time (HH:MM):")
    end = simpledialog.askstring("Sleep End", "Enter wake-up time (HH:MM):")
    
    if start and end:
        global sleep_block
        sleep_block = {"start": start, "end": end}
        refresh_planner_display()
        messagebox.showinfo("Sleep Added", f"Sleep: {start} - {end}")

def set_downtime():
    global downtime
    val = simpledialog.askinteger("Downtime", "Enter downtime between assignments (in minutes):", minvalue=0, maxvalue=120)
    if val is not None:
        downtime = val
        messagebox.showinfo("Downtime Set", f"Downtime set to {downtime} minutes.")

def add_assignments():
    desc_list = [line.strip() for line in assignment_text.get("1.0", tk.END).splitlines() if line.strip()]
    if not desc_list:
        messagebox.showwarning("No Assignments", "Please enter at least one assignment.")
        return

    durations = gemini.prompt_gemini(desc_list, API_KEY)
    
    assignments.clear()
    for desc, time_est in zip(desc_list, durations):
        assignments.append({
            "name": desc,
            "time": time_est,
            "start": None,
            "end": None
        })
    
    messagebox.showinfo(
        "Assignments Added",
        "\n".join([f"{a['name']} - {a['time']} mins" for a in assignments])
    )

def schedule_assignments():
    if not assignments:
        messagebox.showwarning("No Assignments", "Add assignments first!")
        return

    taken_intervals = []
    if sleep_block:
        taken_intervals.append((time_to_minutes(sleep_block["start"]), time_to_minutes(sleep_block["end"])))
    for e in events:
        taken_intervals.append((time_to_minutes(e["start"]), time_to_minutes(e["end"])))
    
    durations = [a["time"] + downtime for a in assignments]  # Add downtime buffer

    intervals = calendarAlgo.generate_intervals(360, 24*60-1, taken_intervals, durations)
    
    if not intervals:
        messagebox.showinfo("Scheduling Failed", "Could not fit assignments into the day.")
        return

    for a, (start, end) in zip(assignments, intervals):
        a["start"] = minutes_to_time(start)
        a["end"] = minutes_to_time(end - downtime)  # exclude the buffer from display
        a["name"] = a["name"]

    refresh_planner_display()
    messagebox.showinfo("Schedule Updated", "Assignments scheduled successfully!")

# --- Buttons ---
tk.Button(button_frame, text="Add Event", command=add_event).grid(row=0, column=0, padx=5)
tk.Button(button_frame, text="Add Sleep Schedule", command=add_sleep_schedule).grid(row=0, column=1, padx=5)
tk.Button(button_frame, text="Set Downtime", command=set_downtime).grid(row=0, column=2, padx=5)
tk.Button(button_frame, text="Add Assignments", command=add_assignments).grid(row=0, column=3, padx=5)
tk.Button(button_frame, text="Schedule Assignments", command=schedule_assignments).grid(row=0, column=4, padx=5)

# --- Start ---
refresh_planner_display()
root.mainloop()
