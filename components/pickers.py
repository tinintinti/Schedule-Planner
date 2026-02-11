
import tkinter as tk
from tkinter import ttk
from config.styles import *


class TimePicker(tk.Frame):
    """Custom time picker widget with hour, minute, and AM/PM"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=BG_CARD, **kwargs)
        
        # Hour
        self.hour_var = tk.StringVar(value="12")
        hour_frame = tk.Frame(self, bg=BG_CARD)
        hour_frame.pack(side="left")
        
        tk.Label(hour_frame, text="Hour", font=FONT_SMALL, 
                fg=TEXT_SECONDARY, bg=BG_CARD).pack()
        hour_spin = ttk.Spinbox(hour_frame, from_=1, to=12, 
                               textvariable=self.hour_var,
                               width=5, font=FONT_BODY)
        hour_spin.pack()
        
        tk.Label(self, text=":", font=("Segoe UI", 16, "bold"),
                fg=TEXT_PRIMARY, bg=BG_CARD).pack(side="left", padx=5)
        
        # Minute
        self.minute_var = tk.StringVar(value="00")
        minute_frame = tk.Frame(self, bg=BG_CARD)
        minute_frame.pack(side="left")
        
        tk.Label(minute_frame, text="Minute", font=FONT_SMALL,
                fg=TEXT_SECONDARY, bg=BG_CARD).pack()
        minute_spin = ttk.Spinbox(minute_frame, from_=0, to=59,
                                 textvariable=self.minute_var,
                                 width=5, font=FONT_BODY, format="%02.0f")
        minute_spin.pack()
        
        # AM/PM
        self.period_var = tk.StringVar(value="AM")
        period_frame = tk.Frame(self, bg=BG_CARD)
        period_frame.pack(side="left", padx=(10, 0))
        
        tk.Label(period_frame, text="Period", font=FONT_SMALL,
                fg=TEXT_SECONDARY, bg=BG_CARD).pack()
        period_combo = ttk.Combobox(period_frame, textvariable=self.period_var,
                                   values=["AM", "PM"], state="readonly",
                                   width=5, font=FONT_BODY)
        period_combo.pack()
    
    def get_time(self):
        """Return time in HH:MM format (24-hour)"""
        try:
            hour = int(self.hour_var.get())
            minute = int(self.minute_var.get())
            period = self.period_var.get()
            
            # Convert to 24-hour format
            if period == "PM" and hour != 12:
                hour += 12
            elif period == "AM" and hour == 12:
                hour = 0
            
            return f"{hour:02d}:{minute:02d}"
        except:
            return "12:00"
    
    def set_time(self, time_str):
        """Set time from HH:MM format (24-hour or 12-hour)"""
        if not time_str:
            return
        
        try:
            if ":" in time_str:
                parts = time_str.split(":")
                hour = int(parts[0])
                minute = int(parts[1].split()[0])
                
                # Convert from 24-hour to 12-hour
                if hour == 0:
                    self.hour_var.set("12")
                    self.period_var.set("AM")
                elif hour < 12:
                    self.hour_var.set(str(hour))
                    self.period_var.set("AM")
                elif hour == 12:
                    self.hour_var.set("12")
                    self.period_var.set("PM")
                else:
                    self.hour_var.set(str(hour - 12))
                    self.period_var.set("PM")
                
                self.minute_var.set(f"{minute:02d}")
        except:
            pass