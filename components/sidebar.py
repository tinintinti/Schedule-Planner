
import tkinter as tk
from config.styles import *


class Sidebar:
    """Application sidebar with navigation buttons"""
    
    def __init__(self, parent, on_navigate):
        """
        Initialize sidebar
        
        Args:
            parent: Parent widget
            on_navigate: Callback function for navigation (receives tab name)
        """
        self.sidebar = tk.Frame(parent, bg=BG_SIDEBAR, width=250)
        self.sidebar.grid(row=0, column=0, sticky="ns")
        self.sidebar.grid_propagate(False)
        
        self.on_navigate = on_navigate
        self._create_widgets()
    
    def _create_widgets(self):
        """Create sidebar widgets"""
        # Logo/Title
        logo_frame = tk.Frame(self.sidebar, bg=BG_SIDEBAR)
        logo_frame.pack(pady=30, padx=20)
        
        tk.Label(logo_frame, text="📅", font=("Segoe UI", 32),
                bg=BG_SIDEBAR, fg="white").pack()
        tk.Label(logo_frame, text="Schedule Planner",
                font=("Segoe UI", 14, "bold"),
                bg=BG_SIDEBAR, fg="white").pack(pady=(10, 0))
        
        # Separator
        tk.Frame(self.sidebar, bg="#334155", height=1).pack(fill="x", padx=20, pady=20)
        
        # Navigation buttons
        nav_buttons = [
            ("📊", "Dashboard", "dashboard"),
            ("➕", "Create", "create"),
            ("📝", "Manage", "manage"),
            ("📈", "Reports", "reports"),
        ]
        
        for icon, text, tab_name in nav_buttons:
            self._create_nav_button(icon, text, tab_name)
        
        # Footer
        tk.Frame(self.sidebar, bg=BG_SIDEBAR).pack(fill="both", expand=True)
        
        footer = tk.Frame(self.sidebar, bg="#334155")
        footer.pack(fill="x", side="bottom")
        
        tk.Label(footer, text="v2.0 Modern", font=FONT_SMALL,
                bg="#334155", fg=TEXT_LIGHT).pack(pady=15)
    
    def _create_nav_button(self, icon, text, tab_name):
        """Create a navigation button"""
        btn = tk.Button(
            self.sidebar,
            text=f"{icon}  {text}",
            command=lambda: self.on_navigate(tab_name),
            bg=BG_SIDEBAR,
            fg="white",
            font=FONT_BODY_BOLD,
            relief=tk.FLAT,
            cursor="hand2",
            anchor="w",
            padx=30,
            pady=15
        )
        btn.pack(fill="x")
        
        # Hover effects
        btn.bind("<Enter>", lambda e: btn.config(bg="#334155"))
        btn.bind("<Leave>", lambda e: btn.config(bg=BG_SIDEBAR))