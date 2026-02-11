
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from tkcalendar import DateEntry
from config.styles import *
from config.database import Database
from components.buttons import ModernButton
from components.cards import ModernCard
from components.pickers import TimePicker


def show_create(parent):
    """Display the create schedule view"""
    # Header
    header = tk.Frame(parent, bg=BG_MAIN)
    header.pack(fill="x", pady=(0, 20))
    
    tk.Label(header, text="Create New Schedule", font=FONT_TITLE,
            fg=TEXT_PRIMARY, bg=BG_MAIN).pack(side="left")
    
    # Main card
    main_card = ModernCard(parent)
    main_card.pack(fill="both", expand=True)
    
    # Scrollable content
    canvas = tk.Canvas(main_card, bg=BG_CARD, highlightthickness=0)
    scrollbar = ttk.Scrollbar(main_card, orient="vertical", command=canvas.yview)
    scrollable = tk.Frame(canvas, bg=BG_CARD)
    
    scrollable.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=scrollable, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    
    # User Information Section
    user_section = tk.Frame(scrollable, bg=BG_CARD)
    user_section.pack(fill="x", padx=30, pady=(30, 20))
    
    tk.Label(user_section, text="👤 User Information", font=FONT_HEADER,
            fg=TEXT_PRIMARY, bg=BG_CARD).pack(anchor="w", pady=(0, 20))
    
    # First Name
    tk.Label(user_section, text="First Name *", font=FONT_BODY_BOLD,
            fg=TEXT_PRIMARY, bg=BG_CARD).pack(anchor="w", pady=(0, 5))
    first_name_entry = tk.Entry(user_section, font=FONT_BODY, relief=tk.FLAT,
                                bd=0, highlightthickness=1, highlightbackground=BORDER_COLOR)
    first_name_entry.pack(fill="x", ipady=10, pady=(0, 15))
    
    # Last Name
    tk.Label(user_section, text="Last Name *", font=FONT_BODY_BOLD,
            fg=TEXT_PRIMARY, bg=BG_CARD).pack(anchor="w", pady=(0, 5))
    last_name_entry = tk.Entry(user_section, font=FONT_BODY, relief=tk.FLAT,
                               bd=0, highlightthickness=1, highlightbackground=BORDER_COLOR)
    last_name_entry.pack(fill="x", ipady=10)
    
    # Separator
    tk.Frame(scrollable, bg=BORDER_COLOR, height=1).pack(fill="x", padx=30, pady=20)
    
    # Activities Container
    activities_container = tk.Frame(scrollable, bg=BG_CARD)
    activities_container.pack(fill="x", padx=30)
    
    activities_list = []
    
    def create_activity_widget(number):
        return _create_activity_widget(activities_container, number, activities_list)
    
    def remove_activity(widget):
        widget['frame'].destroy()
        activities_list.remove(widget)
        renumber_activities()
    
    def renumber_activities():
        for idx, aw in enumerate(activities_list, 1):
            header_frame = aw['frame'].winfo_children()[0]
            labels = [w for w in header_frame.winfo_children() if isinstance(w, tk.Label)]
            if labels:
                labels[0].config(text=f"🎯 Activity #{idx}")
    
    def add_activity():
        widget = create_activity_widget(len(activities_list) + 1)
        activities_list.append(widget)
    
    # Initial activity
    initial_activity = create_activity_widget(1)
    activities_list.append(initial_activity)
    
    # Add Activity Button
    add_act_btn = ModernButton(scrollable, "Add Another Activity", add_activity,
                               style="success", icon="➕", width=20)
    add_act_btn.pack(pady=(20, 20))
    
    # Submit Section
    submit_frame = tk.Frame(scrollable, bg=BG_CARD)
    submit_frame.pack(fill="x", padx=30, pady=(0, 30))
    
    def submit_schedule():
        _submit_schedule(first_name_entry, last_name_entry, activities_list, parent)
    
    ModernButton(submit_frame, "Create Schedule", submit_schedule,
                style="primary", icon="💾", width=20).pack()
    
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")


def _create_activity_widget(parent, number, activities_list):
    """Helper function to create activity widget"""
    activity_frame = tk.Frame(parent, bg="#f8fafc", relief=tk.FLAT,
                             bd=0, highlightthickness=1, highlightbackground=BORDER_COLOR)
    activity_frame.pack(fill="x", pady=(0, 20))
    
    # Activity Header
    act_header = tk.Frame(activity_frame, bg="#f8fafc")
    act_header.pack(fill="x", padx=20, pady=(15, 10))
    
    tk.Label(act_header, text=f"🎯 Activity #{number}", font=FONT_BODY_BOLD,
            fg=TEXT_PRIMARY, bg="#f8fafc").pack(side="left")
    
    if number > 1:
        remove_btn = tk.Button(act_header, text="✕ Remove", font=FONT_SMALL,
                              bg=DANGER, fg="white", relief=tk.FLAT, cursor="hand2",
                              command=lambda: _remove_activity_widget(activity_widget, activities_list))
        remove_btn.pack(side="right")
        
        remove_btn.bind("<Enter>", lambda e: remove_btn.config(bg="#dc2626"))
        remove_btn.bind("<Leave>", lambda e: remove_btn.config(bg=DANGER))
    
    # Activity Fields
    fields_frame = tk.Frame(activity_frame, bg="#f8fafc")
    fields_frame.pack(fill="x", padx=20, pady=(0, 15))
    
    # Activity Name
    tk.Label(fields_frame, text="Activity Name *", font=FONT_BODY,
            fg=TEXT_PRIMARY, bg="#f8fafc").pack(anchor="w", pady=(0, 5))
    activity_name = tk.Entry(fields_frame, font=FONT_BODY, relief=tk.FLAT,
                            bd=0, highlightthickness=1, highlightbackground=BORDER_COLOR)
    activity_name.pack(fill="x", ipady=8, pady=(0, 10))
    
    # Row for dropdowns
    dropdown_frame = tk.Frame(fields_frame, bg="#f8fafc")
    dropdown_frame.pack(fill="x", pady=(0, 10))
    dropdown_frame.grid_columnconfigure((0, 1, 2), weight=1)
    
    # Category
    tk.Label(dropdown_frame, text="Category *", font=FONT_BODY,
            fg=TEXT_PRIMARY, bg="#f8fafc").grid(row=0, column=0, sticky="w", padx=(0, 10))
    category = ttk.Combobox(dropdown_frame, values=["School", "Event", "Hangout", "Travel", "Other"],
                           state="readonly", font=FONT_BODY)
    category.grid(row=1, column=0, sticky="ew", padx=(0, 10))
    category.set("School")
    
    # Priority
    tk.Label(dropdown_frame, text="Priority *", font=FONT_BODY,
            fg=TEXT_PRIMARY, bg="#f8fafc").grid(row=0, column=1, sticky="w", padx=(0, 10))
    priority = ttk.Combobox(dropdown_frame, values=["Low", "Medium", "High"],
                           state="readonly", font=FONT_BODY)
    priority.grid(row=1, column=1, sticky="ew", padx=(0, 10))
    priority.set("Medium")
    
    # Status
    tk.Label(dropdown_frame, text="Status *", font=FONT_BODY,
            fg=TEXT_PRIMARY, bg="#f8fafc").grid(row=0, column=2, sticky="w")
    status = ttk.Combobox(dropdown_frame, values=["Pending", "In Progress", "Done"],
                         state="readonly", font=FONT_BODY)
    status.grid(row=1, column=2, sticky="ew")
    status.set("Pending")
    
    # Tasks Section
    tk.Frame(activity_frame, bg=BORDER_COLOR, height=1).pack(fill="x", padx=20, pady=15)
    
    tk.Label(activity_frame, text="📝 Tasks", font=FONT_BODY_BOLD,
            fg=TEXT_PRIMARY, bg="#f8fafc").pack(anchor="w", padx=20, pady=(0, 10))
    
    tasks_container = tk.Frame(activity_frame, bg="#f8fafc")
    tasks_container.pack(fill="x", padx=20, pady=(0, 15))
    
    tasks_list = []
    
    def create_task_widget(task_num):
        return _create_task_widget(tasks_container, task_num, tasks_list)
    
    def remove_task(widget):
        widget['frame'].destroy()
        tasks_list.remove(widget)
        renumber_tasks()
    
    def renumber_tasks():
        for idx, tw in enumerate(tasks_list, 1):
            header_frame = tw['frame'].winfo_children()[0]
            labels = [w for w in header_frame.winfo_children() if isinstance(w, tk.Label)]
            if labels:
                labels[0].config(text=f"Task #{idx}")
    
    def add_task():
        create_task_widget(len(tasks_list) + 1)
    
    # Initial task
    create_task_widget(1)
    
    # Add Task Button
    add_task_btn = ModernButton(activity_frame, "Add Task", add_task,
                                style="outline", icon="➕")
    add_task_btn.pack(pady=(0, 15))
    
    activity_widget = {
        'frame': activity_frame,
        'name': activity_name,
        'category': category,
        'priority': priority,
        'status': status,
        'tasks': tasks_list,
        'add_task': add_task
    }
    
    return activity_widget


def _create_task_widget(parent, task_num, tasks_list):
    """Helper function to create task widget"""
    task_frame = tk.Frame(parent, bg="white", relief=tk.FLAT,
                         bd=0, highlightthickness=1, highlightbackground=BORDER_COLOR)
    task_frame.pack(fill="x", pady=(0, 10))
    
    # Task Header
    task_hdr = tk.Frame(task_frame, bg="white")
    task_hdr.pack(fill="x", padx=15, pady=(10, 5))
    
    tk.Label(task_hdr, text=f"Task #{task_num}", font=FONT_BODY,
            fg=TEXT_SECONDARY, bg="white").pack(side="left")
    
    if task_num > 1:
        rm_task = tk.Button(task_hdr, text="✕", font=FONT_SMALL,
                           bg=DANGER, fg="white", relief=tk.FLAT, cursor="hand2",
                           width=3, command=lambda: _remove_task_widget(task_widget, tasks_list))
        rm_task.pack(side="right")
        
        rm_task.bind("<Enter>", lambda e: rm_task.config(bg="#dc2626"))
        rm_task.bind("<Leave>", lambda e: rm_task.config(bg=DANGER))
    
    # Task Fields
    task_content = tk.Frame(task_frame, bg="white")
    task_content.pack(fill="x", padx=15, pady=(0, 10))
    
    tk.Label(task_content, text="Task Title *", font=FONT_BODY,
            fg=TEXT_PRIMARY, bg="white").pack(anchor="w", pady=(0, 5))
    task_title = tk.Entry(task_content, font=FONT_BODY, relief=tk.FLAT,
                         bd=0, highlightthickness=1, highlightbackground=BORDER_COLOR)
    task_title.pack(fill="x", ipady=8, pady=(0, 10))
    
    tk.Label(task_content, text="Description", font=FONT_BODY,
            fg=TEXT_PRIMARY, bg="white").pack(anchor="w", pady=(0, 5))
    task_desc = tk.Text(task_content, height=2, font=FONT_BODY, relief=tk.FLAT,
                       bd=0, highlightthickness=1, highlightbackground=BORDER_COLOR, wrap=tk.WORD)
    task_desc.pack(fill="x", pady=(0, 10))
    
    # Date and Time with Pickers
    dt_frame = tk.Frame(task_content, bg="white")
    dt_frame.pack(fill="x")
    dt_frame.grid_columnconfigure((0, 1), weight=1)
    
    # Date Picker
    tk.Label(dt_frame, text="Date *", font=FONT_BODY,
            fg=TEXT_PRIMARY, bg="white").grid(row=0, column=0, sticky="w", padx=(0, 10))
    task_date = DateEntry(dt_frame, font=FONT_BODY, background=PRIMARY, 
                         foreground="white", borderwidth=1, date_pattern='mm/dd/yyyy')
    task_date.grid(row=1, column=0, sticky="ew", ipady=4, padx=(0, 10))
    
    # Time Picker
    tk.Label(dt_frame, text="Time", font=FONT_BODY,
            fg=TEXT_PRIMARY, bg="white").grid(row=0, column=1, sticky="w")
    task_time_picker = TimePicker(dt_frame)
    task_time_picker.grid(row=1, column=1, sticky="w")
    
    task_widget = {
        'frame': task_frame,
        'title': task_title,
        'desc': task_desc,
        'date': task_date,
        'time': task_time_picker
    }
    tasks_list.append(task_widget)
    return task_widget


def _remove_activity_widget(widget, activities_list):
    """Helper to remove activity"""
    widget['frame'].destroy()
    activities_list.remove(widget)
    # Renumber
    for idx, aw in enumerate(activities_list, 1):
        header_frame = aw['frame'].winfo_children()[0]
        labels = [w for w in header_frame.winfo_children() if isinstance(w, tk.Label)]
        if labels:
            labels[0].config(text=f"🎯 Activity #{idx}")


def _remove_task_widget(widget, tasks_list):
    """Helper to remove task"""
    widget['frame'].destroy()
    tasks_list.remove(widget)
    # Renumber
    for idx, tw in enumerate(tasks_list, 1):
        header_frame = tw['frame'].winfo_children()[0]
        labels = [w for w in header_frame.winfo_children() if isinstance(w, tk.Label)]
        if labels:
            labels[0].config(text=f"Task #{idx}")


def _submit_schedule(first_name_entry, last_name_entry, activities_list, parent):
    """Handle schedule submission"""
    # Validation
    if not first_name_entry.get().strip() or not last_name_entry.get().strip():
        messagebox.showerror("Validation Error", "Please enter both first and last name")
        return
    
    for idx, activity in enumerate(activities_list, 1):
        if not activity['name'].get().strip():
            messagebox.showerror("Validation Error", f"Activity #{idx}: Please enter activity name")
            return
        
        for tidx, task in enumerate(activity['tasks'], 1):
            if not task['title'].get().strip():
                messagebox.showerror("Validation Error", f"Activity #{idx}, Task #{tidx}: Please enter task title")
                return
            if not task['date'].get().strip():
                messagebox.showerror("Validation Error", f"Activity #{idx}, Task #{tidx}: Please enter task date")
                return
    
    # Save to database
    try:
        conn = Database.connect()
        cursor = conn.cursor()
        
        cursor.execute("INSERT INTO users (first_name, last_name, created_at) VALUES (%s, %s, %s)",
                      (first_name_entry.get().strip(), last_name_entry.get().strip(), 
                       datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        user_id = cursor.lastrowid
        
        for activity in activities_list:
            cursor.execute("INSERT INTO activities (activity_name, category, priority, status, user_id) VALUES (%s,%s,%s,%s,%s)",
                          (activity['name'].get(), activity['category'].get(), 
                           activity['priority'].get(), activity['status'].get(), user_id))
            activity_id = cursor.lastrowid
            
            for task in activity['tasks']:
                cursor.execute("INSERT INTO tasks (task_title, description, date, time, user_id, activity_id) VALUES (%s,%s,%s,%s,%s,%s)",
                              (task['title'].get(), task['desc'].get("1.0", tk.END).strip(),
                               task['date'].get(), task['time'].get_time(), user_id, activity_id))
        
        conn.commit()
        conn.close()
        
        messagebox.showinfo("Success", f"✅ Schedule created successfully!\n\n{len(activities_list)} activities created\nwith multiple tasks.")
        
        # Refresh to dashboard
        from views.dashboard import show_dashboard
        for widget in parent.winfo_children():
            widget.destroy()
        show_dashboard(parent)
    
    except Exception as e:
        messagebox.showerror("Database Error", f"Failed to save schedule:\n{e}")