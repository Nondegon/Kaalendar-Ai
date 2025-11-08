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

# Global storage
events = []
assignments = []
downtime_minutes = 5  # default downtime between tasks

# Helper functions
def time_to_minutes(t):
    h, m = map(int, t.split(":"))
    return h * 60 + m

def minutes_to_time(m):
    h = m // 60
    m = m % 60
    return f"{h:02d}:{m:02d}"

# --- Core GUI setup ---
root = tk.Tk()
root.title("Kaalendar AI — Daily Planner")

# --- Functions ---

def add_event():
    name = simpledialog.askstring("Event Name", "Enter event name:")
    start_time = simpledialog.askstring("Start Time", "Enter start time (HH:MM):")
    end_time = simpledialog.askstring("End Time", "Enter end time (HH:MM):")

    if name and start_time and end_time:
        events.append({"name": name, "start": start_time, "end": end_time})
        messagebox.showinfo("Event Added", f"{name}: {start_time} - {end_time}")

def add_assignments():
    assign_window = tk.Toplevel(root)
    assign_window.title("Add Assignments")

    tk.Label(assign_window, text="Enter one assignment description per line:").pack(pady=5)

    text_box = scrolledtext.ScrolledText(assign_window, width=40, height=10, wrap=tk.WORD)
    text_box.pack(padx=10, pady=5)

    def submit_assignments():
        desc_list = [line.strip() for line in text_box.get("1.0", tk.END).splitlines() if line.strip()]
        if not desc_list:
            messagebox.showwarning("No Assignments", "Please enter at least one assignment.")
            return

        durations = gemini.prompt_gemini(desc_list, API_KEY)
        for desc, dur in zip(desc_list, durations):
            assignments.append({"desc": desc, "time": dur})

        messagebox.showinfo(
            "Assignments Added",
            "\n".join([f"{a['desc']} — {a['time']} mins" for a in assignments])
        )
        assign_window.destroy()

    tk.Button(assign_window, text="Submit", command=submit_assignments).pack(pady=5)

def add_sleep_schedule():
    start = simpledialog.askstring("Sleep Start", "Enter sleep start time (HH:MM):")
    end = simpledialog.askstring("Sleep End", "Enter wake-up time (HH:MM):")
    if start and end:
        events.append({"name": "Sleep", "start": start, "end": end})
        messagebox.showinfo("Sleep Schedule Added", f"Sleep: {start} to {end}")

def set_downtime():
    global downtime_minutes
    val = simpledialog.askinteger("Downtime", "Enter downtime between assignments (minutes):", minvalue=0, maxvalue=120)
    if val is not None:
        downtime_minutes = val
        messagebox.showinfo("Downtime Set", f"Downtime set to {downtime_minutes} minutes between assignments.")

def schedule_assignments():
    if not assignments:
        messagebox.showwarning("No Assignments", "Add assignments first!")
        return

    taken_intervals = [(time_to_minutes(e["start"]), time_to_minutes(e["end"])) for e in events]
    durations = [a["time"] + downtime_minutes for a in assignments]  # add downtime after each

    intervals = calendarAlgo.generate_intervals(360, 24*60-1, taken_intervals, durations)

    if not intervals:
        messagebox.showinfo("Scheduling Failed", "Could not fit assignments into the day.")
        return

    schedule_strings = []
    for a, (start, end) in zip(assignments, intervals):
        actual_end = end - downtime_minutes if downtime_minutes else end
        schedule_strings.append(f"{minutes_to_time(start)} - {minutes_to_time(actual_end)}: {a['desc']}")

    messagebox.showinfo("Today's Schedule", "\n".join(schedule_strings))

# --- Buttons ---
tk.Button(root, text="Add Event", command=add_event).pack(pady=5)
tk.Button(root, text="Add Assignments", command=add_assignments).pack(pady=5)
tk.Button(root, text="Add Sleep Schedule", command=add_sleep_schedule).pack(pady=5)
tk.Button(root, text="Set Downtime Between Tasks", command=set_downtime).pack(pady=5)
tk.Button(root, text="Schedule Assignments", command=schedule_assignments).pack(pady=10)

# --- Run the app ---
root.mainloop()
