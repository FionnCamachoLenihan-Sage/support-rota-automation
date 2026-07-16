from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
import time
from utils.constants import (
    TIME_RANGE_FROM_FIELD_TESTID,
    TIME_RANGE_OPEN_TESTID,
)

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
