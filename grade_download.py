from loguru import logger
import datetime
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import NoSuchElementException

USERNAME = ''
PASSWORD = ''

# Для настройки браузера нужен полный путь к папкам
GRADE_REPORTS_DIR = '/home/hinahin/PycharmProjects/Pandas_grade_analyse/grade_reports/'
EXAM_RESULTS_DIR = '/home/hinahin/PycharmProjects/Pandas_grade_analyse/exam_results/'


def count_students(course_name: str, w_driver):
    course_url = 'https://courses.openedu.ru/courses/course-v1:urfu+{}/instructor#view-course_info'.format(
        course_name)
    w_driver.get(course_url)
    count = w_driver.find_element_by_xpath('//*[@id="course_info"]/div[1]/table/tbody/tr[5]/td/strong').text
    driver.get('https://openedu.ru/')
    return course_name + ';' + count + ';' + str(datetime.date.today())


def grade_download(course_name: str, w_driver):
    course_url = 'https://courses.openedu.ru/courses/course-v1:urfu+{}/instructor#view-data_download'.format(
        course_name)
    w_driver.get(course_url)
    w_driver.execute_script("window.scrollTo(0,1200)")
    WebDriverWait(w_driver, 30000).until(expected_conditions.presence_of_element_located(
        (By.CLASS_NAME, "file-download-link")))

    # Поиск строки, где есть grade report
    file_list = w_driver.find_elements_by_class_name('file-download-link')
    # logger.info(course_name)
    flag = 1
    for i in file_list:
        if 'grade_report' in i.text:
            w_driver.find_element_by_link_text(i.text).click()
            flag -= 1
            # logger.info(i.text)
        break
    if flag == 1:
        logger.info('Нет выгрузки Grade Report для курса: ' + course_name)

    w_driver.get('https://openedu.ru/')


def exam_results_download(course_name: str, w_driver):
    course_url = 'https://courses.openedu.ru/courses/course-v1:urfu+{}/instructor#view-data_download'.format(
        course_name)
    w_driver.get(course_url)
    w_driver.execute_script("window.scrollTo(0,1200)")
    WebDriverWait(w_driver, 30000).until(expected_conditions.presence_of_element_located(
        (By.CLASS_NAME, "file-download-link")))
    # Поиск строки, где есть exam results
    file_list = w_driver.find_elements_by_class_name('file-download-link')
    # logger.info(course_name)
    flag = 1
    for i in file_list:
        if 'exam_results_report' in i.text:
            w_driver.find_element_by_link_text(i.text).click()
            flag -= 1
            # logger.info(i.text)
        break
    if flag == 1:
        logger.info('Нет выгрузки Exam Results для курса: ' + course_name)

    w_driver.get('https://openedu.ru/')


def grade_order(course_name: str, w_driver: webdriver.Firefox):
    course_url = 'https://courses.openedu.ru/courses/course-v1:urfu+{}/instructor#view-data_download'.format(
        course_name)
    w_driver.get(course_url)
    w_driver.execute_script("window.scrollTo(0,1200)")
    WebDriverWait(w_driver, 30000).until(expected_conditions.presence_of_element_located(
        (By.CLASS_NAME, "file-download-link")))
    logger.info('Заказан отчет по курсу: ' + course_name)
    w_driver.find_element_by_css_selector("input.async-report-btn:nth-child(1)").click()
    logger.info('Заказан отчет по курсу: ' + course_name)
    WebDriverWait(w_driver, 30000).until(lambda x: expected_conditions.visibility_of_element_located(
        (By.CSS_SELECTOR, "#report-request-response")) or expected_conditions.visibility_of_element_located(
        (By.CSS_SELECTOR, "#report-request-response-error")))  # Проверка двух условий работает только через lambda
    w_driver.get('https://openedu.ru/')


def order_exam_results(course_name: str, w_driver):
    course_url = 'https://courses.openedu.ru/courses/course-v1:urfu+{}/instructor#view-data_download'.format(
        course_name)
    w_driver.get(course_url)
    w_driver.execute_script("window.scrollTo(0,1200)")
    WebDriverWait(w_driver, 30000).until(expected_conditions.presence_of_element_located(
        (By.CLASS_NAME, "file-download-link")))
    w_driver.execute_script("window.scrollTo(0,500)")
    try:
        w_driver.find_element_by_css_selector(
            ".reports-download-container > p:nth-child(10) > input:nth-child(1)").click()
        WebDriverWait(w_driver, 30000).until(lambda x: expected_conditions.visibility_of_element_located(
            (By.CSS_SELECTOR, "#report-request-response")) or expected_conditions.visibility_of_element_located(
            (By.CSS_SELECTOR, "#report-request-response-error")))  # Проверка двух условий работает только через lambda
    except NoSuchElementException:
        print("Нет наблюдаемых испытаний на курсе - " + course_name)
    w_driver.get('https://openedu.ru/')


list_courses = ['ARCHC+fall_2020',
                'ARCHC+fall_2020_net',
                'BIOECO+fall_2020',
                'CALC+fall_2020',
                'CELLBIO+fall_2020',
                'CHEMSO+fall_2020',
                'chryso+fall_2020',
                'Crithink+fall_2020',
                'CSHARP+fall_2020',
                'DATAINF+fall_2020',
                'DesignBasics+fall_2020',
                'ECOEFF+fall_2020',
                'ECOS+fall_2020',
                'EDUBASE+fall_2020',
                'EDUBASE+fall_2020_net',
                'EFFSOLUTION+fall_2020',
                'ELB+fall_2020',
                'ELB+fall_2020_net',
                'ELECD+fall_2020',
                'engforinclusb+fall_2020',
                'ENGM+fall_2020',
                'GEOM+fall_2020',
                'GEOM+fall_2020_net',
                'GOVBUSINESS+fall_2020',
                'HIST_VIEW+fall_2020',
                'HIST+fall_2020',
                'Inclus_M1+fall_2020',
                'Inclus_M2+fall_2020',
                'INFENG+fall_2020',
                'INTPR+fall_2020',
                'INTPR+fall_2020_net',
                'INTROBE+fall_2020',
                'ITS+fall_2020',
                'LEGAL+fall_2020',
                'LifeSafety+fall_2020',
                'LifeSafety+fall_2020_net',
                'LineAlg+fall_2020',
                'MANEGEMACH+fall_2020',
                'MCS+fall_2020',
                'METHODS+fall_2020',
                'METR+fall_2020',
                'METR+fall_2020_net',
                'NUCMED+fall_2020',
                'NATCULT+fall_2020',
                'PersonalSafety+fall_2020',
                'PHILOSOPHY+fall_2020',
                'PHILS+fall_2020',
                'PHILS+fall_2020_net',
                'PHILSCI+fall_2020',
                'PHILSCI+fall_2020_net',
                'PhysCult+fall_2020',
                'PRGRMM+fall_2020',
                'PROJ+fall_2020',
                'PSYMEDIA+fall_2020',
                'PSYMEDIA+fall_2020_net',
                'PYDNN+fall_2020',
                'PYAP+fall_2020',
                'RUBSCULT+fall_2020',
                'RUBSCULT+fall_2020_net',
                'SIGPROC+fall_2020',
                'SMNGM+fall_2020',
                'SMNGM+fall_2020_net',
                'SoftSkills+fall_2020',
                'SYSTENG+fall_2020',
                'TECO+fall_2020',
                'TECO+fall_2020_net',
                'TELECOM+fall_2020',
                'TEPL+fall_2020',
                'TheorVer+fall_2020',
                'TRIZ+fall_2020',
                ]

# Подготовка и запуск драйвера
login_url = 'https://sso.openedu.ru/login/'

profile = webdriver.FirefoxProfile()
# Установка директории для скачивания
profile.set_preference('browser.download.folderList', 2)
profile.set_preference("browser.download.dir", GRADE_REPORTS_DIR)
# profile.set_preference("browser.download.dir", EXAM_RESULTS_DIR)
profile.set_preference('browser.download.manager.showWhenStarting', False)
profile.set_preference('browser.helperApps.neverAsk.saveToDisk', 'text/csv')

driver = webdriver.Firefox(profile)

# Авторизация на сайте openedu.ru

driver.get(login_url)
driver.set_window_size(1920, 1015)
WebDriverWait(driver, 30000).until(expected_conditions.presence_of_element_located((By.ID, 'id_password')))
driver.find_element_by_id('id_username').send_keys(USERNAME)
driver.find_element_by_id('id_password').send_keys(PASSWORD)
driver.find_element_by_id('id_password').send_keys(Keys.ENTER)
WebDriverWait(driver, 30000).until(expected_conditions.presence_of_element_located((By.CLASS_NAME,
                                                                                    'dropdown-login__text')))

# Цикл загрузки результатов обучения

for course in list_courses:
    # grade_order(course, driver)  # Заказ отчета
    # order_exam_results(course, driver)  # Заказ отчета наблюдаемых испытаний
    grade_download(course, driver)      # Скачивание grade report
    # exam_results_download(course, driver)  # Скачивание отчета наблюдаемых испытаний

driver.close()
