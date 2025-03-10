import tkinter as tk
from tkinter import messagebox
import json
import os
import time
import threading


TASKS_FILE = 'tasks.json'
REMINDER_FILE = 'reminder.json'


def load_tasks():
    if os.path.exists(TASKS_FILE):
        try:
            with open(TASKS_FILE, 'r') as file:
                tasks = json.load(file)
                if isinstance(tasks, list):
                    return tasks
        except json.JSONDecodeError:
            messagebox.showwarning('Error', 'Failed to load tasks. The file may be corrupted.')
    return []


def save_tasks(tasks):
    with open(TASKS_FILE, 'w') as file:
        json.dump(tasks, file)


def load_reminder():
    if os.path.exists(REMINDER_FILE):
        try:
            with open(REMINDER_FILE, 'r') as file:
                return json.load(file)
        except json.JSONDecodeError:
            messagebox.showwarning('Error', 'Failed to load reminder time.')
    return ''


def save_reminder(reminder_time):
    with open(REMINDER_FILE, 'w') as file:
        json.dump(reminder_time, file)


def play_sound():
    os.system('paplay /usr/share/sounds/freedesktop/stereo/complete.oga')


def reminder_loop():
    while True:
        current_time = time.strftime('%H:%M')
        if current_time == reminder_time:
            play_sound()
            time.sleep(60)  # Prevent multiple alerts within the same minute
        time.sleep(1)


def set_reminder():
    global reminder_time
    hour = hour_entry.get()
    minute = minute_entry.get()
    am_pm = am_pm_var.get()

    if hour.isdigit() and minute.isdigit():
        hour = int(hour)
        minute = int(minute)

        if am_pm == 'PM' and hour != 12:
            hour += 12
        elif am_pm == 'AM' and hour == 12:
            hour = 0

        reminder_time = f'{hour:02}:{minute:02}'
        save_reminder(reminder_time)
        messagebox.showinfo('Success', f'Reminder set for {reminder_time}')
    else:
        messagebox.showwarning('Warning', 'Please enter valid numbers for hours and minutes')


def add_task():
    tasks_input = entry.get()
    if tasks_input:
        new_tasks = [task.strip() for task in tasks_input.split(',') if task.strip()]
        for task in new_tasks:
            tasks.append({'task': task, 'completed': False})
        save_tasks(tasks)
        update_listbox()
        entry.delete(0, tk.END)
    else:
        messagebox.showwarning('Warning', 'Please enter at least one task')


def update_listbox():
    listbox.delete(0, tk.END)
    for idx, task in enumerate(tasks, start=1):
        status = '[✔]' if task['completed'] else '[ ]'
        color = 'green' if task['completed'] else 'black'
        listbox.insert(tk.END, f'{idx}. {status} {task["task"]}')
        listbox.itemconfig(idx - 1, {'fg': color})


def toggle_task():
    selected = listbox.curselection()
    if selected:
        index = selected[0]
        tasks[index]['completed'] = not tasks[index]['completed']
        save_tasks(tasks)
        update_listbox()
    else:
        messagebox.showwarning('Warning', 'Please select a task to mark/unmark')


def delete_task():
    selected = listbox.curselection()
    if selected:
        index = selected[0]
        del tasks[index]
        save_tasks(tasks)
        update_listbox()
    else:
        messagebox.showwarning('Warning', 'Please select a task to delete')


tasks = load_tasks()
reminder_time = load_reminder()

app = tk.Tk()
app.title('To-Do App')
app.geometry('500x600')
app.configure(bg='#282828')

entry = tk.Entry(app, width=50, font=('Arial', 14), bg='#404040', fg='white', insertbackground='white')
entry.pack(pady=10)

add_button = tk.Button(app, text='Add Task(s)', command=add_task, bg='#4CAF50', fg='white', font=('Arial', 12), width=20)
add_button.pack(pady=5)

listbox = tk.Listbox(app, width=60, height=15, font=('Arial', 12), bg='#303030', fg='white', selectbackground='#505050')
listbox.pack(pady=10)

mark_button = tk.Button(app, text='Mark/Unmark', command=toggle_task, bg='#FF9800', fg='white', font=('Arial', 12), width=20)
mark_button.pack(pady=5)

delete_button = tk.Button(app, text='Delete Task', command=delete_task, bg='#F44336', fg='white', font=('Arial', 12), width=20)
delete_button.pack(pady=5)

reminder_frame = tk.Frame(app, bg='#282828')
reminder_frame.pack(pady=10)

hour_entry = tk.Entry(reminder_frame, width=5, font=('Arial', 14), bg='#404040', fg='white', justify='center')
hour_entry.insert(0, '12')
hour_entry.pack(side='left')

minute_entry = tk.Entry(reminder_frame, width=5, font=('Arial', 14), bg='#404040', fg='white', justify='center')
minute_entry.insert(0, '00')
minute_entry.pack(side='left', padx=(5, 0))

am_pm_var = tk.StringVar(value='AM')
am_pm_menu = tk.OptionMenu(reminder_frame, am_pm_var, 'AM', 'PM')
am_pm_menu.config(width=5, font=('Arial', 12), bg='#404040', fg='white')
am_pm_menu.pack(side='left', padx=(5, 0))

reminder_button = tk.Button(app, text='Set Reminder', command=set_reminder, bg='#2196F3', fg='white', font=('Arial', 12), width=20)
reminder_button.pack(pady=5)

update_listbox()

# Start reminder loop in a separate thread
reminder_thread = threading.Thread(target=reminder_loop, daemon=True)
reminder_thread.start()

app.mainloop()
