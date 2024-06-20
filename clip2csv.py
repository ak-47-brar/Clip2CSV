import tkinter as tk
from tkinter import messagebox
import csv
import pyperclip
import os
import time
import logging
from plyer import notification

# Setup logging
logging.basicConfig(filename='clip2csv.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Global variables
last_saved_url = ""
CSV_FILE_PATH = 'links.csv'
CHECK_INTERVAL = 1  # in seconds

# Function to save link
def save_link(url):
    global last_saved_url
    try:
        if not url_already_saved(url):
            with open(CSV_FILE_PATH, 'a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                last_saved_title = get_last_saved_title()
                next_title = str(int(last_saved_title) + 1) if last_saved_title.isdigit() else '1'
                writer.writerow([next_title, url])
                last_saved_url = url  # Update last_saved_url
            logging.info(f"Link saved successfully with title '{next_title}': {url}")
            notification.notify(
                title='Link Saved',
                message=f"Link saved successfully with title '{next_title}'",
                timeout=5
            )
        else:
            logging.info(f"Duplicate URL not saved: {url}")
    except Exception as e:
        logging.error(f"Failed to save link: {str(e)}")
        messagebox.showerror("Error", f"Failed to save link: {str(e)}")

# Function to get the last saved title from CSV
def get_last_saved_title():
    try:
        if os.path.exists(CSV_FILE_PATH):
            with open(CSV_FILE_PATH, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                last_row = None
                for row in reader:
                    last_row = row
                if last_row:
                    return last_row[0]
        return '0'
    except FileNotFoundError:
        return '0'

# Function to check if URL is already saved
def url_already_saved(url):
    try:
        if os.path.exists(CSV_FILE_PATH):
            with open(CSV_FILE_PATH, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                for row in reader:
                    if row[1] == url:
                        return True
        return False
    except Exception as e:
        logging.error(f"Error checking for duplicate URL: {str(e)}")
        return False

# Function to monitor clipboard for changes
def monitor_clipboard(status_label):
    global last_saved_url
    while True:
        try:
            clipboard_content = pyperclip.paste().strip()
            if clipboard_content.startswith('http') and clipboard_content != last_saved_url:
                save_link(clipboard_content)
                status_label.config(text=f"Last URL saved: {clipboard_content}")
        except pyperclip.PyperclipException as e:
            logging.error(f"Clipboard access error: {e}")
        time.sleep(CHECK_INTERVAL)  # Add a delay to reduce the likelihood of clipboard conflicts

# Main function to start monitoring clipboard
def main():
    # Setup the GUI
    root = tk.Tk()
    root.title("Clip2CSV")
    
    status_label = tk.Label(root, text="Monitoring clipboard for URLs...")
    status_label.pack(pady=10)
    
    exit_button = tk.Button(root, text="Exit", command=root.quit)
    exit_button.pack(pady=5)
    
    # Start monitoring clipboard in a separate thread
    import threading
    clipboard_thread = threading.Thread(target=monitor_clipboard, args=(status_label,))
    clipboard_thread.daemon = True
    clipboard_thread.start()
    
    # Run tkinter main loop
    root.mainloop()

if __name__ == "__main__":
    main()
