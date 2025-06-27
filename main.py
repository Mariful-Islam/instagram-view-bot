import tkinter as tk
from tkinter import messagebox, scrolledtext
import threading
import time
import random
import schedule
import sys

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys

# --- Configuration ---
CHECK_INTERVAL = 300  # seconds
MIN_VIEWS = 10000
MAX_VIEWS = 20000
VIEW_DURATION_MINUTES = 60

monitoring = False
monitor_thread = None

# --- Redirect stdout to Text widget ---
class RedirectOutput:
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, message):
        self.text_widget.configure(state='normal')
        self.text_widget.insert(tk.END, message)
        self.text_widget.see(tk.END)
        self.text_widget.configure(state='disabled')

    def flush(self):
        pass  # Required for file-like object

# --- Simulate View Injection ---
def send_views(reel_url, num_views):
    print(f"[VIEWS] Simulated sending {num_views} views to {reel_url}")
    time.sleep(random.uniform(0.5, 1.5))

# --- Schedule View Delivery ---
def schedule_views(reel_url, total_views, duration_minutes):
    intervals = (duration_minutes * 60) // 10
    views_sent = 0

    def deliver_batch():
        nonlocal views_sent
        if views_sent >= total_views or not monitoring:
            print("[COMPLETE] View delivery finished or stopped.")
            return schedule.CancelJob
        batch = random.randint(200, 500)
        views_to_send = min(batch, total_views - views_sent)
        send_views(reel_url, views_to_send)
        views_sent += views_to_send
        print(f"[INFO] Sent {views_sent}/{total_views} views.")

    for _ in range(intervals):
        schedule.every(10).seconds.do(deliver_batch)

# --- Instagram Login ---
def instagram_login(driver, ig_user, ig_pass):
    driver.get("https://www.instagram.com/accounts/login/")
    time.sleep(5)

    username_input = driver.find_element(By.NAME, "username")
    password_input = driver.find_element(By.NAME, "password")

    username_input.send_keys(ig_user)
    password_input.send_keys(ig_pass)
    password_input.send_keys(Keys.RETURN)

    time.sleep(10)

# --- Get Latest Reel ---
def get_latest_reel(driver, username):
    driver.get(f"https://www.instagram.com/{username}/reels/")
    time.sleep(5)

    reels = driver.find_elements(By.XPATH, "//a[contains(@href, '/reel/')]")
    if not reels:
        print("[INFO] No reels found.")
        return None
    return reels[0].get_attribute("href")

# --- Monitoring Bot Logic ---
def monitor_reels(username, ig_user, ig_pass):
    global monitoring
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-notifications")
    driver = webdriver.Chrome(options=options)

    try:
        instagram_login(driver, ig_user, ig_pass)
        last_seen_reel = None

        while monitoring:
            try:
                current_reel = get_latest_reel(driver, username)
                if current_reel and current_reel != last_seen_reel:
                    print(f"[DETECTED] New Reel: {current_reel}")
                    last_seen_reel = current_reel
                    total_views = random.randint(MIN_VIEWS, MAX_VIEWS)
                    schedule_views(current_reel, total_views, VIEW_DURATION_MINUTES)

                schedule.run_pending()
                time.sleep(CHECK_INTERVAL)

            except Exception as e:
                print(f"[ERROR] {e}")
                time.sleep(60)
    finally:
        driver.quit()
        print("[EXIT] Monitoring stopped.")

# --- Thread Runner ---
def start_monitoring(username, ig_user, ig_pass):
    global monitoring
    monitoring = True
    monitor_reels(username, ig_user, ig_pass)

# --- Toggle Start/Stop ---
def toggle_monitoring():
    global monitoring, monitor_thread

    if not monitoring:
        target = username_entry.get().strip()
        ig_user = login_username_entry.get().strip()
        ig_pass = login_password_entry.get().strip()

        if not target or not ig_user or not ig_pass:
            messagebox.showerror("Error", "Please fill in all fields.")
            return

        status_label.config(text="Status: Running", fg="green")
        start_button.config(text="Stop", bg="red")
        monitor_thread = threading.Thread(
            target=start_monitoring, args=(target, ig_user, ig_pass), daemon=True
        )
        monitor_thread.start()
    else:
        monitoring = False
        start_button.config(text="Start", bg="green")
        status_label.config(text="Status: Stopped", fg="red")

# --- Tkinter GUI ---
root = tk.Tk()
root.title("Instagram Reel View Bot")
root.geometry("600x500")

tk.Label(root, text="Target Instagram Username:").pack(pady=5)
username_entry = tk.Entry(root, width=40)
username_entry.pack()

tk.Label(root, text="Instagram Login Username:").pack(pady=5)
login_username_entry = tk.Entry(root, width=40)
login_username_entry.pack()

tk.Label(root, text="Instagram Login Password:").pack(pady=5)
login_password_entry = tk.Entry(root, width=40, show='*')
login_password_entry.pack()

start_button = tk.Button(root, text="Start", bg="green", fg="white", width=15, command=toggle_monitoring)
start_button.pack(pady=10)

status_label = tk.Label(root, text="Status: Stopped", fg="red")
status_label.pack()

# --- Console Output Area ---
console_output = scrolledtext.ScrolledText(root, height=12, state='disabled', wrap='word', bg='black', fg='white')
console_output.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

# Redirect stdout
sys.stdout = RedirectOutput(console_output)

root.mainloop()
