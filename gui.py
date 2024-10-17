import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import threading
from queue import Queue, Empty
from main import main

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
            if message[0] == 'progress':
                _, step, total_steps = message
                progress_bar['value'] = (step / total_steps) * 100
                status_label.config(text=f"Scanning... {step}/{total_steps}")
            elif message[0] == 'complete':
                _, total_steps = message
                messagebox.showinfo("Info", f"Scanned Cards: {total_steps}")
                status_label.config(text="Scanning completed.")
                progress_bar.stop()
                break
    except Empty:
        root.after(100, check_queue, queue)

root = tk.Tk()
root.title("Magic Card Scanner")

start_button = tk.Button(root, text="Start Scanning", command=start_scanning)
start_button.pack(pady=10)

stop_button = tk.Button(root, text="Stop Scanning", command=stop_scanning)
stop_button.pack(pady=10)

status_label = tk.Label(root, text="Status: Idle")
status_label.pack(pady=10)

progress_bar = ttk.Progressbar(root, mode='determinate', maximum=100)
progress_bar.pack(pady=10)

root.mainloop()