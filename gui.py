import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import threading
from queue import Queue, Empty
from main import main
import sys

# Class to redirect console output to a text widget in the GUI
class ConsoleRedirector:
    def __init__(self, text_widget):
        self.text_widget = text_widget

    # Method to write messages to the text widget
    def write(self, message):
        self.text_widget.insert(tk.END, message)  # Insert message at the end of the text widget
        self.text_widget.see(tk.END)  # Scroll to the end of the text widget to show the latest message

    def flush(self):
        pass  # This method is required to handle the flush command, but it does nothing here

# Function to start the scanning process
def start_scanning():
    status_label.config(text="Scanning started...")  # Update the status label to indicate scanning has started
    status_queue = Queue()  # Create a queue to hold status messages
    global scanning_thread
    scanning_thread = threading.Thread(target=main, args=(status_queue,))  # Create a new thread to run the main scanning function
    scanning_thread.start()  # Start the scanning thread
    check_queue(status_queue)  # Start checking the queue for status updates

# Function to stop the scanning process
def stop_scanning():
    if scanning_thread.is_alive():  # Check if the scanning thread is still running
        status_label.config(text="Scanning stopped.")  # Update the status label to indicate scanning has stopped
        # Implement a way to stop the scanning process in main.py if needed

# Function to check the queue for status updates
def check_queue(queue):
    try:
        while True:
            message = queue.get_nowait()  # Get the next message from the queue
            if isinstance(message, (list, tuple)) and message[0] == 'progress':
                _, step, total_steps = message
                progress_bar['value'] = (step / total_steps) * 100  # Update the progress bar
                status_label.config(text=f"Scanning... {step}/{total_steps}")  # Update the status label with the current progress
            elif isinstance(message, (list, tuple)) and message[0] == 'complete':
                _, total_steps = message
                messagebox.showinfo("Info", f"Scanned Cards: {total_steps}")  # Show a message box with the total number of scanned cards
                status_label.config(text="Scanning completed.")  # Update the status label to indicate scanning is complete
                progress_bar.stop()  # Stop the progress bar
                break
    except Empty:
        root.after(100, check_queue, queue)  # Check the queue again after 100 milliseconds if it is empty

# Create the main application window
root = tk.Tk()
root.title("Magic Card Scanner")  # Set the title of the window

# Increase window size by 20%
window_width = int(root.winfo_screenwidth() * 0.24)
window_height = int(root.winfo_screenheight() * 0.24)
root.geometry(f"{window_width}x{window_height}")

# Increase font size by 20%
font_size = 12 * 1.2

# Create and pack the Start Scanning button
start_button = tk.Button(root, text="Start Scanning", command=start_scanning, font=("TkDefaultFont", int(font_size)))
start_button.pack(pady=12)

# Create and pack the Stop Scanning button
stop_button = tk.Button(root, text="Stop Scanning", command=stop_scanning, font=("TkDefaultFont", int(font_size)))
stop_button.pack(pady=12)

# Create and pack the status label
status_label = tk.Label(root, text="Status: Idle", font=("TkDefaultFont", int(font_size)))
status_label.pack(pady=12)

# Create and pack the progress bar
progress_bar = ttk.Progressbar(root, mode='determinate', maximum=100)
progress_bar.pack(pady=12, padx=20)

# Add a text widget to display console output
console_output = tk.Text(root, height=10, wrap='word')
console_output.pack(pady=12, padx=20)

# Redirect standard output to the text widget
sys.stdout = ConsoleRedirector(console_output)

# Start the Tkinter event loop
root.mainloop()