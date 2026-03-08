from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
import time
import os

# Load credentials from .env file
load_dotenv()
OU_EMAIL = os.getenv("OU_EMAIL")
OU_PASSWORD = os.getenv("OU_PASSWORD")
EVENT_URL = os.getenv("EVENT_URL")

if not EVENT_URL:
    EVENT_URL = input("Enter the full GivePulse Event Management URL:\n> ").strip()

driver = webdriver.Chrome()
driver.get("https://www.givepulse.com/login")
time.sleep(3) 

# Dismiss cookie popup if present
try:
    accept_btn = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "button.t-acceptAllButton"))
    )
    driver.execute_script("arguments[0].click();", accept_btn)
    time.sleep(1)
except:
    pass

# Click SSO button
sso_button = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.ID, "showSSO-login"))
)
driver.execute_script("arguments[0].click();", sso_button)
time.sleep(2)

# Type the login provider into the typeahead search field
provider_input = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.ID, "search_sso_groups_id_login"))
)
provider_input.clear()
provider_input.send_keys("The University of Oklahoma")
time.sleep(2) 

# Click the matching suggestion from the typeahead dropdown
suggestion = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'tt-suggestion')]//p[contains(text(), 'The University of Oklahoma')]"))
)
suggestion.click()
time.sleep(1)

# Click Login button to proceed to university SSO
login_button = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.ID, "btn-login-sso-login"))
)
driver.execute_script("arguments[0].click();", login_button)

# Fill in OU SSO credentials
time.sleep(3)  
email_input = WebDriverWait(driver, 15).until(
    EC.presence_of_element_located((By.ID, "ou-email"))
)
email_input.clear()
email_input.send_keys(OU_EMAIL)

password_input = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.ID, "ou-password"))
)
password_input.clear()
password_input.send_keys(OU_PASSWORD)

# Click "Sign In"
sign_in_button = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.CSS_SELECTOR, "input.button--blue"))
)
sign_in_button.click()

print("Waiting for SSO login to complete...")
WebDriverWait(driver, 300).until(
    lambda d: "givepulse.com" in d.current_url
)
print("SSO login complete!")
time.sleep(2)

driver.get(EVENT_URL)

# Click the "Actions" dropdown button
actions_button = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Actions')]"))
)
actions_button.click()
time.sleep(1)

# Click the "Export" option
export_option = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "Export"))
)
export_option.click()
time.sleep(2)

# Select "All Data" 
all_data = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.XPATH, "(//input[@type='radio'])[1]"))
)
all_data.click()
time.sleep(1)

# Click the Export button in the dialog
time.sleep(1)
driver.execute_script("""
    var btns = document.querySelectorAll('button.btn-primary');
    for (var btn of btns) {
        if (btn.offsetParent !== null) {
            btn.click();
            break;
        }
    }
""")

input("Done. Press Enter to close...")
