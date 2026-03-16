import os
import subprocess
import time
import requests
import json
from playwright.sync_api import sync_playwright

cag_dir = r"f:\learnbydoingwithsteven\cag_10"
app_name = "app_04_support_agent"

# Run npm install if needed
front_dir = os.path.join(cag_dir, app_name, "frontend")
if not os.path.exists(os.path.join(front_dir, "node_modules")):
    print(f"Installing npm in {front_dir}...")
    subprocess.run(["npm", "install"], cwd=front_dir, shell=True)

# Start backend
back_dir = os.path.join(cag_dir, app_name, "backend")
print("Starting backend...")
back_proc = subprocess.Popen(["py", "main.py"], cwd=back_dir, creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)

# Start frontend
print("Starting frontend...")
front_proc = subprocess.Popen(["npm", "start"], cwd=front_dir, env={**os.environ, "PORT": "3004", "BROWSER": "none"}, shell=True, creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)

time.sleep(10)
try:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 900})
        page.goto("http://localhost:3004")
        
        # Wait for the app to load
        page.wait_for_timeout(2000)
        
        # Type into the textarea (MUI textarea)
        input_el = page.locator("textarea[placeholder*='Type your question']").first
        if input_el.count() == 0:
            # Fallback
            input_el = page.locator("textarea").first
        
        input_el.fill("I can't login to my account, I forgot my password")
        
        # Click submit
        page.locator("button:has-text('Submit')").first.click()
        
        # Wait for processing
        page.wait_for_timeout(4000)
        
        # Take screenshot
        screenshot_path = os.path.join(cag_dir, app_name, f"{app_name}_screenshot.png")
        page.screenshot(path=screenshot_path, full_page=True)
        print(f"Screenshot saved to {screenshot_path}")
        
        browser.close()
except Exception as e:
    print(f"Error: {e}")
finally:
    back_proc.terminate()
    front_proc.terminate()
    try:
        back_proc.wait(5)
        front_proc.wait(5)
    except:
        back_proc.kill()
        front_proc.kill()
