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

    # Build all items with normalized keys
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
        all_items.append({
            "name": e.get("name", "Event"),
            "start": e.get("start", "--:--"),
            "end": e.get("end", "--:--")
        })
    for a in assignments:
        all_items.append({
            "name": a.get("name", "Assignment"),
            "start": a.get("start", "--:--"),
            "end": a.get("end", "--:--")
        })
    all_items.sort(key=lambda x: time_to_minutes(x["start"]))

    if line_num-1 >= len(all_items):
        return

    item = all_items[line_num-1]

    action = messagebox.askquestion(
        "Modify or Delete",
        f"Do you want to modify or delete:\n{item['name']}: {item['start']} - {item['end']}?",
        icon="question"
    )

    if action == "yes":
        new_name = simpledialog.askstring("Name", "Enter new name:", initialvalue=item["name"])
        new_start = simpledialog.askstring("Start Time", "Enter new start time (HH:MM):", initialvalue=item["start"])
        new_end = simpledialog.askstring("End Time", "Enter new end time (HH:MM):", initialvalue=item["end"])
        if new_name and new_start and new_end:
            if "Sleep" in item["name"]:
                sleep_block["start"] = new_start
                sleep_block["end"] = new_end
            else:
                # Update events
                for e in events:
                    if e.get("name") == item["name"] and e.get("start") == item["start"]:
                        e["name"] = new_name
                        e["start"] = new_start
                        e["end"] = new_end
                        break
                else:
                    # Update assignments
                    for a in assignments:
                        if a.get("name") == item["name"] and a.get("start") == item["start"]:
                            a["name"] = new_name
                            a["start"] = new_start
                            a["end"] = new_end
                            break
    else:
        # Delete
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
    start = simpledialog.askstring("Sleep Start", "Enter sleep start time (HH:MM):")
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
    desc_list = [line.strip() for line in assignment_text.get("1.0", tk.END).splitlines() if line.strip()]
    if not desc_list:
        messagebox.showwarning("No Assignments", "Please enter at least one assignment.")
        return

    durations = gemini.prompt_gemini(desc_list, API_KEY)
    assignments.clear()
    for desc, time_est in zip(desc_list, durations):
        assignments.append({"name": desc, "time": time_est, "start": None, "end": None})

    messagebox.showinfo(
        "Assignments Added",
        "\n".join([f"{a['name']} - {a['time']} mins" for a in assignments])
    )

def schedule_assignments():
    if not assignments:
        messagebox.showwarning("No Assignments", "Add assignments first!")
        return

    # Build taken intervals including sleep and events
    taken_intervals = []
    if sleep_block:
        start_mins = time_to_minutes(sleep_block["start"])
        end_mins = time_to_minutes(sleep_block["end"])
        if end_mins < start_mins:  # crosses midnight
            taken_intervals.append((start_mins, 24*60-1))
            taken_intervals.append((0, end_mins))
        else:
            taken_intervals.append((start_mins, end_mins))
    for e in events:
        taken_intervals.append((time_to_minutes(e["start"]), time_to_minutes(e["end"])))

    durations = [a["time"] + downtime for a in assignments]  # add downtime to each assignment
    intervals = calendarAlgo.generate_intervals(360, 24*60-1, taken_intervals, durations)

    if not intervals:
        messagebox.showinfo("Scheduling Failed", "Could not fit assignments into the day.")
        return

    # Apply downtime between assignments
    for i, (a, (start, end)) in enumerate(zip(assignments, intervals)):
        if i == 0:
            start_with_downtime = start
        else:
            prev_end = time_to_minutes(assignments[i-1]["end"])
            start_with_downtime = max(start, prev_end + downtime)
        a["start"] = minutes_to_time(start_with_downtime)
        a["end"] = minutes_to_time(start_with_downtime + a["time"])

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
