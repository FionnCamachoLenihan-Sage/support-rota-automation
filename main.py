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
import csv
import glob
import sys
from datetime import datetime
from constants import (
  BASE_DIR, LOG_GROUP_TYPES_OTHER, PROFILE_DIR, SCREENSHOTS_DIR, CSV_LOGS_DIR,
  LOG_GROUP_TYPES, TEMPLATE, PANEL_LIST, TEMPLATE_TRANSLATIONS,
)

type LogErrors = dict[str, dict[str, str | int]]

from utils.navigation import change_time_range, navigate_to_logs, download_logs
from utils.clean import clean_message
from utils.constants import MAX_KEY_LEN


# Returns: errors found in current file in tmp_logs
def get_basic_errors() -> LogErrors:
  errors: LogErrors = {}

  csv_files = glob.glob(os.path.join(CSV_LOGS_DIR, "*.csv"))
  if not csv_files:
    print("No CSV files found in tmp_logs/")
    return {}

  csv_path = csv_files[0] # Should only be one file
  with open(csv_path, "r", encoding="utf-8") as f:
    reader = csv.reader(f)
    rows = list(reader)
    
    print(f"Read {len(rows)} rows from {csv_path}")

    for row in rows[1:]:
      message: str = row[2]
      message_clean = clean_message(message)
      log_group: str = row[4]
      log_name: str = row[16]
      log_data: dict[str, str | int] = {"log_group": log_group, "log_name": log_name, "message": message, "count": 1}      
      # short_message = message.split(" ")[0] if message else "Unknown"
      key: str = message_clean[:MAX_KEY_LEN] # Truncate to 500 chars to avoid excessively long keys, adjust as needed
      if key not in errors:
        errors[key] = log_data
      else:
        current_count: int = int(errors[key]["count"]) # Potential crash point
        errors[key]["count"] = current_count + 1
        print(f"Unexpected data format for error: {key}, data: {errors[key]}")

  for f in glob.glob(os.path.join(CSV_LOGS_DIR, "*")):
      os.remove(f)

  return errors


def screenshot(driver: WebDriver):
  # Wait for page to fully load
  time.sleep(2)

  # Take screenshot
  os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
  timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
  screenshot_path = os.path.join(SCREENSHOTS_DIR, f"screenshot_{timestamp}.png")
  driver.save_screenshot(screenshot_path) # type: ignore
  print(f"Screenshot saved to: {screenshot_path}")


def save_logs(logs: LogErrors):
  if not logs:
    print("No logs to save.")
    return

  output_path = os.path.join(BASE_DIR, f"logs.txt")
  with open(output_path, "a", encoding="utf-8") as f:
    f.write(json.dumps(logs, indent=2))
    f.write("\n")


def sort_errors(template: dict[str, dict[str, str]], logs: LogErrors):
  sorted_template = template
  for key, data in logs.items():
    log_group = str(data["log_group"]).split("/")[-1] # failure point
    if log_group not in LOG_GROUP_TYPES:
      log_group = LOG_GROUP_TYPES_OTHER

    translated_group = TEMPLATE_TRANSLATIONS[log_group]
    sorted_template[translated_group][key] = str(data["count"])
  
  return sorted_template


def build_error_template(template: dict[str, dict[str, str]], logs: LogErrors, panel_name: str):
  output = template
  if panel_name == "Errors":
    output = sort_errors(template, logs)
  else:
    for key, data in logs.items():
      translated_heading = TEMPLATE_TRANSLATIONS[panel_name]
      output[translated_heading][key] = str(data["count"])

  return output


def build_formatted_template(template: dict[str, dict[str, str]]):
  output_path = os.path.join(BASE_DIR, f"output.txt")
  with open(output_path, "a", encoding="utf-8") as f:
    for heading, errors in template.items():
      f.write(f"{heading}:\n")

      if not errors:
        f.write("N/A\n")
        continue
      
      for error, count in errors.items():
        f.write(f"{count}x `{error}`\n")


def main():
  if len(sys.argv) != 3:
    print("Usage: python main.py [ENOTARGETURL] [TIME_RANGE]")
    return
  
  target_url = sys.argv[1]
  time_range = sys.argv[2]
  first_run = not os.path.exists(PROFILE_DIR)
  os.remove("logs.txt") if os.path.exists("logs.txt") else None
  os.remove("output.txt") if os.path.exists("output.txt") else None
  for f in glob.glob(os.path.join(CSV_LOGS_DIR, "*")):
    os.remove(f)

  for f in glob.glob(os.path.join(SCREENSHOTS_DIR, "*")):
    os.remove(f)

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
    "download.default_directory": CSV_LOGS_DIR,
    "download.prompt_for_download": False,
  }
  options.add_experimental_option("prefs", prefs) # type: ignore
  options.add_argument("--force-device-scale-factor=0.5")
  driver = webdriver.Chrome(options=options)

  driver.get(target_url)

  if first_run:
    print("First run: please sign in with GitHub in the browser.")
    print("After signing in, press Enter here to continue.")
    input()

  # Timeout potentially too short
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
      print("Invalid time range format. Use format like '24h'.")
      return
    
    change_time_range(driver, time_range)

  screenshot(driver)

  template = TEMPLATE
  for panel in PANEL_LIST:
    navigate_to_logs(driver, panel)
    download_logs(driver)

    logs = get_basic_errors()
    template = build_error_template(template, logs, panel)

    driver.close()
    driver.switch_to.window(driver.window_handles[0])

  driver.close()
  build_formatted_template(template)


if __name__ == "__main__":
  main()