import tkinter as tk
from config.styles import *
from components.sidebar import Sidebar
from views.dashboard import show_dashboard
from views.create import show_create
from views.manage import show_manage
from views.reports import show_reports


class SchedulePlannerApp:
    """Main application class"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Smart Schedule Planner")
        self.root.geometry("1400x800")
        self.root.configure(bg=BG_MAIN)
        
        # Make window responsive
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        
        self.current_tab = None
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup main UI components"""
        # Create sidebar
        self.sidebar = Sidebar(self.root, self.show_tab)
        
        # Main content area
        self.main_content = tk.Frame(self.root, bg=BG_MAIN)
        self.main_content.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        
        # Show initial tab
        self.show_tab("dashboard")
    
    def clear_content(self):
        """Clear main content area"""
        for widget in self.main_content.winfo_children():
            widget.destroy()
    
    def show_tab(self, tab_name):
        """
        Navigate to a specific tab
        
        Args:
            tab_name: Name of tab to display (dashboard, create, manage, reports)
        """
        self.current_tab = tab_name
        self.clear_content()
        
        # Display the appropriate view
        if tab_name == "dashboard":
            show_dashboard(self.main_content)
        elif tab_name == "create":
            show_create(self.main_content)
        elif tab_name == "manage":
            show_manage(self.main_content)
        elif tab_name == "reports":
            show_reports(self.main_content)
    
    def run(self):
        """Start the application"""
        self.root.mainloop()


if __name__ == "__main__":
    app = SchedulePlannerApp()
    app.run()
