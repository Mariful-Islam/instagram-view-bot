from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import time
import random
import schedule
from dotenv import load_dotenv
import os


load_dotenv()

# ========== CONFIG ==========
IG_USERNAME = os.getenv('IG_USERNAME')
IG_PASSWORD = os.getenv('IG_PASSWORD')

TARGET_USERNAME = os.getenv('TARGET_USERNAME')
CHECK_INTERVAL = 300  # seconds between checks
MIN_VIEWS = 10000
MAX_VIEWS = 20000
VIEW_DURATION_MINUTES = 60
# ============================

# Simulate view injection (placeholder)
def send_views(reel_url, num_views):
    print(f"[VIEWS] Simulated sending {num_views} views to {reel_url}")
    time.sleep(random.uniform(0.5, 1.5))  # simulate delay

# Schedule view delivery
def schedule_views(reel_url, total_views, duration_minutes):
    intervals = (duration_minutes * 60) // 10
    views_sent = 0

    def deliver_batch():
        nonlocal views_sent
        if views_sent >= total_views:
            print("[COMPLETE] View delivery finished.")
            return schedule.CancelJob
        batch = random.randint(200, 500)
        views_to_send = min(batch, total_views - views_sent)
        send_views(reel_url, views_to_send)
        views_sent += views_to_send
        print(f"[INFO] Sent {views_sent}/{total_views} views.")

    for _ in range(intervals):
        schedule.every(10).seconds.do(deliver_batch)

# Login to Instagram
def instagram_login(driver):
    driver.get("https://www.instagram.com/accounts/login/")
    time.sleep(5)

    username_input = driver.find_element(By.NAME, "username")
    password_input = driver.find_element(By.NAME, "password")

    username_input.send_keys(IG_USERNAME)
    password_input.send_keys(IG_PASSWORD)
    password_input.send_keys(Keys.RETURN)

    time.sleep(10)

# Get latest Reel URL
def get_latest_reel(driver, username):
    driver.get(f"https://www.instagram.com/{username}/reels/")
    time.sleep(5)

    reels = driver.find_elements(By.XPATH, "//a[contains(@href, '/reel/')]")
    if not reels:
        print("[INFO] No reels found.")
        return None
    latest_reel_href = reels[0].get_attribute("href")
    return latest_reel_href

# Main monitor loop
def monitor_reels():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-notifications")
    driver = webdriver.Chrome(options=options)

    try:
        instagram_login(driver)
        last_seen_reel = None

        while True:
            try:
                current_reel = get_latest_reel(driver, TARGET_USERNAME)
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


if __name__ == "__main__":
    monitor_reels()
