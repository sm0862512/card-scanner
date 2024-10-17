import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import threading
from queue import Queue, Empty
from main import main
import sys

class ConsoleRedirector:
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, message):
        self.text_widget.insert(tk.END, message)
        self.text_widget.see(tk.END)

    def flush(self):
        pass

def start_scanning():
    status_label.config(text="Scanning started...")
    status_queue = Queue()
    global scanning_thread
    scanning_thread = threading.Thread(target=main, args=(status_queue,))
    scanning_thread.start()
    check_queue(status_queue)

def stop_scanning():
    if scanning_thread.is_alive():
        status_label.config(text="Scanning stopped.")
        # Implement a way to stop the scanning process in main.py if needed

def check_queue(queue):
    try:
        while True:
            message = queue.get_nowait()
            if isinstance(message, (list, tuple)) and message[0] == 'progress':
                _, step, total_steps = message
                progress_bar['value'] = (step / total_steps) * 100
                status_label.config(text=f"Scanning... {step}/{total_steps}")
            elif isinstance(message, (list, tuple)) and message[0] == 'complete':
                _, total_steps = message
                messagebox.showinfo("Info", f"Scanned Cards: {total_steps}")
                status_label.config(text="Scanning completed.")
                progress_bar.stop()
                break
    except Empty:
        root.after(100, check_queue, queue)

root = tk.Tk()
root.title("Magic Card Scanner")

# Increase window size by 20%
window_width = int(root.winfo_screenwidth() * 0.24)
window_height = int(root.winfo_screenheight() * 0.24)
root.geometry(f"{window_width}x{window_height}")

# Increase font size by 20%
font_size = 12 * 1.2

start_button = tk.Button(root, text="Start Scanning", command=start_scanning, font=("TkDefaultFont", int(font_size)))
start_button.pack(pady=12)

stop_button = tk.Button(root, text="Stop Scanning", command=stop_scanning, font=("TkDefaultFont", int(font_size)))
stop_button.pack(pady=12)

status_label = tk.Label(root, text="Status: Idle", font=("TkDefaultFont", int(font_size)))
status_label.pack(pady=12)

progress_bar = ttk.Progressbar(root, mode='determinate', maximum=100)
progress_bar.pack(pady=12, padx=20)

# Add a text widget to display console output
console_output = tk.Text(root, height=10, wrap='word')
console_output.pack(pady=12, padx=20)

# Redirect standard output to the text widget
sys.stdout = ConsoleRedirector(console_output)

root.mainloop()