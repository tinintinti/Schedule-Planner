
import tkinter as tk
from config.styles import *


class ModernButton(tk.Button):
    """Modern styled button with hover effects"""
    
    def __init__(self, parent, text, command, style="primary", icon="", **kwargs):
        colors = {
            "primary": (PRIMARY, "white", PRIMARY_DARK),
            "secondary": (SECONDARY, "white", "#d97706"),
            "success": (SUCCESS, "white", "#059669"),
            "danger": (DANGER, "white", "#dc2626"),
            "info": (INFO, "white", "#2563eb"),
            "outline": ("white", PRIMARY, PRIMARY_LIGHT)
        }
        
        bg, fg, hover = colors.get(style, colors["primary"])
        
        super().__init__(
            parent,
            text=f"{icon} {text}" if icon else text,
            command=command,
            bg=bg,
            fg=fg,
            font=FONT_BUTTON,
            relief=tk.FLAT,
            cursor="hand2",
            padx=20,
            pady=10,
            **kwargs
        )
        
        self.default_bg = bg
        self.hover_bg = hover
        
        self.bind("<Enter>", lambda e: self.config(bg=self.hover_bg))
        self.bind("<Leave>", lambda e: self.config(bg=self.default_bg))