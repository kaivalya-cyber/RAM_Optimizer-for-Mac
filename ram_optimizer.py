#!/usr/bin/env python3
"""
Real-Time RAM Optimizer for Mac
Monitors memory usage and provides optimization features
"""

import tkinter as tk
from tkinter import ttk, messagebox
import psutil
import subprocess
import threading
import time
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import deque


class RAMOptimizer:
    def __init__(self, root):
        self.root = root
        self.root.title("RAM Optimizer for Mac")
        self.root.geometry("900x700")
        self.root.configure(bg='#1e1e1e')
        
        # Data storage for graphs
        self.memory_history = deque(maxlen=60)
        self.timestamps = deque(maxlen=60)
        
        # Auto-optimization settings
        self.auto_optimize = tk.BooleanVar(value=False)
        self.auto_optimize_threshold = tk.DoubleVar(value=85.0)
        
        # Monitoring flag
        self.monitoring = True
        
        # Create GUI
        self.create_gui()
        
        # Start monitoring thread
        self.monitor_thread = threading.Thread(target=self.monitor_memory, daemon=True)
        self.monitor_thread.start()
        
        # Start GUI update
        self.update_gui()

    def create_gui(self):
        """Create the main GUI interface"""
        # Title
        title_label = tk.Label(
            self.root, 
            text="🚀 RAM Optimizer for Mac", 
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
            activeforeground='white'
        )
        auto_check.pack(side=tk.LEFT, padx=5)
        
        threshold_scale = tk.Scale(
            auto_frame, 
            from_=50, 
            to=95, 
            orient=tk.HORIZONTAL,
            variable=self.auto_optimize_threshold,
            font=('Helvetica', 10),
            bg='#2d2d2d', 
            fg='white',
            highlightthickness=0,
            troughcolor='#4a4a4a',
            activebackground='#45b7d1'
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

    def monitor_memory(self):
        """Monitor memory usage in real-time"""
        while self.monitoring:
            try:
                # Get memory info
                mem = psutil.virtual_memory()
                
                # Store data for graph
                self.memory_history.append(mem.percent)
                self.timestamps.append(datetime.now().strftime("%H:%M:%S"))
                
                # Check auto-optimization
                if self.auto_optimize.get() and mem.percent > self.auto_optimize_threshold.get():
                    self.root.after(0, self.auto_optimize_memory)
                
                time.sleep(1)
            except Exception as e:
                print(f"Error monitoring memory: {e}")
                time.sleep(5)

    def update_gui(self):
        """Update the GUI with current memory stats"""
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
            
            # Update memory pressure indicator
            self.update_pressure_indicator(mem.percent)
            
            # Update graph
            self.update_graph()
            
        except Exception as e:
            print(f"Error updating GUI: {e}")
        
        # Schedule next update
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

    def purge_memory(self):
        """Purge memory using sudo purge command"""
        self.status_label.config(text="Purging memory...")
        self.root.update()
        
        try:
            # Run purge command
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
            # Clear caches first
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
        self.status_label.config(text="Auto-optimizing...")
        try:
            subprocess.run(['sudo', 'purge'], capture_output=True, timeout=30)
            self.status_label.config(text="Auto-optimization completed")
        except Exception as e:
            self.status_label.config(text=f"Auto-optimization failed: {str(e)}")

    def on_closing(self):
        """Handle window closing"""
        self.monitoring = False
        self.root.destroy()


def main():
    root = tk.Tk()
    app = RAMOptimizer(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()
