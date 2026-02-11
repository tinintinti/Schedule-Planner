
import tkinter as tk
from tkinter import ttk
from config.styles import *
from config.database import Database
from components.buttons import ModernButton
from components.cards import ModernCard


def show_reports(parent):
    """Display the reports and analytics view"""
    header = tk.Frame(parent, bg=BG_MAIN)
    header.pack(fill="x", pady=(0, 20))
    
    tk.Label(header, text="Reports & Analytics", font=FONT_TITLE,
            fg=TEXT_PRIMARY, bg=BG_MAIN).pack(side="left")
    
    # Report selector
    selector_frame = tk.Frame(header, bg=BG_MAIN)
    selector_frame.pack(side="right")
    
    tk.Label(selector_frame, text="Report Type:", font=FONT_BODY,
            fg=TEXT_SECONDARY, bg=BG_MAIN).pack(side="left", padx=(0, 10))
    
    report_var = tk.StringVar(value="Tasks by Status")
    report_combo = ttk.Combobox(selector_frame, textvariable=report_var,
                               values=["Tasks by Status", "Tasks by Priority", "Tasks by Category",
                                      "User Activity Summary", "Upcoming Deadlines"],
                               state="readonly", font=FONT_BODY, width=20)
    report_combo.pack(side="left", padx=5)
    
    ModernButton(selector_frame, "Generate", 
                lambda: generate_report_view(report_var.get(), parent),
                style="primary", width=10).pack(side="left", padx=5)
    
    # Report content
    global report_content_frame
    report_content_frame = ModernCard(parent)
    report_content_frame.pack(fill="both", expand=True)
    
    # Initial report
    generate_report_view("Tasks by Status", parent)


def generate_report_view(report_type, parent):
    """Generate and display specific report"""
    global report_content_frame
    
    for widget in report_content_frame.winfo_children():
        widget.destroy()
    
    # Header
    tk.Label(report_content_frame, text=f"📊 {report_type}", font=FONT_HEADER,
            fg=TEXT_PRIMARY, bg=BG_CARD).pack(pady=20)
    
    # Scrollable content
    canvas = tk.Canvas(report_content_frame, bg=BG_CARD, highlightthickness=0)
    scrollbar = ttk.Scrollbar(report_content_frame, orient="vertical", command=canvas.yview)
    scrollable = tk.Frame(canvas, bg=BG_CARD)
    
    scrollable.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=scrollable, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    
    try:
        conn = Database.connect()
        cursor = conn.cursor()
        
        if report_type == "Tasks by Status":
            query = """
            SELECT a.status, COUNT(t.task_id) as count
            FROM activities a
            JOIN tasks t ON a.activity_id = t.activity_id
            GROUP BY a.status
            """
            cursor.execute(query)
            results = cursor.fetchall()
            
            status_colors = {
                "Pending": WARNING,
                "In Progress": INFO,
                "Done": SUCCESS
            }
            
            for status, count in results:
                create_report_item(scrollable, status, count, status_colors.get(status, PRIMARY))
        
        elif report_type == "Tasks by Priority":
            query = """
            SELECT a.priority, COUNT(t.task_id) as count
            FROM activities a
            JOIN tasks t ON a.activity_id = t.activity_id
            GROUP BY a.priority
            ORDER BY FIELD(a.priority, 'High', 'Medium', 'Low')
            """
            cursor.execute(query)
            results = cursor.fetchall()
            
            priority_colors = {"High": DANGER, "Medium": WARNING, "Low": SUCCESS}
            
            for priority, count in results:
                create_report_item(scrollable, priority, count, priority_colors.get(priority, PRIMARY))
        
        elif report_type == "Tasks by Category":
            query = """
            SELECT a.category, COUNT(t.task_id) as count
            FROM activities a
            JOIN tasks t ON a.activity_id = t.activity_id
            GROUP BY a.category
            """
            cursor.execute(query)
            results = cursor.fetchall()
            
            for category, count in results:
                create_report_item(scrollable, category, count, INFO)
        
        elif report_type == "User Activity Summary":
            query = """
            SELECT u.first_name, u.last_name,
                   COUNT(DISTINCT a.activity_id) as activities,
                   COUNT(t.task_id) as tasks
            FROM users u
            LEFT JOIN activities a ON u.user_id = a.user_id
            LEFT JOIN tasks t ON u.user_id = t.user_id
            GROUP BY u.user_id
            """
            cursor.execute(query)
            results = cursor.fetchall()
            
            for fname, lname, act_count, task_count in results:
                create_user_report_item(scrollable, f"{fname} {lname}", act_count, task_count)
        
        elif report_type == "Upcoming Deadlines":
            query = """
            SELECT t.task_title, t.date, t.time, a.activity_name, a.priority, a.status
            FROM tasks t
            JOIN activities a ON t.activity_id = a.activity_id
            WHERE t.date >= CURDATE()
            ORDER BY t.date ASC, t.time ASC
            LIMIT 15
            """
            cursor.execute(query)
            results = cursor.fetchall()
            
            if results:
                for title, date, time, activity, priority, status in results:
                    create_deadline_item(scrollable, title, date, time, activity, priority, status)
            else:
                tk.Label(scrollable, text="📅 No upcoming deadlines", font=FONT_BODY,
                        fg=TEXT_SECONDARY, bg=BG_CARD).pack(pady=50)
        
        conn.close()
        
    except Exception as e:
        tk.Label(scrollable, text=f"❌ Error generating report:\n{e}",
                font=FONT_BODY, fg=DANGER, bg=BG_CARD).pack(pady=50)
    
    canvas.pack(side="left", fill="both", expand=True, padx=20, pady=(0, 20))
    scrollbar.pack(side="right", fill="y", pady=(0, 20))


def create_report_item(parent, label, value, color):
    """Create a report item widget"""
    item = tk.Frame(parent, bg="#f8fafc", relief=tk.FLAT, bd=0,
                   highlightthickness=1, highlightbackground=BORDER_COLOR)
    item.pack(fill="x", padx=20, pady=5)
    
    # Color indicator
    tk.Frame(item, bg=color, width=5).pack(side="left", fill="y")
    
    # Content
    content = tk.Frame(item, bg="#f8fafc")
    content.pack(side="left", fill="both", expand=True, padx=20, pady=15)
    
    tk.Label(content, text=label, font=FONT_BODY_BOLD,
            fg=TEXT_PRIMARY, bg="#f8fafc").pack(side="left")
    
    tk.Label(content, text=f"{value} tasks", font=FONT_BODY,
            fg=TEXT_SECONDARY, bg="#f8fafc").pack(side="right")


def create_user_report_item(parent, name, activities, tasks):
    """Create a user activity report item"""
    item = tk.Frame(parent, bg="#f8fafc", relief=tk.FLAT, bd=0,
                   highlightthickness=1, highlightbackground=BORDER_COLOR)
    item.pack(fill="x", padx=20, pady=5)
    
    content = tk.Frame(item, bg="#f8fafc")
    content.pack(fill="both", expand=True, padx=20, pady=15)
    
    tk.Label(content, text=name, font=FONT_BODY_BOLD,
            fg=TEXT_PRIMARY, bg="#f8fafc").pack(side="left")
    
    stats = tk.Frame(content, bg="#f8fafc")
    stats.pack(side="right")
    
    tk.Label(stats, text=f"🎯 {activities} activities", font=FONT_SMALL,
            fg=TEXT_SECONDARY, bg="#f8fafc").pack(side="left", padx=10)
    tk.Label(stats, text=f"📋 {tasks} tasks", font=FONT_SMALL,
            fg=TEXT_SECONDARY, bg="#f8fafc").pack(side="left")


def create_deadline_item(parent, title, date, time, activity, priority, status):
    """Create a deadline item widget"""
    item = tk.Frame(parent, bg="#f8fafc", relief=tk.FLAT, bd=0,
                   highlightthickness=1, highlightbackground=BORDER_COLOR)
    item.pack(fill="x", padx=20, pady=5)
    
    # Priority indicator
    priority_colors = {"High": DANGER, "Medium": WARNING, "Low": SUCCESS}
    tk.Frame(item, bg=priority_colors.get(priority, INFO), width=5).pack(side="left", fill="y")
    
    # Content
    content = tk.Frame(item, bg="#f8fafc")
    content.pack(fill="both", expand=True, padx=20, pady=15)
    
    # Left side
    left = tk.Frame(content, bg="#f8fafc")
    left.pack(side="left", fill="both", expand=True)
    
    tk.Label(left, text=title, font=FONT_BODY_BOLD,
            fg=TEXT_PRIMARY, bg="#f8fafc").pack(anchor="w")
    
    info_text = f"🎯 {activity} • 📅 {date}"
    if time:
        info_text += f" ⏰ {time}"
    
    tk.Label(left, text=info_text, font=FONT_SMALL,
            fg=TEXT_SECONDARY, bg="#f8fafc").pack(anchor="w", pady=(3, 0))
    
    # Right side - badges
    right = tk.Frame(content, bg="#f8fafc")
    right.pack(side="right")
    
    # Priority badge
    pri_badge = tk.Label(right, text=priority, font=FONT_SMALL,
                        bg=priority_colors.get(priority, INFO), fg="white",
                        padx=10, pady=4)
    pri_badge.pack(side="right", padx=5)
    
    # Status badge
    status_colors = {
        "Pending": ("#fef3c7", "#92400e"),
        "In Progress": ("#dbeafe", "#1e40af"),
        "Done": ("#d1fae5", "#065f46")
    }
    bg, fg = status_colors.get(status, ("#f3f4f6", TEXT_PRIMARY))
    
    status_badge = tk.Label(right, text=status, font=FONT_SMALL,
                           bg=bg, fg=fg, padx=10, pady=4)
    status_badge.pack(side="right", padx=5)


