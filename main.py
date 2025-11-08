import os
from dotenv import load_dotenv
import tkinter as tk
from tkinter import simpledialog, messagebox
import calendarAlgo
import gemini
# Load environment variables from .env file
load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")


# Create main window
root = tk.Tk()
root.title("Schedule & Assignments")

# Store events and assignments
events = []
assignments = []

# Function to add a schedule event
def add_event():
    start_time = simpledialog.askstring("Start Time", "Enter start time (HH:MM):")
    end_time = simpledialog.askstring("End Time", "Enter end time (HH:MM):")
    
    if start_time and end_time:
        events.append({"start": start_time, "end": end_time})
        messagebox.showinfo("Event Added", f"Event: {start_time} - {end_time}")

# Function to add an assignment
def add_assignment():
    description = []
    description.append(simpledialog.askstring("Assignment", "Enter assignment description:"))
    
    if description:
        assignments.append("desc": description, "time": gemini.prompt_gemini(description, API_KEY))
        messagebox.showinfo("Assignment Added", f"Assignment: {description}")

# Buttons
btn_event = tk.Button(root, text="Add Schedule Event", command=add_event)
btn_event.pack(pady=10)

btn_assignment = tk.Button(root, text="Add Assignment", command=add_assignment)
btn_assignment.pack(pady=10)

# Run the GUI
root.mainloop()
