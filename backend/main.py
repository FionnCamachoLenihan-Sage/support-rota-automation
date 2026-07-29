from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import os
import time
import json
import sys
from datetime import datetime
from constants import ( PROFILE_DIR, SCREENSHOTS_DIR, CSV_LOGS_DIR)

type LogErrors = dict[str, dict[str, str | int]]

from utils.navigation import change_time_range

def screenshot(driver: WebDriver, id: str):
  time.sleep(5)
  os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
  timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
  screenshot_path = os.path.join(SCREENSHOTS_DIR, f"{id}_{timestamp}.png")
  driver.save_screenshot(screenshot_path) # type: ignore

def getGrafanaSessionCookie(driver: WebDriver):
  cookies: list[dict[str, str]] = driver.get_cookies() # type: ignore
  for cookie in cookies:
    if cookie["name"] == "grafana_session":
      return cookie["value"]
  return None

def main():
  if len(sys.argv) != 4:
    print("Usage: python main.py <target_url> <time_range> <id>")
    return
  
  target_url = sys.argv[1]
  time_range = sys.argv[2]
  id = sys.argv[3]
  first_run = not os.path.exists(PROFILE_DIR)

  options = Options()
  options.add_argument(f"--user-data-dir={PROFILE_DIR}")
  options.add_argument("--no-first-run")
  options.add_argument("--no-default-browser-check")
  options.add_argument("--disable-session-crashed-bubble")
  options.add_argument("--disable-infobars")
  options.add_argument("--hide-crash-restore-bubble")
  options.add_experimental_option("excludeSwitches", ["enable-automation"]) # type: ignore
  os.makedirs(CSV_LOGS_DIR, exist_ok=True)
  prefs: dict[str, str | bool] = {
    "download.prompt_for_download": False,
  }
  options.add_experimental_option("prefs", prefs) # type: ignore
  options.add_argument("--force-device-scale-factor=0.5")
  driver = webdriver.Chrome(options=options)

  driver.get(target_url)

  if first_run:
    while getGrafanaSessionCookie(driver) is None:
      time.sleep(1)

  try:
    sign_in_link = WebDriverWait(driver, 3).until(
      EC.element_to_be_clickable((By.XPATH,
        "/html/body/div/div/div[1]/div/div/main/div[2]/div/div/div/div/div[2]/div/div[2]/a"))
    )
    if sign_in_link.text.strip() == "Sign in with GitHub":
      sign_in_link.click()
  except TimeoutException:
    pass
  
  if time_range != "24h":
    if not time_range[0].isdigit() or not time_range[1].isdigit() or time_range[2] != "h":
      return
    
    change_time_range(driver, time_range)

  screenshot(driver, id)

  grafana_session_cookie = getGrafanaSessionCookie(driver)
  if grafana_session_cookie:
    print(json.dumps({ "grafana_session": grafana_session_cookie }))
    return

  driver.close()

  print(json.dumps({ "error": "No Grafana Session Found" }))
  return None


if __name__ == "__main__":
  main()