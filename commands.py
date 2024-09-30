from selenium import webdriver
from time import sleep
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.support import expected_conditions as EC

# Настройка опций для Microsoft Edge
edge_options = Options()
edge_options.use_chromium = True

# Установка драйвера и запуск браузера
service = Service(EdgeChromiumDriverManager().install())
driver = webdriver.Edge(service=service, options=edge_options)


def login():

    driver.get("https://*.*.*.*/controlPanel/policies") # указываем айпи или дднс
    login_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "ndm-input__unit-text")))
    login_input.send_keys("admin")

    search_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "ndm-input__unit-text--password")))
    search_input.send_keys("parol") # указываем парол от роутера

    search_button = driver.find_element(By.XPATH, "/html/body/ndm-layout/div/div/div/div/section/div[1]/div[1]/div/section[2]/form/ndm-button/button/span/span")
    search_button.click()

    policies_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located(
        (By.XPATH, '//*[@id="cp-main-container"]/div[1]/div[1]/div[1]/div/div[2]/div/ndm-tabs/div/ul/li[2]')))
    policies_input.click()



def exit():
    exit = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH,
                                                                           '/html/body/ndm-layout/div/div[2]/div[1]/ndm-menu/div/div[2]/div[1]/div[1]/div/div[7]/div/span[1]/span')))
    exit.click()

def find(device):
    devices = driver.find_elements(By.CSS_SELECTOR, "div.policy-consumers-list__consumer-label.ng-binding.ng-scope")

    for element in devices:
        if element.text == device:
            return True
        else:
            continue



def toggle(device):
    login()
    politics = driver.find_elements(By.CSS_SELECTOR, "div span.ng-scope")
    for element in politics:
        if element.text == "Политика по умолчанию":
            element.click()
            print("политика по умолчанию")
            break
    if find(device):
         return move_to_vpn(device)
    else:
        politics = driver.find_elements(By.CSS_SELECTOR, "div span.ng-scope")
        for element in politics:
            if element.text == "VPN":
                element.click()
                break
        if find(device):
            return move_back(device)
        else:
         return "Устройство не найдено"


def move_to_vpn(device):

    devices = driver.find_elements(By.CSS_SELECTOR, "div.policy-consumers-list__consumer-label.ng-binding.ng-scope")
    for element in devices:
        if element.text == device:
            element.click()
            break

    listos = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="sb-5"]/a')))
    listos.click()

    policies = driver.find_elements(By.CSS_SELECTOR, 'a')
    for element in policies:
        if element.text == 'VPN':
            element.click()
            break

    confirm = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH,
                                                                              '//*[@id="cp-main-container"]/div[1]/div[1]/div[1]/div/div[2]/div/div[1]/div[2]/div/div/div/form/div[2]/ndm-button/button/span/span')))
    confirm.click()
    sleep(1)

    exit()

    return "На устройстве включен ВПН"


def move_back(device):

    devices = driver.find_elements(By.CSS_SELECTOR, "div.policy-consumers-list__consumer-label.ng-binding.ng-scope")
    for element in devices:
        if element.text == device:
            element.click()
            break

    listos = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="sb-5"]/a')))
    listos.click()

    policies = driver.find_elements(By.CSS_SELECTOR, 'a')
    for element in policies:
        if element.text == 'Политика по умолчанию':
            element.click()
            break

    confirm = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH,
                                                                              '//*[@id="cp-main-container"]/div[1]/div[1]/div[1]/div/div[2]/div/div[1]/div[2]/div/div/div/form/div[2]/ndm-button/button/span/span')))
    confirm.click()
    sleep(1)

    exit()

    return "На устройстве выключен ВПН"

