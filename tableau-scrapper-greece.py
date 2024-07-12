import os
import shutil
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta


def open_browser(url):
    driver = webdriver.Chrome()
    driver.get(url)
    time.sleep(10)
    email_input = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, "email"))
    )
    email_input.send_keys('m.tsiakiris@faradaynorton.com')
    sign_in_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "login-submit"))
    )
    sign_in_button.click()
    time.sleep(5)
    password_input = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, "password"))
    )
    password_input.send_keys('#X^Ue65rGzv7fREvrxVp')
    # Click the 'Sign in' button to submit the form
    sign_in_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "signInButton"))
    )
    sign_in_button.click()
    time.sleep(15)
    close_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-tb-test-id='postlogin-footer-close-Button']"))
    )
    close_button.click()

    time.sleep(5)

    return driver


def print_html_and_check_class(driver, iframe_selector="iframe", element_class="tab-dashboard-region", timeout=60,
                               filename_prefix="html_"):
    """
    Prints and writes the HTML content of a specific element within an iframe to a text file.
    Args:
        driver (selenium.webdriver.remote.webdriver.WebDriver): The WebDriver instance.
        iframe_selector (str, optional): Selector for the iframe element. Defaults to "iframe".
        element_class (str, optional): Class name of the target element within the iframe. Defaults to "tab-dashboard-region".
        timeout (int, optional): The maximum wait time in seconds. Defaults to 10.
        filename_prefix (str, optional): Prefix for the text file name. Defaults to "html_".
    Returns:
        str: The raw HTML content of the target element (if found), or None if not found.
    """
    try:
        # Wait for the main page to load (optional)
        WebDriverWait(driver, timeout).until(
            lambda d: d.execute_script('return document.readyState') == 'complete'
        )
        # Locate the iframe (modify selector if needed)
        iframe_element = driver.find_element(By.CSS_SELECTOR, iframe_selector)
        # Switch context to the iframe
        driver.switch_to.frame(iframe_element)
        # Wait for the target element with a class 'tab-dashboard-region' to be present and visible
        target_element = WebDriverWait(driver, timeout).until(
            EC.visibility_of_element_located((By.CLASS_NAME, element_class))
        )
        # Get the target element's outer HTML
        html_content = target_element.get_attribute('outerHTML')
        # Create a unique filename
        now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"{filename_prefix}{now}.txt"
        # Write target element's HTML content to the text file
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"Content of element with class '{element_class}' stored in text file: {filename}")
        return html_content
    except (TimeoutException, StaleElementReferenceException) as e:
        print(f"An error occurred: {e}")
        return None


def update_dates(driver, start_date, end_date, iframe_selector="iframe", class_name="QueryBox", start_date_name=None,
                 end_date_name=None):
    """Update the start and end date input fields within an iframe,
    using CSS selectors and potentially name attributes."""
    try:

        # Wait for the iframe to be present and switch to it
        WebDriverWait(driver, 60).until(
            EC.frame_to_be_available_and_switch_to_it((By.TAG_NAME, "iframe"))
        )
        time.sleep(20)

        # Find the start date input using CSS selector and potentially name attribute
        start_date_input = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//input[@aria-label='Map Start Month']"))
        )
        start_date_input.send_keys('\ue003' * 20)  # Sends 20 backspaces
        time.sleep(3)
        start_date_input.send_keys(start_date)
        start_date_input.send_keys(Keys.ENTER)

        time.sleep(30)

        # Find the end date input using CSS selector and potentially name attribute
        end_date_input = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//input[@aria-label='Map End Month']"))
        )
        end_date_input.send_keys('\ue003' * 20)  # Sends 20 backspaces
        time.sleep(3)
        end_date_input.send_keys(end_date)
        end_date_input.send_keys(Keys.ENTER)  # Simulate pressing Enter after entering the date
        # Switch back to the main frame (optional)
        driver.switch_to.default_content()
    except Exception as e:
        print(f"Error updating date fields: {str(e)}")


def draw_rectangle_on_map(driver):
    try:
        # Wait for the iframe to be present and switch to it
        WebDriverWait(driver, 60).until(
            EC.frame_to_be_available_and_switch_to_it((By.TAG_NAME, "iframe"))
        )
        time.sleep(20)

        # Locate the parent div containing the map element
        parent_div = driver.find_element(By.CSS_SELECTOR,
                                         'div.tab-tvView.tvimagesNS#view2484860129000949599_4945100679507155691')
        if parent_div:
            # Locate the map element
            map_element = parent_div.find_element(By.CSS_SELECTOR, 'div.tvimagesContainer img')
            driver.execute_script("arguments[0].scrollIntoView(true);", map_element)
            time.sleep(2)

            # Get the location and size of the map element
            map_location = map_element.location
            map_size = map_element.size
            print(f"Map location: {map_location}")
            print(f"Map size: {map_size}")

            # # Define the start and end points for the drag within the map
            start_x_offset = -1 * (map_size["width"] / 2 - 100)  # Starting offset from the top-left corner of the map element
            start_y_offset = -1 * (map_size["height"] / 2 - 10)
            width_offset = map_size["width"] - 150 # Width of the rectangle to draw
            height_offset = map_size["height"] - 20  # Height of the rectangle to draw

            # Ensure the offsets are within the bounds of the map size
            action = ActionChains(driver)
            action.move_to_element_with_offset(map_element, start_x_offset, start_y_offset).click_and_hold()
            action.move_by_offset(width_offset, height_offset).release().perform()
            print("Performed click-and-drag action on the map element.")
            time.sleep(30)

    except Exception as e:
        print(f"Error performing click-and-drag action: {str(e)}")


def rename_downloaded_file(start_date):
    """
    Renames the downloaded file from "Map View_data.csv" to "MonthOrder-Year.csv".
    """
    # Define the downloads folder and the original file name
    downloads_folder = os.path.expanduser('~/Downloads')
    original_file_name = os.path.join(downloads_folder, "Map View_data.csv")

    # Define the new file name based on the start_date
    new_file_name = os.path.join(downloads_folder, f"{start_date.strftime('%m-%Y')}.csv")

    # Check if the original file exists and rename it
    if os.path.exists(original_file_name):
        shutil.move(original_file_name, new_file_name)
        print(f"Renamed '{original_file_name}' to '{new_file_name}'")
    else:
        print(f"File '{original_file_name}' not found.")


def download_data_of_new_popup(driver):
    try:
        # Wait for the iframe to be present and switch to it
        download_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "download"))
        )
        download_btn.click()
        time.sleep(3)

        data_download_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//div[@data-tb-test-id='download-flyout-download-data-MenuItem']"))
        )
        data_download_btn.click()

        # Get the handle of the current window
        original_window = driver.current_window_handle
        time.sleep(2)

        # Get handles of all open windows/tabs
        all_windows = driver.window_handles

        # Find the new window handle
        for window in all_windows:
            if window != original_window:
                new_window = window
                break

        # Switch to the new window
        driver.switch_to.window(new_window)

        # Perform actions in the new window (e.g., fetch some data)
        data_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//button[@data-tb-test-id='download-data-Button']"))
        )
        data_element.click()
        time.sleep(10)

        # Close the new window
        driver.close()

        # Switch back to the original window
        driver.switch_to.window(original_window)

        print("Performed downloading CSV data.")
    except Exception as e:
        print(f"Error downloading data using action: {str(e)}")


def generate_monthly_periods(start_date, end_date):
    """
    Generates monthly periods between start_date and end_date.
    Each period is represented as a tuple of strings in the format 'm/d/Y'.
    """
    periods = []
    current_start = start_date

    while current_start < end_date:
        current_end = current_start + relativedelta(months=1)
        periods.append((current_start.strftime("%m/%d/%Y"), current_end.strftime("%m/%d/%Y")))
        current_start = current_end

    return periods


def main():
    url = "https://10ay.online.tableau.com/#/site/airdna/views/Europe_PPD/Map"
    driver = open_browser(url)

    # DEBUG - print HTML
    # print_html_and_check_class(driver)

    # Generate periods dynamically
    start_date = datetime.strptime("1/1/2019", "%m/%d/%Y")
    end_date = datetime.strptime("1/1/2023", "%m/%d/%Y")
    periods = generate_monthly_periods(start_date, end_date)


    # Loop through each period and update dates
    for start_date_str, end_date_str in periods:
        print(f"Processing period: {start_date_str} to {end_date_str}")
        update_dates(driver, start_date_str, end_date_str)
        draw_rectangle_on_map(driver)
        download_data_of_new_popup(driver)
        print(f"CSV data downloaded for period: {start_date_str} to {end_date_str}")
        start_date = datetime.strptime(start_date_str, "%m/%d/%Y")
        rename_downloaded_file(start_date)


    input("Press any key to close the browser... ")
    driver.quit()


if __name__ == "__main__":
    main()
