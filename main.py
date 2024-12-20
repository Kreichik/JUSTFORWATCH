from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

options = webdriver.ChromeOptions()
options.page_load_strategy = 'none'
# Укажите путь к драйверу Chrome
CHROMEDRIVER_PATH = "C:\\chrome_driver\\chromedriver.exe"

# Учетные данные
EMAIL = "77773386306"
PASSWORD = "Aa280606"


def login_to_platform(driver):
    driver.get("https://admin.eduser.app/login")

    # Ожидаем, пока элемент для ввода email станет доступным
    email_input = WebDriverWait(driver, 40).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="__layout"]/div/div/div/input'))
    )
    email_input.send_keys(EMAIL)
    time.sleep(2)

    # Ожидаем появления поля для ввода пароля
    password_input = driver.find_element(By.XPATH, '/html/body/div/div/div/div/div/div/input')
    password_input.send_keys(PASSWORD)
    time.sleep(2)
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="__layout"]/div/div/div/button'))
    ).click()

    # Если требуется подтверждение (MFA), пользователь должен подтвердить вручную
    print("Если требуется подтверждение, выполните его в браузере")


def get_assignments(driver):
    # Переход на вкладку "Assignments"
    # time.sleep(10)
    driver.get("https://admin.eduser.app/supervision/groups/my")
    # Ожидаем загрузки страницы и появления элемента для перехода к заданиям
    groups = WebDriverWait(driver, 40).until(
        EC.element_to_be_clickable((By.CLASS_NAME, 'vs-sidebar'))
    )
    groups.find_element(By.XPATH, "//*[contains(text(), 'Бақдаулет тобы')]").click()
    # group_button.click()
    time.sleep(20)
    choose_div = driver.find_element(By.ID, "choose_div")

    choose_time = driver.find_element(By.XPATH, '//*[@id="Выполнено"]')
    choose_time.click()

    # Ожидаем появления элементов с заданиями
    assignments = WebDriverWait(driver, 40).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, 'item-container__hLpG3'))
    )

    print(assignments)
    for assignment in assignments:
        title = assignment.find_element(By.CSS_SELECTOR, ".title-class").text
        due_date = assignment.find_element(By.CSS_SELECTOR, ".due-date-class").text
        print(f"Задание: {title}, Срок сдачи: {due_date}")


if __name__ == "__main__":
    # Создаем объект Service для указания пути к драйверу
    service = Service(CHROMEDRIVER_PATH, options=options)
    driver = webdriver.Chrome(service=service)

    try:
        login_to_platform(driver)
        get_assignments(driver)
    finally:
        driver.quit()
