
import tkinter as tk
from config.styles import *


class ModernCard(tk.Frame):
    """Modern card container with border"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(
            parent,
            bg=BG_CARD,
            relief=tk.FLAT,
            bd=0,
            highlightthickness=1,
            highlightbackground=BORDER_COLOR,
            **kwargs
        )


class StatCard(tk.Frame):
    """Statistics card with icon and value"""
    
    def __init__(self, parent, title, value, icon, color):
        super().__init__(
            parent, 
            bg=BG_CARD, 
            relief=tk.FLAT, 
            bd=0,
            highlightthickness=1, 
            highlightbackground=BORDER_COLOR
        )
        
        # Icon section
        icon_frame = tk.Frame(self, bg=color, width=60, height=60)
        icon_frame.pack(side="left", padx=20, pady=20)
        icon_frame.pack_propagate(False)
        
        tk.Label(
            icon_frame, 
            text=icon, 
            font=("Segoe UI", 24),
            fg="white", 
            bg=color
        ).place(relx=0.5, rely=0.5, anchor="center")
        
        # Content section
        content_frame = tk.Frame(self, bg=BG_CARD)
        content_frame.pack(side="left", fill="both", expand=True, padx=(0, 20), pady=20)
        
        tk.Label(
            content_frame, 
            text=str(value), 
            font=("Segoe UI", 28, "bold"),
            fg=TEXT_PRIMARY, 
            bg=BG_CARD
        ).pack(anchor="w")
        
        tk.Label(
            content_frame, 
            text=title, 
            font=FONT_BODY,
            fg=TEXT_SECONDARY, 
            bg=BG_CARD
        ).pack(anchor="w")