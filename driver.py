import logging
import sys
import time
from collections import deque

from retry import retry
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys

from config import get_config
from exceptions import NoNativeLocationsException
from exceptions import NotEligibleException
from utils import send_text

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

class Driver:
    def __init__(self):
        self.config = get_config()
        self.driver = webdriver.Chrome(self.config.chromedriver_location)
        self.wait = WebDriverWait(self.driver, 10)
        self.routes_map = {
            "location-search": self._pick_location,
            "personal-details": self._fill_form,
        }
        self.locations = self.config.get_locations()

    def _answer_eligibility(self):
        logging.info("Answering eligibility")
        try:
            self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@data-testid='landing-page-continue']"))).click()
        except TimeoutException:
            raise NotEligibleException("Restart the app")
        self.driver.find_element(By.NAME, "q-screening-18-yr-of-age").click()
        self.driver.find_element(By.NAME, "q-screening-health-data").click()
        self.driver.find_element(By.NAME, "q-screening-privacy-statement").click()
        self.driver.find_element(By.NAME, "q-screening-accuracy-attestation").click()
        # Get screening eligibility
        age_ranges = self.driver.find_elements(By.XPATH, "//input[@name='q-screening-eligibility-age-range']")
        for age_range in age_ranges:
            if age_range.get_attribute("value").startswith(self.config.age_range):
                age_range.click()
        self.driver.find_element(By.XPATH, f"//input[@name='q-screening-underlying-health-condition'][@value='{self.config.health_condition}']").click()
        self.driver.find_element(By.XPATH, f"//input[@name='q-screening-disability'][@value='{self.config.disability}']").click()
        self.driver.find_element(By.ID, "q-screening-eligibility-industry").click()
        dropdown = self.driver.find_element(By.ID, "q-screening-eligibility-industry")
        dropdown.find_element(By.XPATH, f"//option[. = '{self.config.industry}']").click()
        self.driver.find_element(By.ID, "q-screening-eligibility-county").click()
        dropdown = self.driver.find_element(By.ID, "q-screening-eligibility-county")
        dropdown.find_element(By.XPATH, f"//option[. = '{self.config.county}']").click()
        self.driver.find_element(By.XPATH, "//button[@data-testid='continue-button']").click()
        try:
            self.wait.until(lambda driver: driver.current_url.endswith("location-search"))
        except TimeoutException:
            raise NotEligibleException("We are currently not eligible.")
    
    def _pick_location(self):
        logging.info("Picking location")
        try:
            search_input = self.wait.until(EC.element_to_be_clickable((By.ID, "location-search-input")))
        except TimeoutException:
            return
        try:
            location = next(self.locations)
        except StopIteration:
            self.locations = self.config.get_locations()
            return
        send_text(search_input, str(location))
        self.driver.find_element(By.XPATH, "//button[@data-testid='location-search-page-continue']").click()
        # self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "tw-space-y-4")))
        # try:
        #     native_location = self.driver.find_element(By.XPATH, "//button[@data-testid='location-select-location-continue']")
        #     native_location.click()
        # except NoSuchElementException:
        #     self.driver.back()
        #     return

    def _schedule_appointments(self):
        pass

    def _fill_form(self):
        # Don't refill if already filled out
        if self.driver.find_element(By.ID, "q-patient-firstname").get_attribute("value"):
            return
        logging.info("Filling out personal information")
        self.driver.find_element(By.ID, "q-patient-firstname").click()
        self.driver.find_element(By.ID, "q-patient-firstname").send_keys(self.config.first_name)
        self.driver.find_element(By.ID, "q-patient-lastname").click()
        self.driver.find_element(By.ID, "q-patient-lastname").send_keys(self.config.last_name)
        self.driver.find_element(By.NAME, "month").click()
        self.driver.find_element(By.NAME, "month").send_keys(self.config.dob_month)
        self.driver.find_element(By.NAME, "day").click()
        self.driver.find_element(By.NAME, "day").send_keys(self.config.dob_day)
        self.driver.find_element(By.NAME, "year").click()
        self.driver.find_element(By.NAME, "year").send_keys(self.config.dob_year)
        self.driver.find_element(By.ID, "q-patient-mothersfirstname").click()
        self.driver.find_element(By.ID, "q-patient-mothersfirstname").send_keys(self.config.mother)
        self.driver.find_element(By.XPATH, f"//input[@name='q-patient-gender'][@value='{self.config.gender}']").click()
        self.driver.find_element(By.ID, "q-patient-race").click()
        dropdown = self.driver.find_element(By.ID, "q-patient-race")
        dropdown.find_element(By.XPATH, f"//option[. = '{self.config.race}']").click()
        self.driver.find_element(By.ID, "q-patient-ethnicity").click()
        dropdown = self.driver.find_element(By.ID, "q-patient-ethnicity")
        dropdown.find_element(By.XPATH, f"//option[. = '{self.config.ethnicity}']").click()
        self.driver.find_element(By.ID, "q-patient-email").click()
        self.driver.find_element(By.ID, "q-patient-email").send_keys(self.config.email)
        self.driver.find_element(By.ID, "q-patient-mobile").click()
        self.driver.find_element(By.ID, "q-patient-mobile").send_keys(self.config.mobile)
        self.driver.find_element(By.ID, "q-patient-address").click()
        self.driver.find_element(By.ID, "q-patient-address").send_keys(self.config.address)
        self.driver.find_element(By.ID, "q-patient-city").click()
        self.driver.find_element(By.ID, "q-patient-city").send_keys(self.config.city)
        self.driver.find_element(By.ID, "q-patient-zip-code").click()
        self.driver.find_element(By.ID, "q-patient-zip-code").send_keys(self.config.zip_code)
        self.driver.find_element(By.ID, "q-patient-industry").click()
        dropdown = self.driver.find_element(By.ID, "q-patient-industry")
        dropdown.find_element(By.XPATH, f"//option[. = '{self.config.industry}']").click()
        self.driver.find_element(By.XPATH, "//input[@name='q-patient-health-insurance'][@value='Yes']").click()
        self.driver.find_element(By.ID, "q-patient-primary-carrier").click()
        dropdown = self.driver.find_element(By.ID, "q-patient-primary-carrier")
        dropdown.find_element(By.XPATH, f"//option[. = '{self.config.primary_carrier}']").click()
        self.driver.find_element(By.NAME, "q-patient-primary-holder").click()
        self.driver.find_element(By.ID, "q-patient-policy-number").click()
        self.driver.find_element(By.ID, "q-patient-policy-number").send_keys(str(self.config.policy_number))
        self.driver.find_element(By.CSS_SELECTOR, "span:nth-child(26) .tw-flex:nth-child(2)").click()
        self.driver.find_element(By.CSS_SELECTOR, "span:nth-child(27) .tw-flex:nth-child(2)").click()
        self.driver.find_element(By.CSS_SELECTOR, "span:nth-child(28) .tw-flex:nth-child(2)").click()
        self.driver.find_element(By.CSS_SELECTOR, "span:nth-child(29) .tw-flex:nth-child(2)").click()
        self.driver.find_element(By.CSS_SELECTOR, "span:nth-child(30) .tw-flex:nth-child(2)").click()
        self.driver.find_element(By.CSS_SELECTOR, "span:nth-child(31) .tw-flex:nth-child(2)").click()
        self.driver.find_element(By.CSS_SELECTOR, "span:nth-child(32) .tw-flex:nth-child(2)").click()
        self.driver.find_element(By.CSS_SELECTOR, "span:nth-child(33) .tw-flex:nth-child(2)").click()
        self.driver.find_element(By.CSS_SELECTOR, "span:nth-child(34) .tw-flex:nth-child(2)").click()
        self.driver.find_element(By.CSS_SELECTOR, "span:nth-child(35) .tw-flex:nth-child(2)").click()
        self.driver.find_element(By.CSS_SELECTOR, "span:nth-child(36) .tw-flex:nth-child(2)").click()
        self.driver.find_element(By.CSS_SELECTOR, "span:nth-child(37) .tw-flex:nth-child(1)").click()
        # self.driver.find_element(By.CSS_SELECTOR, ".tw-border-accent2").click()

    @retry(exceptions=Exception, delay=1)
    def run(self):
        self.driver.get("https://myturn.ca.gov/")
        self._answer_eligibility()
        while True:
            route_ending = self.driver.current_url.split("/")[-1]
            if route_ending in self.routes_map:
                self.routes_map[route_ending]()
            time.sleep(2)

if __name__ == "__main__":
    Driver().run()