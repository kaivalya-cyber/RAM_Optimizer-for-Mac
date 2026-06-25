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
from tkinter import messagebox
from datetime import datetime
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

    def create_stat_label(self, parent, text, row):
        """Create a statistic label"""
        frame = tk.Frame(parent, bg='#2d2d2d')
        frame.pack(fill=tk.X, padx=10, pady=5)
        
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
        
        value_label = tk.Label(
            frame, 
            text="---", 
            font=('Helvetica', 11, 'bold'),
            bg='#2d2d2d', 
            fg='#00ff00'
        )
        value_label.pack(side=tk.LEFT)
        
        return value_label

    def update_threshold(self):
        """Update the auto-optimization threshold"""
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
            'battery_aware': self.battery_aware.get() if hasattr(self, 'battery_aware') else True
        }
        try:
            with open(self.config_path, 'w') as f:
                json.dump(settings, f, indent=2)
        except IOError:
            pass

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
            
            # Update CPU usage
            cpu_pct = psutil.cpu_percent(interval=None)
            self.cpu_percent_label.config(text=f"{cpu_pct:.1f}%")
            if cpu_pct < 50:
                self.cpu_percent_label.config(fg='#00ff00')
            elif cpu_pct < 80:
                self.cpu_percent_label.config(fg='#ffcc00')
            else:
                self.cpu_percent_label.config(fg='#ff6b6b')
            
            # Update memory pressure indicator
            self.update_pressure_indicator(mem.percent)
            
            # Update graph
            self.memory_history.append(mem.percent)
            self.timestamps.append(datetime.now().strftime("%H:%M:%S"))
            self.update_graph()
            
            # Update top processes
            self.update_processes()
            
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
        """Update the top processes treeview"""
        # Clear existing items
        for item in self.processes_tree.get_children():
            self.processes_tree.delete(item)
        
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
        
        # Insert into treeview
        for pid, name, mem_pct, mem_mb in top_processes:
            self.processes_tree.insert('', tk.END, values=(
                pid,
                name[:40] if len(name) > 40 else name,
                f"{mem_pct:.1f}",
                f"{mem_mb:.1f}"
            ))

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

    def clear_caches(self):
        """Clear system caches"""
        self.status_label.config(text="Clearing caches...")
        self.root.update()
        
        try:
            commands = [
                'sudo rm -rf /Library/Caches/*',
                'sudo rm -rf ~/Library/Caches/*',
                'sudo rm -rf /System/Library/Caches/*'
            ]
            
            for cmd in commands:
                subprocess.run(cmd, shell=True, capture_output=True, timeout=30)
            
            messagebox.showinfo("Success", "Caches cleared successfully!")
            self.status_label.config(text="Caches cleared successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Error clearing caches: {str(e)}")
            self.status_label.config(text=f"Error: {str(e)}")

    def full_optimization(self):
        """Run full optimization"""
        self.status_label.config(text="Running full optimization...")
        self.root.update()
        
        try:
            commands = [
                'sudo rm -rf ~/Library/Caches/*',
                'sudo purge'
            ]
            
            for cmd in commands:
                subprocess.run(cmd, shell=True, capture_output=True, timeout=30)
            
            messagebox.showinfo("Success", "Full optimization completed!")
            self.status_label.config(text="Full optimization completed")
        except Exception as e:
            messagebox.showerror("Error", f"Error during optimization: {str(e)}")
            self.status_label.config(text=f"Error: {str(e)}")

    def auto_optimize_memory(self):
        """Auto-optimize memory when threshold is exceeded"""
        try:
            subprocess.run(['sudo', 'purge'], capture_output=True, timeout=30)
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
        
        # Create menu
        auto_label = f"Auto-Optimize: {'On' if self.auto_optimize_enabled else 'Off'}"
        self.menu = [
            rumps.MenuItem("Open Dashboard", callback=self.open_dashboard),
            rumps.separator,
            rumps.MenuItem("Quick Purge", callback=self.quick_purge),
            rumps.MenuItem("Clear Caches", callback=self.clear_caches),
            rumps.separator,
            rumps.MenuItem(auto_label, callback=self.toggle_auto_optimize),
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
            
            # Auto-optimize if enabled (with battery check)
            if self.auto_optimize_enabled and mem.percent > self.auto_optimize_threshold:
                if not self._is_on_battery():
                    threading.Thread(target=self.auto_optimize_memory, daemon=True).start()
            
            # Memory alerts
            self.check_memory_alerts(mem.percent)
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
            commands = [
                'sudo rm -rf ~/Library/Caches/*',
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
        
        # Also update dashboard setting
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
        settings = {
            'auto_optimize': self.auto_optimize_enabled,
            'auto_optimize_threshold': self.auto_optimize_threshold,
            'alert_enabled': self.alert_enabled,
            'alert_threshold': self.alert_threshold,
            'battery_aware': self.battery_aware
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

    def quit_app(self, sender):
        """Quit the application"""
        rumps.quit_application()

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
