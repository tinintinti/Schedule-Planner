import tkinter as tk
from tkinter import ttk
from datetime import datetime
from config.styles import *
from config.database import Database
from components.buttons import ModernButton
from components.cards import ModernCard, StatCard


def show_dashboard(parent):
    """Display the dashboard view"""
    # Clear the parent frame first to ensure fresh data
    for widget in parent.winfo_children():
        widget.destroy()
    
    # Header
    header = tk.Frame(parent, bg=BG_MAIN)
    header.pack(fill="x", pady=(0, 20))
    
    tk.Label(header, text="Dashboard", font=FONT_TITLE,
            fg=TEXT_PRIMARY, bg=BG_MAIN).pack(side="left")
    
    tk.Label(header, text=datetime.now().strftime("%B %d, %Y"), 
            font=FONT_BODY, fg=TEXT_SECONDARY, bg=BG_MAIN).pack(side="right")
    
    # Stats Grid
    try:
        conn = Database.connect()
        cursor = conn.cursor()
        
        # Count ONLY users who have at least one task
        cursor.execute("""
            SELECT COUNT(DISTINCT user_id) FROM tasks
        """)
        total_users = cursor.fetchone()[0]
        
        # Count ONLY activities that have at least one task
        cursor.execute("""
            SELECT COUNT(DISTINCT activity_id) FROM tasks
        """)
        total_activities = cursor.fetchone()[0]
        
        # Count total tasks
        cursor.execute("SELECT COUNT(*) FROM tasks")
        total_tasks = cursor.fetchone()[0]
        
        # Count upcoming tasks (today and future)
        cursor.execute("SELECT COUNT(*) FROM tasks WHERE date >= CURDATE()")
        upcoming_tasks = cursor.fetchone()[0]
        
        conn.close()
        
        stats_grid = tk.Frame(parent, bg=BG_MAIN)
        stats_grid.pack(fill="x", pady=(0, 20))
        
        stats_data = [
            ("Active Users", total_users, "👥", SUCCESS),
            ("Active Activities", total_activities, "🎯", INFO),
            ("Total Tasks", total_tasks, "📋", SECONDARY),
            ("Upcoming", upcoming_tasks, "⏰", PRIMARY)
        ]
        
        for idx, (title, value, icon, color) in enumerate(stats_data):
            card = StatCard(stats_grid, title, value, icon, color)
            card.grid(row=0, column=idx, padx=10, sticky="ew")
            stats_grid.grid_columnconfigure(idx, weight=1)
    
    except Exception as e:
        tk.Label(parent, text=f"Error loading stats: {e}",
                fg=DANGER, bg=BG_MAIN).pack()
    
    # Recent Activity Section
    recent_frame = ModernCard(parent)
    recent_frame.pack(fill="both", expand=True)
    
    # Card header
    card_header = tk.Frame(recent_frame, bg=BG_CARD)
    card_header.pack(fill="x", padx=20, pady=(20, 10))
    
    tk.Label(card_header, text="Recent Tasks", font=FONT_HEADER,
            fg=TEXT_PRIMARY, bg=BG_CARD).pack(side="left")
    
    refresh_btn = ModernButton(card_header, "Refresh", 
                               lambda: show_dashboard(parent),
                               style="outline", width=10)
    refresh_btn.pack(side="right")
    
    # Scrollable task list
    canvas = tk.Canvas(recent_frame, bg=BG_CARD, highlightthickness=0)
    scrollbar = ttk.Scrollbar(recent_frame, orient="vertical", command=canvas.yview)
    scrollable = tk.Frame(canvas, bg=BG_CARD)
    
    scrollable.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=scrollable, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    
    try:
        conn = Database.connect()
        cursor = conn.cursor()
        
        # Only fetch existing tasks (deleted tasks won't appear)
        query = """
        SELECT t.task_id, t.task_title, t.date, t.time,
               a.activity_name, a.priority, a.status,
               u.first_name, u.last_name
        FROM tasks t
        JOIN activities a ON t.activity_id = a.activity_id
        JOIN users u ON t.user_id = u.user_id
        ORDER BY t.task_id DESC
        LIMIT 10
        """
        cursor.execute(query)
        tasks = cursor.fetchall()
        conn.close()
        
        if tasks:
            for task in tasks:
                task_card = create_task_card(scrollable, task)
                task_card.pack(fill="x", padx=20, pady=5)
        else:
            tk.Label(scrollable, text="📭 No tasks yet\nCreate your first schedule to get started!",
                    font=FONT_BODY, fg=TEXT_SECONDARY, bg=BG_CARD,
                    justify="center").pack(pady=50)
    
    except Exception as e:
        tk.Label(scrollable, text=f"Error loading tasks: {e}",
                fg=DANGER, bg=BG_CARD).pack(pady=20)
    
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")


def create_task_card(parent, task):
    """Create a task card widget"""
    task_id, title, date, time, activity, priority, status, fname, lname = task
    
    card = tk.Frame(parent, bg="#f8fafc", relief=tk.FLAT, bd=0,
                   highlightthickness=1, highlightbackground=BORDER_COLOR)
    
    # Priority indicator
    priority_colors = {"High": DANGER, "Medium": WARNING, "Low": SUCCESS}
    indicator = tk.Frame(card, bg=priority_colors.get(priority, INFO), width=5)
    indicator.pack(side="left", fill="y")
    
    # Content
    content = tk.Frame(card, bg="#f8fafc")
    content.pack(side="left", fill="both", expand=True, padx=15, pady=12)
    
    # Title and activity
    tk.Label(content, text=title, font=FONT_BODY_BOLD,
            fg=TEXT_PRIMARY, bg="#f8fafc", anchor="w").pack(fill="x")
    
    info_text = f"🎯 {activity} • 📅 {date}"
    if time:
        info_text += f" • ⏰ {time}"
    info_text += f" • 👤 {fname} {lname}"
    
    tk.Label(content, text=info_text, font=FONT_SMALL,
            fg=TEXT_SECONDARY, bg="#f8fafc", anchor="w").pack(fill="x", pady=(3, 0))
    
    # Status badge
    status_colors = {
        "Pending": ("#fef3c7", "#92400e"),
        "In Progress": ("#dbeafe", "#1e40af"),
        "Done": ("#d1fae5", "#065f46")
    }
    bg, fg = status_colors.get(status, ("#f3f4f6", TEXT_PRIMARY))
    
    badge = tk.Label(card, text=status, font=FONT_SMALL,
                    bg=bg, fg=fg, padx=12, pady=4)
    badge.pack(side="right", padx=15)
    
    return card