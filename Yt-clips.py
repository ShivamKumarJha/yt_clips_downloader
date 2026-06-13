from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import csv

# Setup Chrome
options = webdriver.ChromeOptions()

# IMPORTANT:
# Use a separate Selenium Chrome profile
options.add_argument(
    r"--user-data-dir=C:\Users\Shivam\AppData\Local\Google\Chrome\SeleniumProfile"
)

options.add_argument("--profile-directory=Default")

# Prevent DevToolsActivePort crash
options.add_argument("--remote-debugging-port=9222")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)

# Open YouTube clips page
driver.get("https://www.youtube.com/feed/clips")

print("Please log in if needed...")
time.sleep(10)

# Scroll until all clips are loaded
last_height = driver.execute_script("return document.documentElement.scrollHeight")

while True:
    driver.execute_script(
        "window.scrollTo(0, document.documentElement.scrollHeight);"
    )

    time.sleep(3)

    new_height = driver.execute_script(
        "return document.documentElement.scrollHeight"
    )

    if new_height == last_height:
        break

    last_height = new_height

print("Finished loading clips")

# Find clip elements
clips = driver.find_elements(By.TAG_NAME, "ytd-rich-grid-media")

results = []

for clip in clips:
    try:
        link = clip.find_element(By.ID, "video-title-link")
        title = link.get_attribute("title")
        url = link.get_attribute("href")

        if url and "/clip/" in url:
            results.append([title, url])

    except Exception:
        pass

# Remove duplicates
unique_results = []
seen = set()

for title, url in results:
    if url not in seen:
        seen.add(url)
        unique_results.append([title, url])

# Save to CSV
with open("youtube_clips.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Title", "URL"])
    writer.writerows(unique_results)

print(f"Saved {len(unique_results)} clips to youtube_clips.csv")

driver.quit()