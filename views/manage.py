import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from tkcalendar import DateEntry
from config.styles import *
from config.database import Database
from components.buttons import ModernButton
from components.cards import ModernCard
from components.pickers import TimePicker


def show_manage(parent):
    """Display the manage schedules view"""
    # Store reference to parent
    global manage_parent
    manage_parent = parent
    
    header = tk.Frame(parent, bg=BG_MAIN)
    header.pack(fill="x", pady=(0, 20))
    
    tk.Label(header, text="Manage Schedules", font=FONT_TITLE,
            fg=TEXT_PRIMARY, bg=BG_MAIN).pack(side="left")
    
    # Content card
    global manage_content_card
    manage_content_card = ModernCard(parent)
    manage_content_card.pack(fill="both", expand=True)
    
    # Action buttons
    btn_frame = tk.Frame(header, bg=BG_MAIN)
    btn_frame.pack(side="right")
    
    ModernButton(btn_frame, "View All", lambda: load_manage_view("view"),
                style="info", icon="👁", width=10).pack(side="left", padx=5)
    ModernButton(btn_frame, "Update", lambda: load_manage_view("update"),
                style="secondary", icon="✏", width=10).pack(side="left", padx=5)
    ModernButton(btn_frame, "Delete", lambda: load_manage_view("delete"),
                style="danger", icon="🗑", width=10).pack(side="left", padx=5)
    
    # Default view
    load_manage_view("view")


def delete_task_with_cleanup(task_id, task_title):
    """
    Delete a task and clean up orphaned users/activities
    This permanently removes data from the MySQL database
    """
    conn = None
    try:
        conn = Database.connect()
        cursor = conn.cursor()
        
        # Get user_id and activity_id BEFORE deleting the task
        cursor.execute("""
            SELECT user_id, activity_id 
            FROM tasks 
            WHERE task_id = %s
        """, (task_id,))
        
        result = cursor.fetchone()
        if not result:
            messagebox.showwarning("Warning", "Task not found!")
            if conn:
                conn.close()
            return False
        
        user_id, activity_id = result
        
        # Step 1: Delete the task from database
        cursor.execute("DELETE FROM tasks WHERE task_id = %s", (task_id,))
        print(f"[DELETE] Deleted task_id {task_id} from tasks table")
        
        # Step 2: Check if this user has any other tasks
        cursor.execute("SELECT COUNT(*) FROM tasks WHERE user_id = %s", (user_id,))
        user_task_count = cursor.fetchone()[0]
        
        # If user has no more tasks, delete the user
        if user_task_count == 0:
            cursor.execute("DELETE FROM users WHERE user_id = %s", (user_id,))
            print(f"[DELETE] Deleted orphaned user_id {user_id} from users table")
        
        # Step 3: Check if this activity has any other tasks
        cursor.execute("SELECT COUNT(*) FROM tasks WHERE activity_id = %s", (activity_id,))
        activity_task_count = cursor.fetchone()[0]
        
        # If activity has no more tasks, delete the activity
        if activity_task_count == 0:
            cursor.execute("DELETE FROM activities WHERE activity_id = %s", (activity_id,))
            print(f"[DELETE] Deleted orphaned activity_id {activity_id} from activities table")
        
        # CRITICAL: Commit changes to database
        # Without this, changes won't be saved to MySQL!
        conn.commit()
        print("[COMMIT] Changes committed to MySQL database")
        
        # Close connection
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Delete failed: {e}")
        if conn:
            conn.rollback()  # Rollback if there's an error
            conn.close()
        raise e


def load_manage_view(mode):
    """Load specific manage view mode"""
    global manage_content_card
    
    # Clear the content card
    for widget in manage_content_card.winfo_children():
        widget.destroy()
    
    # Header
    card_header = tk.Frame(manage_content_card, bg=BG_CARD)
    card_header.pack(fill="x", padx=20, pady=20)
    
    mode_titles = {
        "view": "📋 All Schedules",
        "update": "✏️ Update Schedule",
        "delete": "🗑️ Delete Schedule"
    }
    
    tk.Label(card_header, text=mode_titles.get(mode, "Schedules"),
            font=FONT_HEADER, fg=TEXT_PRIMARY, bg=BG_CARD).pack(side="left")
    
    # Table frame
    table_frame = tk.Frame(manage_content_card, bg=BG_CARD)
    table_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
    
    try:
        conn = Database.connect()
        cursor = conn.cursor()
        
        query = """
        SELECT t.task_id, t.task_title, t.date, t.time,
               a.activity_name, a.priority, a.status, a.category,
               u.first_name, u.last_name
        FROM tasks t
        JOIN activities a ON t.activity_id = a.activity_id
        JOIN users u ON t.user_id = u.user_id
        ORDER BY t.task_id DESC
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()
        
        if rows:
            # Create treeview
            columns = ("ID", "Task", "Date", "Time", "Activity", "Priority", "Status", "User", "Actions")
            tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=20)
            
            # Style the treeview
            style = ttk.Style()
            style.configure("Treeview", rowheight=35, font=FONT_BODY)
            style.configure("Treeview.Heading", font=FONT_BODY_BOLD)
            
            column_widths = [50, 180, 100, 80, 130, 80, 100, 130, 120]
            for col, width in zip(columns, column_widths):
                tree.heading(col, text=col, anchor=tk.W)
                tree.column(col, width=width, anchor=tk.W)
            
            for idx, row in enumerate(rows, 1):
                task_id, title, date, time, activity, priority, status, category, fname, lname = row
                display_row = (idx, title, date, time or "-", activity, priority, status, f"{fname} {lname}", "Quick Actions")
                tree.insert('', tk.END, values=display_row, tags=(task_id, priority))
            
            # Priority colors
            tree.tag_configure("High", foreground=DANGER)
            tree.tag_configure("Medium", foreground=WARNING)
            tree.tag_configure("Low", foreground=SUCCESS)
            
            # Quick status change function
            def quick_status_change(event):
                region = tree.identify("region", event.x, event.y)
                if region == "cell":
                    column = tree.identify_column(event.x)
                    item = tree.identify_row(event.y)
                    
                    if item and column == "#9":  # Actions column
                        task_id = tree.item(item)['tags'][0]
                        values = tree.item(item)['values']
                        current_status = values[6]
                        
                        # Create popup menu
                        menu = tk.Menu(tree, tearoff=0, font=FONT_BODY)
                        menu.add_command(label="✏️ Edit Full Details", 
                                       command=lambda: [menu.unpost(), open_update_form(task_id)])
                        menu.add_separator()
                        menu.add_command(label="📋 Change to: Pending", 
                                       command=lambda: [menu.unpost(), change_status(task_id, "Pending")])
                        menu.add_command(label="🔄 Change to: In Progress", 
                                       command=lambda: [menu.unpost(), change_status(task_id, "In Progress")])
                        menu.add_command(label="✅ Change to: Done", 
                                       command=lambda: [menu.unpost(), change_status(task_id, "Done")])
                        
                        menu.post(event.x_root, event.y_root)
            
            def change_status(task_id, new_status):
                try:
                    conn = Database.connect()
                    cursor = conn.cursor()
                    
                    cursor.execute("SELECT activity_id FROM tasks WHERE task_id = %s", (task_id,))
                    activity_id = cursor.fetchone()[0]
                    
                    cursor.execute("UPDATE activities SET status = %s WHERE activity_id = %s", 
                                 (new_status, activity_id))
                    
                    conn.commit()
                    conn.close()
                    
                    status_icons = {"Pending": "📋", "In Progress": "🔄", "Done": "✅"}
                    messagebox.showinfo("Status Updated", 
                                      f"{status_icons.get(new_status, '')} Status changed to: {new_status}")
                    
                    load_manage_view(mode)
                    
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to update status:\n{e}")
            
            tree.bind('<Button-1>', quick_status_change)
            
            # Mode-specific interactions
            if mode == "update":
                def on_double_click(event):
                    selection = tree.selection()
                    if selection:
                        item = tree.item(selection[0])
                        task_id = item['tags'][0]
                        open_update_form(task_id)
                
                tree.bind('<Double-1>', on_double_click)
                
                info_label = tk.Label(table_frame, text="💡 Double-click row to edit full details | Click 'Quick Actions' to change status quickly",
                                     font=FONT_SMALL, fg=TEXT_SECONDARY, bg=BG_CARD)
                info_label.pack(pady=(10, 0))
            
            elif mode == "delete":
                def on_delete_click(event):
                    selection = tree.selection()
                    if selection:
                        item = tree.item(selection[0])
                        task_id = item['tags'][0]
                        values = item['values']
                        task_title = values[1]
                        
                        if messagebox.askyesno("Confirm Delete", 
                                              f"Are you sure you want to delete this task?\n\n📋 {task_title}\n🆔 Task ID: {task_id}\n\n⚠️ This action cannot be undone."):
                            try:
                                # Use the new delete function with cleanup
                                success = delete_task_with_cleanup(task_id, task_title)
                                
                                if success:
                                    messagebox.showinfo("Success", 
                                        f"✅ Task '{task_title}' deleted successfully!\n\n" +
                                        "The data has been permanently removed from the database.")
                                    
                                    # Reset auto increment
                                    Database.reset_auto_increment()
                                    
                                    # Refresh the view
                                    load_manage_view("delete")
                                
                            except Exception as e:
                                messagebox.showerror("Error", f"Failed to delete task:\n{e}")
                
                tree.bind('<Double-1>', on_delete_click)
                
                info_label = tk.Label(table_frame, text="⚠️ Double-click a row to delete",
                                     font=FONT_SMALL, fg=DANGER, bg=BG_CARD)
                info_label.pack(pady=(10, 0))
            
            scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=tree.yview)
            tree.configure(yscrollcommand=scrollbar.set)
            scrollbar.pack(side="right", fill="y")
            tree.pack(side="left", fill="both", expand=True)
        
        else:
            empty_state = tk.Frame(table_frame, bg=BG_CARD)
            empty_state.pack(expand=True)
            
            tk.Label(empty_state, text="📭", font=("Segoe UI", 48),
                    fg=TEXT_SECONDARY, bg=BG_CARD).pack(pady=(50, 20))
            tk.Label(empty_state, text="No schedules found", font=FONT_HEADER,
                    fg=TEXT_PRIMARY, bg=BG_CARD).pack()
            tk.Label(empty_state, text="Create your first schedule to get started",
                    font=FONT_BODY, fg=TEXT_SECONDARY, bg=BG_CARD).pack(pady=(5, 50))
    
    except Exception as e:
        tk.Label(table_frame, text=f"❌ Error loading schedules:\n{e}",
                font=FONT_BODY, fg=DANGER, bg=BG_CARD).pack(expand=True)


def open_update_form(task_id):
    """Open update form in popup window"""
    try:
        conn = Database.connect()
        cursor = conn.cursor()
        
        query = """
        SELECT 
            u.user_id, u.first_name, u.last_name,
            a.activity_id, a.activity_name, a.category, a.priority, a.status,
            t.task_id, t.task_title, t.description, t.date, t.time
        FROM tasks t
        JOIN activities a ON t.activity_id = a.activity_id
        JOIN users u ON t.user_id = u.user_id
        WHERE t.task_id = %s
        """
        cursor.execute(query, (task_id,))
        data = cursor.fetchone()
        conn.close()
        
        if not data:
            messagebox.showerror("Error", "Task not found")
            return
        
        user_id, fname, lname, activity_id, act_name, category, priority, status, task_id, title, desc, date, time = data
        
        # Create popup window
        popup = tk.Toplevel()
        popup.title(f"Update Task")
        popup.geometry("700x800")
        popup.configure(bg=BG_MAIN)
        popup.transient()
        popup.grab_set()
        
        # Header
        header = tk.Frame(popup, bg=PRIMARY, height=60)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        tk.Label(header, text=f"✏️ Edit Schedule", font=FONT_HEADER,
                fg="white", bg=PRIMARY).pack(pady=15, padx=20)
        
        # Scrollable content
        canvas = tk.Canvas(popup, bg=BG_MAIN, highlightthickness=0)
        scrollbar = ttk.Scrollbar(popup, orient="vertical", command=canvas.yview)
        scrollable = tk.Frame(canvas, bg=BG_MAIN)
        
        scrollable.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # User Section
        user_card = ModernCard(scrollable)
        user_card.pack(fill="x", padx=20, pady=(20, 10))
        
        tk.Label(user_card, text="👤 User Information", font=FONT_BODY_BOLD,
                fg=TEXT_PRIMARY, bg=BG_CARD).pack(anchor="w", padx=20, pady=(15, 10))
        
        user_frame = tk.Frame(user_card, bg=BG_CARD)
        user_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        tk.Label(user_frame, text="First Name *", font=FONT_BODY,
                fg=TEXT_PRIMARY, bg=BG_CARD).pack(anchor="w", pady=(0, 5))
        fname_entry = tk.Entry(user_frame, font=FONT_BODY, relief=tk.FLAT,
                              bd=0, highlightthickness=1, highlightbackground=BORDER_COLOR)
        fname_entry.pack(fill="x", ipady=8, pady=(0, 10))
        fname_entry.insert(0, fname)
        
        tk.Label(user_frame, text="Last Name *", font=FONT_BODY,
                fg=TEXT_PRIMARY, bg=BG_CARD).pack(anchor="w", pady=(0, 5))
        lname_entry = tk.Entry(user_frame, font=FONT_BODY, relief=tk.FLAT,
                              bd=0, highlightthickness=1, highlightbackground=BORDER_COLOR)
        lname_entry.pack(fill="x", ipady=8)
        lname_entry.insert(0, lname)
        
        # Activity Section
        activity_card = ModernCard(scrollable)
        activity_card.pack(fill="x", padx=20, pady=10)
        
        tk.Label(activity_card, text="🎯 Activity Information", font=FONT_BODY_BOLD,
                fg=TEXT_PRIMARY, bg=BG_CARD).pack(anchor="w", padx=20, pady=(15, 10))
        
        activity_frame = tk.Frame(activity_card, bg=BG_CARD)
        activity_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        tk.Label(activity_frame, text="Activity Name *", font=FONT_BODY,
                fg=TEXT_PRIMARY, bg=BG_CARD).pack(anchor="w", pady=(0, 5))
        act_entry = tk.Entry(activity_frame, font=FONT_BODY, relief=tk.FLAT,
                            bd=0, highlightthickness=1, highlightbackground=BORDER_COLOR)
        act_entry.pack(fill="x", ipady=8, pady=(0, 10))
        act_entry.insert(0, act_name)
        
        # Dropdowns in grid
        dropdown_frame = tk.Frame(activity_frame, bg=BG_CARD)
        dropdown_frame.pack(fill="x")
        dropdown_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        tk.Label(dropdown_frame, text="Category *", font=FONT_BODY,
                fg=TEXT_PRIMARY, bg=BG_CARD).grid(row=0, column=0, sticky="w", padx=(0, 10))
        cat_combo = ttk.Combobox(dropdown_frame, values=["School", "Event", "Hangout", "Travel", "Other"],
                                state="readonly", font=FONT_BODY)
        cat_combo.grid(row=1, column=0, sticky="ew", padx=(0, 10))
        cat_combo.set(category)
        
        tk.Label(dropdown_frame, text="Priority *", font=FONT_BODY,
                fg=TEXT_PRIMARY, bg=BG_CARD).grid(row=0, column=1, sticky="w", padx=(0, 10))
        pri_combo = ttk.Combobox(dropdown_frame, values=["Low", "Medium", "High"],
                                state="readonly", font=FONT_BODY)
        pri_combo.grid(row=1, column=1, sticky="ew", padx=(0, 10))
        pri_combo.set(priority)
        
        tk.Label(dropdown_frame, text="Status *", font=FONT_BODY,
                fg=TEXT_PRIMARY, bg=BG_CARD).grid(row=0, column=2, sticky="w")
        stat_combo = ttk.Combobox(dropdown_frame, values=["Pending", "In Progress", "Done"],
                                 state="readonly", font=FONT_BODY)
        stat_combo.grid(row=1, column=2, sticky="ew")
        stat_combo.set(status)
        
        # Task Section
        task_card = ModernCard(scrollable)
        task_card.pack(fill="x", padx=20, pady=10)
        
        tk.Label(task_card, text="📝 Task Information", font=FONT_BODY_BOLD,
                fg=TEXT_PRIMARY, bg=BG_CARD).pack(anchor="w", padx=20, pady=(15, 10))
        
        task_frame = tk.Frame(task_card, bg=BG_CARD)
        task_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        tk.Label(task_frame, text="Task Title *", font=FONT_BODY,
                fg=TEXT_PRIMARY, bg=BG_CARD).pack(anchor="w", pady=(0, 5))
        title_entry = tk.Entry(task_frame, font=FONT_BODY, relief=tk.FLAT,
                              bd=0, highlightthickness=1, highlightbackground=BORDER_COLOR)
        title_entry.pack(fill="x", ipady=8, pady=(0, 10))
        title_entry.insert(0, title)
        
        tk.Label(task_frame, text="Description", font=FONT_BODY,
                fg=TEXT_PRIMARY, bg=BG_CARD).pack(anchor="w", pady=(0, 5))
        desc_text = tk.Text(task_frame, height=4, font=FONT_BODY, relief=tk.FLAT,
                           bd=0, highlightthickness=1, highlightbackground=BORDER_COLOR, wrap=tk.WORD)
        desc_text.pack(fill="x", pady=(0, 10))
        desc_text.insert("1.0", desc or "")
        
        # Date and Time with Pickers
        dt_frame = tk.Frame(task_frame, bg=BG_CARD)
        dt_frame.pack(fill="x")
        dt_frame.grid_columnconfigure((0, 1), weight=1)
        
        # Date Picker
        tk.Label(dt_frame, text="Date *", font=FONT_BODY,
                fg=TEXT_PRIMARY, bg=BG_CARD).grid(row=0, column=0, sticky="w", padx=(0, 10))
        date_entry = DateEntry(dt_frame, font=FONT_BODY, background=PRIMARY,
                              foreground="white", borderwidth=1, date_pattern='mm/dd/yyyy')
        date_entry.grid(row=1, column=0, sticky="ew", ipady=4, padx=(0, 10))
        # Set the date
        try:
            if date:
                date_obj = datetime.strptime(str(date), '%Y-%m-%d')
                date_entry.set_date(date_obj)
        except:
            pass
        
        # Time Picker
        tk.Label(dt_frame, text="Time", font=FONT_BODY,
                fg=TEXT_PRIMARY, bg=BG_CARD).grid(row=0, column=1, sticky="w")
        time_picker = TimePicker(dt_frame)
        time_picker.grid(row=1, column=1, sticky="w")
        if time:
            time_picker.set_time(str(time))
        
        # Buttons
        btn_frame = tk.Frame(scrollable, bg=BG_MAIN)
        btn_frame.pack(fill="x", padx=20, pady=20)
        
        def save_update():
            # Validation
            if not fname_entry.get().strip() or not lname_entry.get().strip():
                messagebox.showerror("Validation Error", "First and last name are required")
                return
            
            if not act_entry.get().strip():
                messagebox.showerror("Validation Error", "Activity name is required")
                return
            
            if not title_entry.get().strip() or not date_entry.get_date():
                messagebox.showerror("Validation Error", "Task title and date are required")
                return
            
            # Update database
            try:
                conn = Database.connect()
                cursor = conn.cursor()
                
                # Update user
                cursor.execute("UPDATE users SET first_name = %s, last_name = %s WHERE user_id = %s",
                              (fname_entry.get().strip(), lname_entry.get().strip(), user_id))
                
                # Update activity
                cursor.execute("UPDATE activities SET activity_name = %s, category = %s, priority = %s, status = %s WHERE activity_id = %s",
                              (act_entry.get().strip(), cat_combo.get(), pri_combo.get(), stat_combo.get(), activity_id))
                
                # Update task
                cursor.execute("UPDATE tasks SET task_title = %s, description = %s, date = %s, time = %s WHERE task_id = %s",
                              (title_entry.get().strip(), desc_text.get("1.0", tk.END).strip(), 
                               date_entry.get_date().strftime('%Y-%m-%d'), time_picker.get_time(), task_id))
                
                conn.commit()
                conn.close()
                
                messagebox.showinfo("Success", f"✅ Task updated successfully!")
                popup.destroy()
                load_manage_view("update")
                
            except Exception as e:
                messagebox.showerror("Database Error", f"Failed to update:\n{e}")
        
        def cancel_update():
            popup.destroy()
        
        ModernButton(btn_frame, "Cancel", cancel_update, style="outline", width=12).pack(side="left")
        ModernButton(btn_frame, "Save Changes", save_update, style="primary", icon="💾", width=15).pack(side="right")
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load task data:\n{e}")