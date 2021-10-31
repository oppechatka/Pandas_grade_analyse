from loguru import logger
import pandas as pnd
import grade_download as GD
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
import time

def load_certificates(file):
    try:
        cert_lst = pnd.read_excel(file)
    except FileNotFoundError:
        logger.error('Нет файла ' + file)
        return -1
    # print(cert_lst.info())
    print(cert_lst.columns)
    print(cert_lst[['Курс', 'Сессия', 'Email', 'fio', 'fi', 'Балл', 'id_cert', 'link']].columns)
    print(cert_lst.sort_values(['Курс', 'Сессия'], ascending=True))
    courses_lst = cert_lst.groupby(['Курс', 'Сессия'])['Email'].count()
    print(courses_lst[[0]][1])
    #
    # driver = GD.make_web_driver()
    # GD.login(driver)
    # driver.get('https://openedu.ru/upd/urfu/students/certificates') # страница загрузки сертификатов
    # WebDriverWait(driver, 30000).until(expected_conditions.presence_of_element_located(
    #     (By.ID, '//*[@id="filter-form"]/div[2]/label')))
    # driver.find_element_by_xpath('//*[@id="filter-form"]/div[3]').click()
    # time.sleep(1)
    # driver.find_element_by_xpath('//*[@id="filter-form"]/div[3]').send_keys()

if __name__ == '__main__':
    load_certificates('Сертификаты fall_2020.xlsx')