#!/usr/bin/env python3
"""
Real-Time RAM Optimizer for Mac
Menu bar application with expandable dashboard
"""

import rumps
import psutil
import subprocess
import threading
import json
import os
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox, filedialog
from datetime import datetime
import csv
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import deque


class RAMOptimizerDashboard:
    """The expandable tkinter dashboard GUI"""
    def __init__(self):
        self.root = None
        self.memory_history = deque(maxlen=60)
        self.timestamps = deque(maxlen=60)
        self.auto_optimize_threshold = 85.0
        self.dashboard_open = False
        self.config_path = os.path.expanduser('~/.ram_optimizer_config.json')
        self.log_path = os.path.expanduser('~/.ram_optimizer.log')

    @staticmethod
    def log_action(action, details=""):
        """Log an optimization action to the log file"""
        log_path = os.path.expanduser('~/.ram_optimizer.log')
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            mem = psutil.virtual_memory()
            mem_info = f"[RAM {mem.percent:.1f}%]"
        except Exception:
            mem_info = ""
        log_entry = f"{timestamp} {mem_info} {action}{' - ' + details if details else ''}\n"
        try:
            with open(log_path, 'a') as f:
                f.write(log_entry)
            # Truncate if too large (keep last ~5000 lines)
            if os.path.getsize(log_path) > 500_000:
                with open(log_path, 'r') as f:
                    lines = f.readlines()
                with open(log_path, 'w') as f:
                    f.writelines(lines[-2000:])
        except IOError:
            pass

    @staticmethod
    def view_logs(parent_root):
        """Open a window to view optimization logs"""
        log_path = os.path.expanduser('~/.ram_optimizer.log')
        
        log_window = tk.Toplevel(parent_root)
        log_window.title("Optimization Action Logs")
        log_window.geometry("800x500")
        log_window.configure(bg='#1e1e1e')
        
        # Title
        title = tk.Label(log_window, text="📋 Optimization Action Logs",
            font=('Helvetica', 18, 'bold'), bg='#1e1e1e', fg='#00ff00')
        title.pack(pady=15)
        
        # Text area with scrollbar
        text_frame = tk.Frame(log_window, bg='#1e1e1e')
        text_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        log_text = tk.Text(text_frame, bg='#2d2d2d', fg='#cccccc',
            font=('Courier', 11), wrap=tk.NONE, insertbackground='white')
        log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar_y = tk.Scrollbar(text_frame, orient=tk.VERTICAL, command=log_text.yview)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        log_text.config(yscrollcommand=scrollbar_y.set)
        
        # Load log content
        try:
            if os.path.exists(log_path):
                with open(log_path, 'r') as f:
                    content = f.read()
                log_text.insert(tk.END, content)
                log_text.see(tk.END)
            else:
                log_text.insert(tk.END, "No logs yet. Run some optimization actions to populate the log.")
        except IOError:
            log_text.insert(tk.END, "Error reading log file.")
        
        log_text.config(state=tk.DISABLED)
        
        # Close button
        close_btn = tk.Button(log_window, text="Close", command=log_window.destroy,
            font=('Helvetica', 12, 'bold'), bg='#45b7d1', fg='white',
            padx=30, pady=8, relief=tk.FLAT, cursor='hand2')
        close_btn.pack(pady=15)
        
        # Clear logs button
        def clear_logs():
            if messagebox.askyesno("Clear Logs", "Are you sure you want to clear all logs?"):
                try:
                    with open(log_path, 'w') as f:
                        f.write('')
                    log_text.config(state=tk.NORMAL)
                    log_text.delete('1.0', tk.END)
                    log_text.insert(tk.END, "Logs cleared at " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n")
                    log_text.config(state=tk.DISABLED)
                except IOError:
                    pass
        
        clear_btn = tk.Button(log_window, text="🗑️ Clear Logs", command=clear_logs,
            font=('Helvetica', 11, 'bold'), bg='#ff6b6b', fg='white',
            padx=20, pady=6, relief=tk.FLAT, cursor='hand2')
        clear_btn.pack(pady=5)

    def show_dashboard(self):
        """Show the dashboard window"""
        if self.dashboard_open:
            if self.root:
                self.root.lift()
            return

        self.dashboard_open = True
        self.root = tk.Tk()
        self.root.title("RAM Optimizer Dashboard")
        self.root.geometry("900x920")
        self.root.configure(bg='#1e1e1e')
        
        # Load settings
        settings = self.load_settings()
        
        # Auto-optimization settings
        self.auto_optimize = tk.BooleanVar(value=settings.get('auto_optimize', False))
        self.auto_optimize_threshold_var = tk.DoubleVar(value=settings.get('auto_optimize_threshold', 85.0))
        
        # Alert settings
        self.alert_enabled = tk.BooleanVar(value=settings.get('alert_enabled', False))
        self.alert_threshold_var = tk.DoubleVar(value=settings.get('alert_threshold', 80.0))
        
        # Battery-aware setting
        self.battery_aware = tk.BooleanVar(value=settings.get('battery_aware', True))
        
        # Theme setting
        self.dark_mode = tk.BooleanVar(value=settings.get('dark_mode', True))
        
        self.create_gui()
        
        # Start GUI update
        self.update_gui()
        
        # Handle window closing
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.root.mainloop()

    def on_closing(self):
        """Handle window closing"""
        self.dashboard_open = False
        if self.root:
            self.root.destroy()
            self.root = None

    def create_gui(self):
        """Create the main GUI interface"""
        # Title
        title_label = tk.Label(
            self.root, 
            text="🚀 RAM Optimizer Dashboard", 
            font=('Helvetica', 24, 'bold'),
            bg='#1e1e1e', 
            fg='#00ff00'
        )
        title_label.pack(pady=20)
        
        # Main frame
        main_frame = tk.Frame(self.root, bg='#1e1e1e')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Memory Stats Frame
        stats_frame = tk.LabelFrame(
            main_frame, 
            text="Memory Statistics", 
            font=('Helvetica', 14, 'bold'),
            bg='#2d2d2d', 
            fg='#ffffff'
        )
        stats_frame.pack(fill=tk.X, pady=10)
        
        # Memory labels
        self.total_memory_label = self.create_stat_label(stats_frame, "Total Memory:", 0)
        self.used_memory_label = self.create_stat_label(stats_frame, "Used Memory:", 1)
        self.free_memory_label = self.create_stat_label(stats_frame, "Free Memory:", 2)
        self.available_memory_label = self.create_stat_label(stats_frame, "Available Memory:", 3)
        self.memory_percent_label = self.create_stat_label(stats_frame, "Memory Usage:", 4)
        
        # Swap Memory Labels
        self.swap_total_label = self.create_stat_label(stats_frame, "Swap Total:", 5)
        self.swap_used_label = self.create_stat_label(stats_frame, "Swap Used:", 6)
        self.swap_percent_label = self.create_stat_label(stats_frame, "Swap Usage:", 7)
        
        # CPU Usage Label
        self.cpu_percent_label = self.create_stat_label(stats_frame, "CPU Usage:", 8)
        
        # System Info Labels
        self.uptime_label = self.create_stat_label(stats_frame, "System Uptime:", 9)
        self.boot_time_label = self.create_stat_label(stats_frame, "Boot Time:", 10)
        
        # Temperature Label
        self.temp_label = self.create_stat_label(stats_frame, "CPU Temp:", 11)
        
        # Network labels
        self.net_sent_label = self.create_stat_label(stats_frame, "Net Sent:", 12)
        self.net_recv_label = self.create_stat_label(stats_frame, "Net Recv:", 13)
        
        # Track previous network counters for delta calculation
        self._prev_net = psutil.net_io_counters()
        self._prev_net_time = datetime.now().timestamp()
        
        # Memory Pressure Indicator
        pressure_frame = tk.LabelFrame(
            main_frame, 
            text="Memory Pressure", 
            font=('Helvetica', 14, 'bold'),
            bg='#2d2d2d', 
            fg='#ffffff'
        )
        pressure_frame.pack(fill=tk.X, pady=10)
        
        self.pressure_canvas = tk.Canvas(pressure_frame, height=30, bg='#2d2d2d', highlightthickness=0)
        self.pressure_canvas.pack(fill=tk.X, padx=10, pady=10)
        
        self.pressure_label = tk.Label(
            pressure_frame, 
            text="Normal", 
            font=('Helvetica', 12, 'bold'),
            bg='#2d2d2d', 
            fg='#00ff00'
        )
        self.pressure_label.pack(pady=5)
        
        # Memory Usage Graph
        graph_frame = tk.LabelFrame(
            main_frame, 
            text="Memory Usage History (Last 60 seconds)", 
            font=('Helvetica', 14, 'bold'),
            bg='#2d2d2d', 
            fg='#ffffff'
        )
        graph_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.fig, self.ax = plt.subplots(figsize=(8, 3), facecolor='#2d2d2d')
        self.ax.set_facecolor('#1e1e1e')
        self.ax.tick_params(colors='white')
        self.ax.spines['bottom'].set_color('white')
        self.ax.spines['top'].set_color('white')
        self.ax.spines['left'].set_color('white')
        self.ax.spines['right'].set_color('white')
        self.ax.set_ylabel('Memory %', color='white')
        self.ax.set_ylim(0, 100)
        self.ax.grid(True, alpha=0.3)
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=graph_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Top Processes Frame
        processes_frame = tk.LabelFrame(
            main_frame,
            text="Top Memory-Consuming Processes",
            font=('Helvetica', 14, 'bold'),
            bg='#2d2d2d',
            fg='#ffffff'
        )
        processes_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Treeview style
        style = ttk.Style()
        style.theme_use('default')
        style.configure("Treeview",
            background="#1e1e1e",
            foreground="white",
            fieldbackground="#1e1e1e",
            rowheight=25,
            font=('Helvetica', 10)
        )
        style.configure("Treeview.Heading",
            background="#2d2d2d",
            foreground="white",
            font=('Helvetica', 11, 'bold')
        )
        style.map('Treeview', background=[('selected', '#45b7d1')])
        
        columns = ('pid', 'name', 'memory_pct', 'memory_mb')
        self.processes_tree = ttk.Treeview(processes_frame, columns=columns, show='headings', height=10)
        self.processes_tree.heading('pid', text='PID')
        self.processes_tree.heading('name', text='Process Name')
        self.processes_tree.heading('memory_pct', text='Memory %')
        self.processes_tree.heading('memory_mb', text='Memory (MB)')
        self.processes_tree.column('pid', width=70, anchor='center')
        self.processes_tree.column('name', width=300, anchor='w')
        self.processes_tree.column('memory_pct', width=120, anchor='center')
        self.processes_tree.column('memory_mb', width=120, anchor='center')
        
        scrollbar = ttk.Scrollbar(processes_frame, orient=tk.VERTICAL, command=self.processes_tree.yview)
        self.processes_tree.configure(yscrollcommand=scrollbar.set)
        
        self.processes_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)
        
        # Right-click context menu for process kill
        self.process_context_menu = tk.Menu(self.root, tearoff=0, bg='#2d2d2d', fg='white',
            activebackground='#ff6b6b', activeforeground='white', font=('Helvetica', 11))
        self.process_context_menu.add_command(label="🔪 Kill Process", command=self.kill_selected_process)
        
        def show_context_menu(event):
            selected = self.processes_tree.identify_row(event.y)
            if selected:
                self.processes_tree.selection_set(selected)
                self.process_context_menu.post(event.x_root, event.y_root)
        
        self.processes_tree.bind("<Button-2>", show_context_menu)  # macOS right-click
        self.processes_tree.bind("<Button-3>", show_context_menu)  # Windows/Linux right-click
        if hasattr(self.processes_tree, 'bind'):
            self.processes_tree.bind("<Control-Button-1>", show_context_menu)  # macOS Ctrl+click
        
        # Control Buttons Frame
        control_frame = tk.LabelFrame(
            main_frame, 
            text="Optimization Controls", 
            font=('Helvetica', 14, 'bold'),
            bg='#2d2d2d', 
            fg='#ffffff'
        )
        control_frame.pack(fill=tk.X, pady=10)
        
        # Buttons
        button_frame = tk.Frame(control_frame, bg='#2d2d2d')
        button_frame.pack(pady=10)
        
        self.purge_button = tk.Button(
            button_frame, 
            text="🧹 Purge Memory", 
            command=self.purge_memory,
            font=('Helvetica', 12, 'bold'),
            bg='#ff6b6b', 
            fg='white',
            padx=20, 
            pady=10,
            relief=tk.FLAT,
            cursor='hand2'
        )
        self.purge_button.pack(side=tk.LEFT, padx=10)
        
        self.clear_cache_button = tk.Button(
            button_frame, 
            text="🗑️ Clear Caches", 
            command=self.clear_caches,
            font=('Helvetica', 12, 'bold'),
            bg='#4ecdc4', 
            fg='white',
            padx=20, 
            pady=10,
            relief=tk.FLAT,
            cursor='hand2'
        )
        self.clear_cache_button.pack(side=tk.LEFT, padx=10)
        
        self.optimize_button = tk.Button(
            button_frame, 
            text="⚡ Full Optimization", 
            command=self.full_optimization,
            font=('Helvetica', 12, 'bold'),
            bg='#45b7d1', 
            fg='white',
            padx=20, 
            pady=10,
            relief=tk.FLAT,
            cursor='hand2'
        )
        self.optimize_button.pack(side=tk.LEFT, padx=10)
        
        self.export_button = tk.Button(
            button_frame,
            text="📊 Export CSV",
            command=self.export_csv,
            font=('Helvetica', 12, 'bold'),
            bg='#2ecc71',
            fg='white',
            padx=20,
            pady=10,
            relief=tk.FLAT,
            cursor='hand2'
        )
        self.export_button.pack(side=tk.LEFT, padx=10)
        
        # Auto-optimization settings
        auto_frame = tk.Frame(control_frame, bg='#2d2d2d')
        auto_frame.pack(pady=10)
        
        auto_check = tk.Checkbutton(
            auto_frame, 
            text="Auto-Optimize when memory usage exceeds:", 
            variable=self.auto_optimize,
            font=('Helvetica', 11),
            bg='#2d2d2d', 
            fg='white',
            selectcolor='#2d2d2d',
            activebackground='#2d2d2d',
            activeforeground='white',
            command=self.update_threshold
        )
        auto_check.pack(side=tk.LEFT, padx=5)
        
        threshold_scale = tk.Scale(
            auto_frame, 
            from_=50, 
            to=95, 
            orient=tk.HORIZONTAL,
            variable=self.auto_optimize_threshold_var,
            font=('Helvetica', 10),
            bg='#2d2d2d', 
            fg='white',
            highlightthickness=0,
            troughcolor='#4a4a4a',
            activebackground='#45b7d1',
            command=lambda x: self.update_threshold()
        )
        threshold_scale.pack(side=tk.LEFT, padx=5)
        
        threshold_label = tk.Label(
            auto_frame, 
            text="%", 
            font=('Helvetica', 11),
            bg='#2d2d2d', 
            fg='white'
        )
        threshold_label.pack(side=tk.LEFT, padx=5)
        
        # Alert settings
        alert_frame = tk.Frame(control_frame, bg='#2d2d2d')
        alert_frame.pack(pady=10)
        
        alert_check = tk.Checkbutton(
            alert_frame,
            text="Alert when memory usage exceeds:",
            variable=self.alert_enabled,
            font=('Helvetica', 11),
            bg='#2d2d2d',
            fg='white',
            selectcolor='#2d2d2d',
            activebackground='#2d2d2d',
            activeforeground='white',
            command=self.save_settings
        )
        alert_check.pack(side=tk.LEFT, padx=5)
        
        alert_scale = tk.Scale(
            alert_frame,
            from_=50,
            to=99,
            orient=tk.HORIZONTAL,
            variable=self.alert_threshold_var,
            font=('Helvetica', 10),
            bg='#2d2d2d',
            fg='white',
            highlightthickness=0,
            troughcolor='#4a4a4a',
            activebackground='#45b7d1',
            command=lambda x: self.save_settings()
        )
        alert_scale.pack(side=tk.LEFT, padx=5)
        
        alert_pct_label = tk.Label(
            alert_frame,
            text="%",
            font=('Helvetica', 11),
            bg='#2d2d2d',
            fg='white'
        )
        alert_pct_label.pack(side=tk.LEFT, padx=5)
        
        # Battery-aware optimization setting
        battery_frame = tk.Frame(control_frame, bg='#2d2d2d')
        battery_frame.pack(pady=10)
        
        battery_check = tk.Checkbutton(
            battery_frame,
            text="🔋 Disable Auto-Optimize when on battery power",
            variable=self.battery_aware,
            font=('Helvetica', 11),
            bg='#2d2d2d',
            fg='white',
            selectcolor='#2d2d2d',
            activebackground='#2d2d2d',
            activeforeground='white',
            command=self.save_settings
        )
        battery_check.pack(side=tk.LEFT, padx=5)
        
        # Theme toggle
        theme_frame = tk.Frame(control_frame, bg='#2d2d2d')
        theme_frame.pack(pady=10)
        
        theme_check = tk.Checkbutton(
            theme_frame,
            text="🌙 Dark Mode",
            variable=self.dark_mode,
            font=('Helvetica', 11),
            bg='#2d2d2d',
            fg='white',
            selectcolor='#2d2d2d',
            activebackground='#2d2d2d',
            activeforeground='white',
            command=self.toggle_theme
        )
        theme_check.pack(side=tk.LEFT, padx=5)
        
        # Status bar
        self.status_label = tk.Label(
            self.root, 
            text="Ready", 
            font=('Helvetica', 10),
            bg='#1e1e1e', 
            fg='#888888',
            relief=tk.SUNKEN
        )
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)

    def update_threshold(self):
        """Update auto-optimize threshold and save settings"""
        self.auto_optimize_threshold = self.auto_optimize_threshold_var.get()
        self.save_settings()

    def load_settings(self):
        """Load settings from JSON config file"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    settings = json.load(f)
                return settings
        except (json.JSONDecodeError, IOError):
            pass
        return {}

    def save_settings(self):
        """Save settings to JSON config file"""
        settings = {
            'auto_optimize': self.auto_optimize.get() if hasattr(self, 'auto_optimize') else False,
            'auto_optimize_threshold': self.auto_optimize_threshold_var.get() if hasattr(self, 'auto_optimize_threshold_var') else 85.0,
            'alert_enabled': self.alert_enabled.get() if hasattr(self, 'alert_enabled') else False,
            'alert_threshold': self.alert_threshold_var.get() if hasattr(self, 'alert_threshold_var') else 80.0,
            'battery_aware': self.battery_aware.get() if hasattr(self, 'battery_aware') else True,
            'dark_mode': self.dark_mode.get() if hasattr(self, 'dark_mode') else True
        }
        try:
            with open(self.config_path, 'w') as f:
                json.dump(settings, f, indent=2)
        except IOError:
            pass

    def toggle_theme(self):
        """Toggle between dark and light themes"""
        dark = self.dark_mode.get()
        if not hasattr(self, '_widget_registry'):
            self._widget_registry = []
        
        if dark:
            self._apply_dark_theme()
        else:
            self._apply_light_theme()
        self.save_settings()

    def _apply_dark_theme(self):
        """Apply dark color theme to all widgets"""
        for widget_info in self._widget_registry:
            widget, attr_map = widget_info
            try:
                for attr, value in attr_map['dark'].items():
                    widget.config(**{attr: value})
            except Exception:
                pass
        try:
            self.root.configure(bg='#1e1e1e')
        except Exception:
            pass

    def _apply_light_theme(self):
        """Apply light color theme to all widgets"""
        for widget_info in self._widget_registry:
            widget, attr_map = widget_info
            try:
                for attr, value in attr_map['light'].items():
                    widget.config(**{attr: value})
            except Exception:
                pass
        try:
            self.root.configure(bg='#f0f0f0')
        except Exception:
            pass

    def _register_widget(self, widget, dark_attrs, light_attrs):
        """Register a widget for theme switching"""
        if not hasattr(self, '_widget_registry'):
            self._widget_registry = []
        self._widget_registry.append((widget, {'dark': dark_attrs, 'light': light_attrs}))

    def create_stat_label(self, parent, text, row):
        """Create a statistic label with theme support"""
        frame = tk.Frame(parent, bg='#2d2d2d')
        frame.pack(fill=tk.X, padx=10, pady=5)
        self._register_widget(frame, {'bg': '#2d2d2d'}, {'bg': '#ffffff'})

        label = tk.Label(
            frame,
            text=text,
            font=('Helvetica', 11),
            bg='#2d2d2d',
            fg='#aaaaaa',
            width=20,
            anchor='w'
        )
        label.pack(side=tk.LEFT)
        self._register_widget(label, {'bg': '#2d2d2d', 'fg': '#aaaaaa'}, {'bg': '#ffffff', 'fg': '#666666'})

        value_label = tk.Label(
            frame,
            text="---",
            font=('Helvetica', 11, 'bold'),
            bg='#2d2d2d',
            fg='#00ff00'
        )
        value_label.pack(side=tk.LEFT)
        self._register_widget(value_label, {'bg': '#2d2d2d', 'fg': '#00ff00'}, {'bg': '#ffffff', 'fg': '#007700'})

        return value_label

    def update_gui(self):
        """Update the GUI with current memory stats"""
        if not self.dashboard_open or not self.root:
            return
            
        try:
            mem = psutil.virtual_memory()
            
            # Update memory labels
            self.total_memory_label.config(text=f"{mem.total / (1024**3):.2f} GB")
            self.used_memory_label.config(text=f"{mem.used / (1024**3):.2f} GB")
            self.free_memory_label.config(text=f"{mem.free / (1024**3):.2f} GB")
            self.available_memory_label.config(text=f"{mem.available / (1024**3):.2f} GB")
            self.memory_percent_label.config(text=f"{mem.percent:.1f}%")
            
            # Color code memory percentage
            if mem.percent < 50:
                self.memory_percent_label.config(fg='#00ff00')
            elif mem.percent < 75:
                self.memory_percent_label.config(fg='#ffcc00')
            else:
                self.memory_percent_label.config(fg='#ff6b6b')
            
            # Update swap memory labels
            swap = psutil.swap_memory()
            self.swap_total_label.config(text=f"{swap.total / (1024**3):.2f} GB")
            self.swap_used_label.config(text=f"{swap.used / (1024**3):.2f} GB")
            if swap.total > 0:
                swap_pct = (swap.used / swap.total) * 100
                self.swap_percent_label.config(text=f"{swap_pct:.1f}%")
                if swap_pct < 10:
                    self.swap_percent_label.config(fg='#00ff00')
                elif swap_pct < 50:
                    self.swap_percent_label.config(fg='#ffcc00')
                else:
                    self.swap_percent_label.config(fg='#ff6b6b')
            else:
                self.swap_percent_label.config(text="N/A")
            
            # Update CPU usage (read from shared cache set by MenuBar timer)
            cpu_pct = self._cached_cpu_pct if hasattr(self, '_cached_cpu_pct') else 0
            self.cpu_percent_label.config(text=f"{cpu_pct:.1f}%")
            if cpu_pct < 50:
                self.cpu_percent_label.config(fg='#00ff00')
            elif cpu_pct < 80:
                self.cpu_percent_label.config(fg='#ffcc00')
            else:
                self.cpu_percent_label.config(fg='#ff6b6b')
            
            # Update system uptime
            boot_time = psutil.boot_time()
            uptime_seconds = datetime.now().timestamp() - boot_time
            days, rem = divmod(int(uptime_seconds), 86400)
            hours, rem = divmod(rem, 3600)
            minutes, seconds = divmod(rem, 60)
            self.uptime_label.config(text=f"{days}d {hours}h {minutes}m")
            self.boot_time_label.config(text=datetime.fromtimestamp(boot_time).strftime("%Y-%m-%d %H:%M"))
            
            # Update temperature (every 10 seconds to avoid expensive calls)
            if not hasattr(self, '_temp_counter'):
                self._temp_counter = 0
            self._temp_counter += 1
            if self._temp_counter % 10 == 0:
                threading.Thread(target=self._update_temperature, daemon=True).start()
            
            # Update network stats (skip first reading to avoid spike)
            if hasattr(self, '_prev_net'):
                net = psutil.net_io_counters()
                now = datetime.now().timestamp()
                elapsed = now - self._prev_net_time
                if elapsed > 0.5:
                    sent_delta = net.bytes_sent - self._prev_net.bytes_sent
                    recv_delta = net.bytes_recv - self._prev_net.bytes_recv
                    self._prev_net = net
                    self._prev_net_time = now
                    self.net_sent_label.config(text=self._format_bytes(sent_delta / elapsed) + "/s")
                    self.net_recv_label.config(text=self._format_bytes(recv_delta / elapsed) + "/s")
            
            # Update memory pressure indicator
            self.update_pressure_indicator(mem.percent)
            
            # Update graph
            self.memory_history.append(mem.percent)
            self.timestamps.append(datetime.now().strftime("%H:%M:%S"))
            self.update_graph()
            
            # Update top processes (every 5 seconds to avoid UI lag)
            if not hasattr(self, '_process_update_counter'):
                self._process_update_counter = 0
            self._process_update_counter += 1
            if self._process_update_counter % 5 == 0:
                threading.Thread(target=self.update_processes, daemon=True).start()
            
            # Check auto-optimization
            if self.auto_optimize.get() and mem.percent > self.auto_optimize_threshold:
                threading.Thread(target=self.auto_optimize_memory, daemon=True).start()
            
        except Exception as e:
            print(f"Error updating GUI: {e}")
        
        # Schedule next update
        if self.root:
            self.root.after(1000, self.update_gui)

    def update_pressure_indicator(self, percent):
        """Update the memory pressure indicator"""
        self.pressure_canvas.delete("all")
        
        width = self.pressure_canvas.winfo_width()
        if width < 100:
            width = 400
        
        # Draw background
        self.pressure_canvas.create_rectangle(0, 0, width, 30, fill='#1e1e1e', outline='')
        
        # Draw pressure bar
        if percent < 50:
            color = '#00ff00'
            status = "Normal"
            fg_color = '#00ff00'
        elif percent < 75:
            color = '#ffcc00'
            status = "Moderate"
            fg_color = '#ffcc00'
        else:
            color = '#ff6b6b'
            status = "High"
            fg_color = '#ff6b6b'
        
        bar_width = (percent / 100) * width
        self.pressure_canvas.create_rectangle(0, 0, bar_width, 30, fill=color, outline='')
        
        self.pressure_label.config(text=f"{status} ({percent:.1f}%)", fg=fg_color)

    def update_graph(self):
        """Update the memory usage graph"""
        if len(self.memory_history) < 2:
            return
        
        self.ax.clear()
        self.ax.plot(list(self.memory_history), color='#00ff00', linewidth=2)
        self.ax.fill_between(range(len(self.memory_history)), list(self.memory_history), alpha=0.3, color='#00ff00')
        self.ax.set_ylim(0, 100)
        self.ax.set_ylabel('Memory %', color='white')
        self.ax.set_facecolor('#1e1e1e')
        self.ax.tick_params(colors='white')
        self.ax.spines['bottom'].set_color('white')
        self.ax.spines['top'].set_color('white')
        self.ax.spines['left'].set_color('white')
        self.ax.spines['right'].set_color('white')
        self.ax.grid(True, alpha=0.3)
        
        if len(self.timestamps) > 0:
            self.ax.set_xticks(range(0, len(self.timestamps), 10))
            self.ax.set_xticklabels([self.timestamps[i] if i < len(self.timestamps) else '' for i in range(0, len(self.timestamps), 10)], rotation=45, color='white')
        
        self.canvas.draw()

    def update_processes(self):
        """Update the top processes treeview (runs in background thread)"""
        if not self.dashboard_open or not self.root:
            return
        
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'memory_percent', 'memory_info']):
            try:
                info = proc.info
                mem_mb = info['memory_info'].rss / (1024 * 1024)
                processes.append((
                    info['pid'],
                    info['name'] or 'Unknown',
                    info['memory_percent'] or 0.0,
                    mem_mb
                ))
            except (psutil.NoSuchProcess, psutil.AccessDenied, AttributeError):
                continue
        
        # Sort by memory usage (descending) and take top 15
        processes.sort(key=lambda x: x[3], reverse=True)
        top_processes = processes[:15]
        
        # Update treeview on the main thread
        def _update_tree():
            if not self.dashboard_open or not self.root:
                return
            for item in self.processes_tree.get_children():
                self.processes_tree.delete(item)
            for pid, name, mem_pct, mem_mb in top_processes:
                self.processes_tree.insert('', tk.END, values=(
                    pid,
                    name[:40] if len(name) > 40 else name,
                    f"{mem_pct:.1f}",
                    f"{mem_mb:.1f}"
                ))
        if self.root:
            self.root.after(0, _update_tree)

    def purge_memory(self):
        """Purge memory using sudo purge command"""
        self.status_label.config(text="Purging memory...")
        self.root.update()
        
        try:
            result = subprocess.run(
                ['sudo', 'purge'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                self.log_action("Memory Purged", "Success")
                messagebox.showinfo("Success", "Memory purged successfully!")
                self.status_label.config(text="Memory purged successfully")
            else:
                messagebox.showerror("Error", f"Failed to purge memory: {result.stderr}")
                self.status_label.config(text="Failed to purge memory")
        except subprocess.TimeoutExpired:
            messagebox.showerror("Error", "Purge command timed out")
            self.status_label.config(text="Purge command timed out")
        except Exception as e:
            messagebox.showerror("Error", f"Error purging memory: {str(e)}")
            self.status_label.config(text=f"Error: {str(e)}")

    @staticmethod
    def _format_bytes(b):
        """Format bytes per second to human-readable string"""
        if b >= 1024**3:
            return f"{b / (1024**3):.1f} GB"
        elif b >= 1024**2:
            return f"{b / (1024**2):.1f} MB"
        elif b >= 1024:
            return f"{b / 1024:.1f} KB"
        else:
            return f"{b:.0f} B"

    @staticmethod
    def _get_user_cache_path():
        """Return the absolute path to the user's Library/Caches directory"""
        return os.path.expanduser('~/Library/Caches')

    def _update_temperature(self):
        """Update CPU temperature from macOS sensors"""
        temp_c = None
        
        # Try psutil sensors first (no sudo needed)
        try:
            temps = psutil.sensors_temperatures()
            if temps:
                for entries in temps.values():
                    for entry in entries:
                        if entry.current > 0:
                            temp_c = entry.current
                            break
                    if temp_c:
                        break
        except Exception:
            pass
        
        if temp_c is not None and self.root and self.dashboard_open:
            self._set_temp_display(temp_c)

    def _set_temp_display(self, temp_c):
        """Update the temperature label with color coding"""
        def _set():
            if not self.dashboard_open or not self.root:
                return
            self.temp_label.config(text=f"{temp_c:.1f}°C")
            if temp_c < 60:
                self.temp_label.config(fg='#00ff00')
            elif temp_c < 80:
                self.temp_label.config(fg='#ffcc00')
            else:
                self.temp_label.config(fg='#ff6b6b')
        self.root.after(0, _set)

    def kill_selected_process(self):
        """Kill the selected process in the Treeview"""
        selected = self.processes_tree.selection()
        if not selected:
            return
        
        item = self.processes_tree.item(selected[0])
        values = item['values']
        if not values or len(values) < 2:
            return
        
        pid = values[0]
        name = values[1]
        
        confirm = messagebox.askyesno(
            "Kill Process",
            f"Are you sure you want to kill '{name}' (PID: {pid})?\n\nThis will force-terminate the process."
        )
        
        if not confirm:
            return
        
        try:
            proc = psutil.Process(pid)
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except psutil.TimeoutExpired:
                proc.kill()
                proc.wait(timeout=2)
            
            self.log_action("Killed Process", f"{name} (PID: {pid})")
            self.status_label.config(text=f"Killed {name} (PID: {pid})")
            messagebox.showinfo("Process Killed", f"Successfully killed '{name}' (PID: {pid})")
        except psutil.NoSuchProcess:
            messagebox.showwarning("Not Found", f"Process {pid} no longer exists.")
        except psutil.AccessDenied:
            messagebox.showerror("Access Denied", f"Permission denied to kill '{name}' (PID: {pid}).\nTry running with sudo.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to kill process: {str(e)}")

    def export_csv(self):
        """Export memory history to CSV file"""
        if len(self.memory_history) == 0:
            messagebox.showinfo("No Data", "No memory history data to export yet. Wait for data collection.")
            return
        
        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile=f"ram_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            title="Export Memory History"
        )
        
        if not filepath:
            return
        
        try:
            with open(filepath, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Timestamp', 'Memory Usage (%)'])
                
                timestamps = list(self.timestamps)
                memory_data = list(self.memory_history)
                
                for i in range(min(len(timestamps), len(memory_data))):
                    writer.writerow([timestamps[i], f"{memory_data[i]:.1f}"])
            
            self.status_label.config(text=f"Exported {min(len(timestamps), len(memory_data))} records to CSV")
            messagebox.showinfo("Export Complete", f"Memory history exported to:\n{filepath}")
            self.log_action("CSV Export", f"{min(len(timestamps), len(memory_data))} records")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export CSV: {str(e)}")
            self.status_label.config(text="CSV export failed")

    def clear_caches(self):
        """Clear system caches"""
        self.status_label.config(text="Clearing caches...")
        self.root.update()

        try:
            user_cache = RAMOptimizerDashboard._get_user_cache_path()
            commands = [
                'sudo rm -rf /Library/Caches/*',
                f'sudo rm -rf {user_cache}/*',
                'sudo rm -rf /System/Library/Caches/*'
            ]

            for cmd in commands:
                subprocess.run(cmd, shell=True, capture_output=True, timeout=30)

            messagebox.showinfo("Success", "Caches cleared successfully!")
            self.status_label.config(text="Caches cleared successfully")
            self.log_action("Caches Cleared", "Success")
        except Exception as e:
            messagebox.showerror("Error", f"Error clearing caches: {str(e)}")
            self.status_label.config(text=f"Error: {str(e)}")

    def full_optimization(self):
        """Run full optimization"""
        self.status_label.config(text="Running full optimization...")
        self.root.update()

        try:
            user_cache = RAMOptimizerDashboard._get_user_cache_path()
            commands = [
                f'sudo rm -rf {user_cache}/*',
                'sudo purge'
            ]

            for cmd in commands:
                subprocess.run(cmd, shell=True, capture_output=True, timeout=30)

            messagebox.showinfo("Success", "Full optimization completed!")
            self.status_label.config(text="Full optimization completed")
            self.log_action("Full Optimization", "Success")
        except Exception as e:
            messagebox.showerror("Error", f"Error during optimization: {str(e)}")
            self.status_label.config(text=f"Error: {str(e)}")

    def auto_optimize_memory(self):
        """Auto-optimize memory when threshold is exceeded"""
        try:
            subprocess.run(['sudo', 'purge'], capture_output=True, timeout=30)
            self.log_action("Auto-Optimization", "Purge executed")
            if self.status_label:
                self.status_label.config(text="Auto-optimization completed")
        except Exception as e:
            if self.status_label:
                self.status_label.config(text=f"Auto-optimization failed: {str(e)}")


class RAMOptimizerMenuBar(rumps.App):
    """Menu bar application for RAM Optimizer"""
    def __init__(self):
        super(RAMOptimizerMenuBar, self).__init__("RAM", quit_button=None)
        
        self.config_path = os.path.expanduser('~/.ram_optimizer_config.json')
        settings = self.load_settings()
        
        self.dashboard = RAMOptimizerDashboard()
        self.auto_optimize_enabled = settings.get('auto_optimize', False)
        self.auto_optimize_threshold = settings.get('auto_optimize_threshold', 85.0)
        
        # Alert settings
        self.alert_enabled = settings.get('alert_enabled', False)
        self.alert_threshold = settings.get('alert_threshold', 80.0)
        self.last_alert_time = 0
        self.alert_cooldown = 300  # 5 minutes between alerts
        
        # Battery-aware setting
        self.battery_aware = settings.get('battery_aware', True)
        
        # Scheduled optimization settings
        self.schedule_enabled = settings.get('schedule_enabled', False)
        self.schedule_interval_minutes = settings.get('schedule_interval', 30)
        self._last_scheduled_opt = 0
        
        # Create menu
        auto_label = f"Auto-Optimize: {'On' if self.auto_optimize_enabled else 'Off'}"
        self.menu = [
            rumps.MenuItem("Open Dashboard", callback=self.open_dashboard),
            rumps.separator,
            rumps.MenuItem("Quick Purge", callback=self.quick_purge),
            rumps.MenuItem("Clear Caches", callback=self.clear_caches),
            rumps.separator,
            rumps.MenuItem("View Logs", callback=self.view_logs_menu),
            rumps.separator,
            rumps.MenuItem("Schedule Opt: Off", callback=self.toggle_schedule),
            rumps.separator,
            rumps.MenuItem(auto_label, callback=self.toggle_auto_optimize),
            rumps.separator,
            rumps.MenuItem("Launch at Login", callback=self.toggle_startup),
            rumps.separator,
            rumps.MenuItem("Quit", callback=self.quit_app)
        ]

    @rumps.timer(1)
    def update_memory(self, sender):
        """Update memory display in menu bar"""
        try:
            mem = psutil.virtual_memory()
            cpu_pct = psutil.cpu_percent(interval=None)
            self.title = f"RAM {mem.percent:.0f}% | CPU {cpu_pct:.0f}%"
            # Cache CPU for dashboard to read
            self.dashboard._cached_cpu_pct = cpu_pct
            
            # Sync settings from dashboard (if dashboard GUI has been created)
            if hasattr(self.dashboard, 'alert_enabled'):
                self.alert_enabled = self.dashboard.alert_enabled.get()
                self.alert_threshold = self.dashboard.alert_threshold_var.get()
            if hasattr(self.dashboard, 'battery_aware'):
                self.battery_aware = self.dashboard.battery_aware.get()
            if hasattr(self.dashboard, 'auto_optimize'):
                self.auto_optimize_enabled = self.dashboard.auto_optimize.get()
                self.auto_optimize_threshold = self.dashboard.auto_optimize_threshold_var.get()
            
            # Auto-optimize if enabled (with battery check)
            if self.auto_optimize_enabled and mem.percent > self.auto_optimize_threshold:
                if not self._is_on_battery():
                    threading.Thread(target=self.auto_optimize_memory, daemon=True).start()
            
            # Memory alerts
            self.check_memory_alerts(mem.percent)
            
            # Scheduled optimization
            self.check_scheduled_optimization()
        except Exception as e:
            print(f"Error updating memory: {e}")

    def open_dashboard(self, sender):
        """Open the dashboard in a separate thread"""
        threading.Thread(target=self.dashboard.show_dashboard, daemon=True).start()

    def quick_purge(self, sender):
        """Quick memory purge"""
        threading.Thread(target=self._purge_memory, daemon=True).start()

    def _purge_memory(self):
        """Perform memory purge"""
        try:
            subprocess.run(['sudo', 'purge'], capture_output=True, timeout=30)
            rumps.notification(title="RAM Optimizer", subtitle="Success", message="Memory purged successfully")
        except Exception as e:
            rumps.notification(title="RAM Optimizer", subtitle="Error", message=f"Failed to purge memory: {str(e)}")

    def clear_caches(self, sender):
        """Clear system caches"""
        threading.Thread(target=self._clear_caches, daemon=True).start()

    def _clear_caches(self):
        """Clear cache files"""
        try:
            user_cache = RAMOptimizerDashboard._get_user_cache_path()
            commands = [
                f'sudo rm -rf {user_cache}/*',
                'sudo rm -rf /Library/Caches/*'
            ]

            for cmd in commands:
                subprocess.run(cmd, shell=True, capture_output=True, timeout=30)

            rumps.notification(title="RAM Optimizer", subtitle="Success", message="Caches cleared successfully")
        except Exception as e:
            rumps.notification(title="RAM Optimizer", subtitle="Error", message=f"Failed to clear caches: {str(e)}")

    def toggle_auto_optimize(self, sender):
        """Toggle auto-optimization"""
        self.auto_optimize_enabled = not self.auto_optimize_enabled
        sender.title = f"Auto-Optimize: {'On' if self.auto_optimize_enabled else 'Off'}"
        
        # Also update dashboard setting if dashboard has been opened
        if hasattr(self.dashboard, 'auto_optimize'):
            self.dashboard.auto_optimize.set(self.auto_optimize_enabled)
        
        self.save_settings()
        rumps.notification(
            title="RAM Optimizer", 
            subtitle="Auto-Optimization", 
            message=f"Auto-optimization {'enabled' if self.auto_optimize_enabled else 'disabled'}"
        )

    def load_settings(self):
        """Load settings from JSON config file"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    settings = json.load(f)
                return settings
        except (json.JSONDecodeError, IOError):
            pass
        return {}

    def save_settings(self):
        """Save settings to JSON config file"""
        dark_mode = self.dashboard.dark_mode.get() if hasattr(self.dashboard, 'dark_mode') else True
        settings = {
            'auto_optimize': self.auto_optimize_enabled,
            'auto_optimize_threshold': self.auto_optimize_threshold,
            'alert_enabled': self.alert_enabled,
            'alert_threshold': self.alert_threshold,
            'battery_aware': self.battery_aware,
            'schedule_enabled': self.schedule_enabled,
            'schedule_interval': self.schedule_interval_minutes,
            'dark_mode': dark_mode
        }
        try:
            with open(self.config_path, 'w') as f:
                json.dump(settings, f, indent=2)
        except IOError:
            pass

    def auto_optimize_memory(self):
        """Auto-optimize memory"""
        try:
            subprocess.run(['sudo', 'purge'], capture_output=True, timeout=30)
        except Exception as e:
            print(f"Auto-optimization error: {e}")

    def toggle_schedule(self, sender):
        """Toggle scheduled optimization"""
        self.schedule_enabled = not self.schedule_enabled
        sender.title = f"Schedule Opt: {'On' if self.schedule_enabled else 'Off'}"
        self.save_settings()
        rumps.notification(
            title="RAM Optimizer",
            subtitle="Scheduled Optimization",
            message=f"Scheduled optimization {'enabled' if self.schedule_enabled else 'disabled'} (every {self.schedule_interval_minutes} min)"
        )

    def check_scheduled_optimization(self):
        """Run optimization on schedule"""
        if not self.schedule_enabled:
            return
        now = datetime.now().timestamp()
        if now - self._last_scheduled_opt < self.schedule_interval_minutes * 60:
            return
        self._last_scheduled_opt = now
        threading.Thread(target=self._run_scheduled_opt, daemon=True).start()

    def _run_scheduled_opt(self):
        """Execute scheduled optimization"""
        try:
            subprocess.run(['sudo', 'purge'], capture_output=True, timeout=30)
            RAMOptimizerDashboard.log_action("Scheduled Optimization", f"Every {self.schedule_interval_minutes}min")
        except Exception:
            pass

    def quit_app(self, sender):
        """Quit the application"""
        rumps.quit_application()

    def view_logs_menu(self, sender):
        """View optimization logs from the menu bar"""
        def _run_log_viewer():
            temp_root = tk.Tk()
            temp_root.withdraw()
            RAMOptimizerDashboard.view_logs(temp_root)
            temp_root.mainloop()
        threading.Thread(target=_run_log_viewer, daemon=True).start()

    def _is_on_battery(self):
        """Check if the system is running on battery power"""
        if not self.battery_aware:
            return False
        try:
            battery = psutil.sensors_battery()
            if battery is None:
                return False  # Desktop Macs don't have battery info
            return not battery.power_plugged
        except Exception:
            return False

    def check_memory_alerts(self, mem_percent):
        """Check and send memory alerts with cooldown"""
        if not self.alert_enabled:
            return
        if mem_percent < self.alert_threshold:
            return
        
        now = datetime.now().timestamp()
        if now - self.last_alert_time < self.alert_cooldown:
            return
        
        self.last_alert_time = now
        threading.Thread(target=self._send_alert, args=(mem_percent,), daemon=True).start()

    def toggle_startup(self, sender):
        """Toggle launch at login"""
        plist_path = os.path.expanduser('~/Library/LaunchAgents/com.ramoptimizer.plist')
        
        if os.path.exists(plist_path):
            os.remove(plist_path)
            rumps.notification(
                title="RAM Optimizer",
                subtitle="Startup Launch",
                message="Removed from login items."
            )
        else:
            import sys
            app_path = os.path.abspath(sys.argv[0])
            try:
                python_path = subprocess.check_output(['which', 'python3'], text=True).strip()
            except (subprocess.CalledProcessError, FileNotFoundError):
                python_path = sys.executable
            
            plist_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.ramoptimizer</string>
    <key>ProgramArguments</key>
    <array>
        <string>{python_path}</string>
        <string>{app_path}</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <false/>
</dict>
</plist>'''
            try:
                os.makedirs(os.path.dirname(plist_path), exist_ok=True)
                with open(plist_path, 'w') as f:
                    f.write(plist_content)
                rumps.notification(
                    title="RAM Optimizer",
                    subtitle="Startup Launch",
                    message="Added to login items. Will launch at startup."
                )
            except Exception as e:
                rumps.notification(
                    title="RAM Optimizer",
                    subtitle="Error",
                    message=f"Failed to create launch agent: {str(e)}"
                )

    def _send_alert(self, mem_percent):
        """Send a macOS notification for high memory usage"""
        rumps.notification(
            title="⚠️ RAM Optimizer Alert",
            subtitle=f"High Memory Usage: {mem_percent:.1f}%",
            message="Memory usage exceeds your alert threshold. Consider optimizing."
        )


if __name__ == "__main__":
    app = RAMOptimizerMenuBar()
    app.run()
