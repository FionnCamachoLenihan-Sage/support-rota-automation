from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import os
import time
import glob
from constants import CSV_LOGS_DIR
from utils.constants import (
    PANELS_MEATBALL_MENU_TESTID_TEMPLATE, PANEL_CARD_TESTID_TEMPLATE,
    EXPLORE_DATA_TESTID, RADIO_BUTTONS_DATA_TESTID,
    DOWNLOAD_ARIA_LABEL,
    TIME_RANGE_FROM_FIELD_TESTID,
    TIME_RANGE_OPEN_TESTID,
)


def panel_testid(panel_name: str):
    return PANELS_MEATBALL_MENU_TESTID_TEMPLATE + panel_name

def panel_card_testid(panel_name: str):
    return PANEL_CARD_TESTID_TEMPLATE + panel_name

def new_tab_open(driver: WebDriver, element: WebElement):
    ActionChains(driver).key_down(Keys.CONTROL).click(element).key_up(Keys.CONTROL).perform()

def navigate_to_logs(driver: WebDriver, panel_name: str):
    current_testid = panel_testid(panel_name)
    print(f"Navigating to logs for panel: {panel_name}")
    try:
      CARD_XPATH = f"//section[@data-testid=\"{panel_card_testid(panel_name)}\"]"
      print(f"\tLooking for {CARD_XPATH}")
      card_element = WebDriverWait(driver, 10).until(
          EC.presence_of_element_located((By.XPATH, CARD_XPATH)),
          f"Could not find {panel_name}"
      )
      ActionChains(driver).move_to_element(card_element).perform()

      MEATBALL_XPATH = f"//button[@data-testid=\"{current_testid}\"]"
      print(f"\tLooking for {MEATBALL_XPATH}")
      WebDriverWait(driver, 10).until(
          EC.element_to_be_clickable((By.XPATH, MEATBALL_XPATH)),
          f"Could not find {panel_name}"
      ).click()

      time.sleep(.5)

      EXPLORE_XPATH = f"//a[@data-testid=\"{EXPLORE_DATA_TESTID}\"]"
      print(f"\tLooking for {EXPLORE_XPATH}")
      explore_element = WebDriverWait(driver, 10).until(
          EC.element_to_be_clickable((By.XPATH, EXPLORE_XPATH)),
          f"Could not find {panel_name}"
      )
      new_tab_open(driver, explore_element)
      driver.switch_to.window(driver.window_handles[-1])

      RADIO_BUTTONS_XPATH = f"//div[@data-testid=\"{RADIO_BUTTONS_DATA_TESTID}\"]"
      print(f"\tLooking for {RADIO_BUTTONS_XPATH}")
      radio_buttons = WebDriverWait(driver, 10).until(
          EC.presence_of_all_elements_located((By.XPATH, RADIO_BUTTONS_XPATH)),
          f"Could not find {panel_name}"
      )
      
      log_radio_button = None
      for button in radio_buttons:
          if button.text.strip() == "Logs":
              log_radio_button = button
              break

      if log_radio_button:
          log_radio_button.click()
      else:
          print(f"Could not find Logs radio button for {panel_name}")

    except TimeoutException as e:
        print(f"{e}")


def download_logs(driver: WebDriver):
  try:
    download_button = WebDriverWait(driver, 3).until(
      EC.element_to_be_clickable((By.XPATH, f"//button[@aria-label='{DOWNLOAD_ARIA_LABEL}']"))
    )
    download_button.click()

    csv_button = WebDriverWait(driver, 3).until(
      EC.element_to_be_clickable((By.XPATH, "//button[.//span[text()='csv']]"))
    )
    csv_button.click()

    # Wait for download to complete
    timeout = 30
    elapsed = 0
    while elapsed < timeout:
      downloading = glob.glob(os.path.join(CSV_LOGS_DIR, "*.crdownload"))
      csv_files = glob.glob(os.path.join(CSV_LOGS_DIR, "*.csv"))
      if csv_files and not downloading:
        break
      time.sleep(0.5)
      elapsed += 0.5
    print("Download complete")

  except TimeoutException:
    print("Could not find Download logs button")


def change_time_range(driver: WebDriver, time_range: str):
  try:
    TIME_RANGE_OPEN_XPATH = f"//button[@data-testid=\"{TIME_RANGE_OPEN_TESTID}\"]"
    time_range_button = WebDriverWait(driver, 10).until(
      EC.element_to_be_clickable((By.XPATH, TIME_RANGE_OPEN_XPATH))
    )
    time_range_button.click()

    TIME_RANGE_FROM_FIELD_XPATH = f"//input[@data-testid=\"{TIME_RANGE_FROM_FIELD_TESTID}\"]"
    from_field = WebDriverWait(driver, 10).until(
      EC.element_to_be_clickable((By.XPATH, TIME_RANGE_FROM_FIELD_XPATH))
    )
    from_field.clear()
    from_field.send_keys(f"now-{time_range}")
    from_field.send_keys(Keys.RETURN)
    print(f"Changed time range to now-{time_range}")
    time.sleep(2) # Wait for logs to refresh after changing time range

  except TimeoutException:
    print("Could not find time range button or desired time range option")
