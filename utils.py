from selenium.webdriver.common.keys import Keys

def clear_text(element):
    while element.get_attribute("value"):
        element.send_keys(Keys.BACK_SPACE)

def send_text(element, text):
    clear_text(element)
    element.send_keys(text)