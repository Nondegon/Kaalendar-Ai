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
    if m >= 1440:
        return "24:00"
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
tk.Label(root, text="Assignments (one per line). Use the format TITLE | DESCRIPTION:", font=("Arial", 12, "bold")).pack(pady=5)
assignment_text = scrolledtext.ScrolledText(root, width=60, height=8, wrap=tk.WORD)
assignment_text.pack(pady=5)

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

    # Handle sleep as recurring block
    if sleep_block:
        start_mins = time_to_minutes(sleep_block["start"])
        end_mins = time_to_minutes(sleep_block["end"])
        if end_mins < start_mins:  # crosses midnight
            all_items.append({"name": "Sleep (Night)", "start": sleep_block["start"], "end": "23:59"})
            all_items.append({"name": "Sleep (Morning)", "start": "00:00", "end": sleep_block["end"]})
        else:
            all_items.append({"name": "Sleep", "start": sleep_block["start"], "end": sleep_block["end"]})

    # Normalize events
    for e in events:
        all_items.append({
            "name": e.get("name", "Event"),
            "start": e.get("start", "--:--"),
            "end": e.get("end", "--:--")
        })

    # Normalize assignments
    for a in assignments:
        all_items.append({
            "name": a.get("name", "Assignment"),
            "start": a.get("start", "--:--"),
            "end": a.get("end", "--:--")
        })

    # Sort by start time (default to 0 if missing)
    def sort_key(x):
        try:
            return time_to_minutes(x["start"])
        except:
            return 0
    all_items.sort(key=sort_key)
    
    for item in all_items:
        planner_box.insert(tk.END, f"{item['name']}: {item['start']} to {item['end']}\n")
    
    planner_box.config(state="disabled")

def on_planner_click(event):
    global sleep_block
    index = planner_box.index(f"@{event.x},{event.y}")
    line_num = int(index.split('.')[0])
    line_text = planner_box.get(f"{line_num}.0", f"{line_num}.end").strip()
    if not line_text:
        return

    # Build all items normalized
    all_items = []
    if sleep_block:
        start_mins = time_to_minutes(sleep_block["start"])
        end_mins = time_to_minutes(sleep_block["end"])
        if end_mins < start_mins:
            all_items.append({"name": "Sleep (Night)", "start": sleep_block["start"], "end": "23:59"})
            all_items.append({"name": "Sleep (Morning)", "start": "00:00", "end": sleep_block["end"]})
        else:
            all_items.append({"name": "Sleep", "start": sleep_block["start"], "end": sleep_block["end"]})
    for e in events:
        all_items.append({"name": e.get("name", "Event"), "start": e.get("start", "--:--"), "end": e.get("end", "--:--")})
    for a in assignments:
        all_items.append({"name": a.get("name", "Assignment"), "start": a.get("start", "--:--"), "end": a.get("end", "--:--")})
    all_items.sort(key=lambda x: time_to_minutes(x["start"]))

    if line_num-1 >= len(all_items):
        return

    item = all_items[line_num-1]

    # Custom modify/delete dialog
    top = tk.Toplevel(root)
    top.title("Modify or Delete")
    tk.Label(top, text=f"What do you want to do with:\n{item['name']}: {item['start']} - {item['end']}?").pack(pady=10)
    
    def modify():
        top.destroy()
        new_name = simpledialog.askstring("Name", "Enter new name:", initialvalue=item["name"])
        new_start = simpledialog.askstring("Start Time", "Enter new start time (HH:MM):", initialvalue=item["start"])
        new_end = simpledialog.askstring("End Time", "Enter new end time (HH:MM):", initialvalue=item["end"])
        if new_name and new_start and new_end:
            if "Sleep" in item["name"]:
                sleep_block["start"] = new_start
                sleep_block["end"] = new_end
            else:
                for e in events:
                    if e.get("name") == item["name"] and e.get("start") == item["start"]:
                        e.update({"name": new_name, "start": new_start, "end": new_end})
                        break
                else:
                    for a in assignments:
                        if a.get("name") == item["name"] and a.get("start") == item["start"]:
                            a.update({"name": new_name, "start": new_start, "end": new_end})
                            break
        refresh_planner_display()
    
    def delete():
        top.destroy()
        if "Sleep" in item["name"]:
            sleep_block = None
        else:
            for e in events:
                if e.get("name") == item["name"] and e.get("start") == item["start"]:
                    events.remove(e)
                    break
            else:
                for a in assignments:
                    if a.get("name") == item["name"] and a.get("start") == item["start"]:
                        assignments.remove(a)
                        break
        refresh_planner_display()

    tk.Button(top, text="Modify", command=modify, width=10).pack(side="left", padx=10, pady=10)
    tk.Button(top, text="Delete", command=delete, width=10).pack(side="right", padx=10, pady=10)

def add_event():
    start_time = simpledialog.askstring("Start Time", "Enter start time (HH:MM):")
    end_time = simpledialog.askstring("End Time", "Enter end time (HH:MM):")
    name = simpledialog.askstring("Event Name", "Enter event name:")
    if start_time and end_time and name:
        events.append({"name": name, "start": start_time, "end": end_time})
        refresh_planner_display()
        messagebox.showinfo("Event Added", f"{name}: {start_time} - {end_time}")

def add_sleep_schedule():
    global sleep_block
    start = simpledialog.askstring("Sleep Start", "Enter the time at which you sleep (HH:MM):")
    end = simpledialog.askstring("Sleep End", "Enter wake-up time (HH:MM):")
    if start and end:
        sleep_block = {"start": start, "end": end}
        refresh_planner_display()
        messagebox.showinfo("Sleep Added", f"Sleep: {start} - {end} (recurring daily)")

def set_downtime():
    global downtime
    val = simpledialog.askinteger("Downtime", "Enter downtime between assignments (in minutes):", minvalue=0, maxvalue=120)
    if val is not None:
        downtime = val
        messagebox.showinfo("Downtime Set", f"Downtime set to {downtime} minutes.")

def add_assignments():
    raw_lines = [line.strip() for line in assignment_text.get("1.0", tk.END).splitlines() if line.strip()]
    if not raw_lines:
        messagebox.showwarning("No Assignments", "Please enter at least one assignment.")
        return

    titles = []
    descriptions = []

    for line in raw_lines:
        if "|" in line:
            title, desc = map(str.strip, line.split("|", 1))
        else:  # fallback: title = description if no |
            title = desc = line
        titles.append(title)
        descriptions.append(desc)

    # Call Gemini to estimate times based on descriptions
    durations = gemini.prompt_gemini(descriptions, API_KEY)

    # Save assignments
    assignments.clear()
    for title, desc, time_est in zip(titles, descriptions, durations):
        assignments.append({
            "name": title,      # displayed in planner
            "desc": desc,       # stored for reference / Gemini
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

    # --- Build taken intervals including sleep and events ---
    taken_intervals = []
    if sleep_block:
        start_mins = time_to_minutes(sleep_block["start"])
        end_mins = time_to_minutes(sleep_block["end"])
        if end_mins < start_mins:  # crosses midnight
            taken_intervals.append((start_mins, 24*60))  # night part
            taken_intervals.append((0, end_mins))        # morning part
        else:
            taken_intervals.append((start_mins, end_mins))
    for e in events:
        taken_intervals.append((time_to_minutes(e["start"]), time_to_minutes(e["end"])))

    # --- Sort intervals and add downtime padding ---
    taken_intervals.sort()
    buffered_intervals = []
    for start, end in taken_intervals:
        buffered_start = max(0, start - downtime)   # buffer before the block
        buffered_end = min(24*60, end + downtime)  # buffer after the block
        buffered_intervals.append((buffered_start, buffered_end))

    # --- Prepare assignment durations ---
    durations = [a["time"] for a in assignments]  # raw durations

    # --- Generate intervals considering all buffered intervals ---
    intervals = calendarAlgo.generate_intervals(360, 24*60, buffered_intervals, durations)
    if not intervals:
        messagebox.showinfo("Scheduling Failed", "Could not fit assignments into the day.")
        return

    # --- Assign start/end times while respecting downtime between assignments ---
    latest_end = 0
    for a, (start, end) in zip(assignments, intervals):
        # Start after previous assignment + downtime
        start_with_downtime = max(start, latest_end + downtime)

        # End time capped at 24*60
        end_time = min(start_with_downtime + a["time"], 24*60)

        a["start"] = minutes_to_time(start_with_downtime)
        a["end"] = minutes_to_time(end_time)

        latest_end = end_time  # update for next assignment

    # --- Refresh UI ---
    refresh_planner_display()
    messagebox.showinfo("Schedule Updated", "Assignments scheduled successfully!")

# --- Buttons ---
planner_box.bind("<Button-1>", on_planner_click)
tk.Button(button_frame, text="Add Event", command=add_event).grid(row=0, column=0, padx=5)
tk.Button(button_frame, text="Add Sleep Schedule", command=add_sleep_schedule).grid(row=0, column=1, padx=5)
tk.Button(button_frame, text="Set Downtime", command=set_downtime).grid(row=0, column=2, padx=5)
tk.Button(button_frame, text="Add Assignments", command=add_assignments).grid(row=0, column=3, padx=5)
tk.Button(button_frame, text="Schedule Assignments", command=schedule_assignments).grid(row=0, column=4, padx=5)

# --- Start ---
refresh_planner_display()
root.mainloop()
