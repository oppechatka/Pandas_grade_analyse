import datetime
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import NoSuchElementException

USERNAME = ''
PASSWORD = ''


def grade_folder(function):
    def wrapped(arg1, arg2):
        grade_report_dir = '/home/hinahin/PycharmProjects/Pandas_grade_analyse/grade_reports/'
        arg2.profile.set_preference(profile.set_preference("browser.download.dir", grade_report_dir))
        function(arg1, arg2)

    return wrapped


def count_students(course_name: str, w_driver):
    course_url = 'https://courses.openedu.ru/courses/course-v1:urfu+{}/instructor#view-course_info'.format(
        course_name)
    w_driver.get(course_url)
    count = w_driver.find_element_by_xpath('//*[@id="course_info"]/div[1]/table/tbody/tr[5]/td/strong').text
    driver.get('https://openedu.ru/')
    return course_name + ';' + count + ';' + str(datetime.date.today())


# @grade_folder
def grade_download(course_name: str, w_driver):
    course_url = 'https://courses.openedu.ru/courses/course-v1:urfu+{}/instructor#view-data_download'.format(
        course_name)
    w_driver.get(course_url)
    w_driver.execute_script("window.scrollTo(0,1200)")
    WebDriverWait(w_driver, 30000).until(expected_conditions.presence_of_element_located(
        (By.XPATH, "//*[@id=\"report-downloads-table\"]/div/div[5]/div/div[1]/div/a")))

    # Поиск строки, где есть grade report

    n = 1
    while True:
        text = w_driver.find_element_by_xpath(
            "//*[@id=\"report-downloads-table\"]/div/div[5]/div/div[{}]/div/a".format(n)).text
        if 'grade_report' in text:
            w_driver.find_element_by_xpath(
                "//*[@id=\"report-downloads-table\"]/div/div[5]/div/div[{}]/div/a".format(n)).click()
            print(text + ' - ' + str(n) + ' в списке')
            break
        elif n < 10:
            n += 1
            continue
        else:
            print('Нет выгрузки Grade Report для курса' + course_name)
            break
    w_driver.get('https://openedu.ru/')


def exam_results_download(course_name: str, w_driver):
    course_url = 'https://courses.openedu.ru/courses/course-v1:urfu+{}/instructor#view-data_download'.format(
        course_name)
    w_driver.get(course_url)
    w_driver.execute_script("window.scrollTo(0,1200)")
    WebDriverWait(w_driver, 30000).until(expected_conditions.presence_of_element_located(
        (By.XPATH, "//*[@id=\"report-downloads-table\"]/div/div[5]/div/div[1]/div/a")))

    # Поиск строки, где есть grade report

    n = 1
    while True:
        text = w_driver.find_element_by_xpath(
            "//*[@id=\"report-downloads-table\"]/div/div[5]/div/div[{}]/div/a".format(n)).text
        if 'exam_results_report' in text:
            w_driver.find_element_by_xpath(
                "//*[@id=\"report-downloads-table\"]/div/div[5]/div/div[{}]/div/a".format(n)).click()
            print(text + ' - ' + str(n) + ' в списке')
            break
        elif n < 10:
            n += 1
            continue
        else:
            print('Нет выгрузки Exam Results для курса' + course_name)
            break
    w_driver.get('https://openedu.ru/')


def grade_order(course_name: str, w_driver):
    course_url = 'https://courses.openedu.ru/courses/course-v1:urfu+{}/instructor#view-data_download'.format(
        course_name)
    w_driver.get(course_url)
    w_driver.execute_script("window.scrollTo(0,1200)")
    WebDriverWait(w_driver, 30000).until(expected_conditions.presence_of_element_located(
        (By.XPATH, "//*[@id=\"report-downloads-table\"]/div/div[5]/div/div[1]/div/a")))
    w_driver.find_element_by_css_selector("input.async-report-btn:nth-child(1)").click()
    WebDriverWait(w_driver, 30000).until(expected_conditions.visibility_of_element_located(
        (By.XPATH, '//*[@id="report-request-response"]')))
    w_driver.get('https://openedu.ru/')


def order_exam_results(course_name: str, w_driver):
    course_url = 'https://courses.openedu.ru/courses/course-v1:urfu+{}/instructor#view-data_download'.format(
        course_name)
    w_driver.get(course_url)
    w_driver.execute_script("window.scrollTo(0,1200)")
    WebDriverWait(w_driver, 30000).until(expected_conditions.presence_of_element_located(
        (By.XPATH, "//*[@id=\"report-downloads-table\"]/div/div[5]/div/div[1]/div/a")))
    w_driver.execute_script("window.scrollTo(0,500)")
    try:
        w_driver.find_element_by_css_selector(
            ".reports-download-container > p:nth-child(10) > input:nth-child(1)").click()
        WebDriverWait(w_driver, 30000).until(expected_conditions.presence_of_element_located(
            (By.XPATH, '//*[@id="report-request-response"]')))
    except NoSuchElementException:
        print("Нет наблюдаемых испытаний на курсе -" + course_name)
    w_driver.get('https://openedu.ru/')


list_courses = ['PROJ+spring_2020',
                'METR+spring_2020',
                'METR+spring_2020_net',
                'GEOM+spring_2020',
                'ELECD+spring_2020',
                'ELECD+spring_2020_net',
                'TRIZ+spring_2020',
                'TRIZ+spring_2020_net',
                'CALC+spring_2020',
                'CALC+spring_2020_net',
                'DATAINF+spring_2020_net',
                'DATAINF+spring_2020',
                'TELECOM+spring_2020',
                'TELECOM+spring_2020_net',
                'Inclus_M1+spring_2020',
                'Inclus_M1+spring_2020_net',
                'METHODS+spring_2020',
                'BIOECO+spring_2020',
                'BIOECO+spring_2020_net',
                'SIGPROC+spring_2020',
                'EDUBASE+spring_2020',
                'EDUBASE+spring_2020_net',
                'INTPR+spring_2020',
                'INTPR+spring_2020_net',
                'LEGAL+spring_2020',
                'CELLBIO+spring_2020',
                'CELLBIO+spring_2020_net',
                'MCS+spring_2020',
                'MCS+spring_2020_net',
                'LifeSafety+spring_2020',
                'LifeSafety+spring_2020_net',
                'ITS+spring_2020',
                'PSYMEDIA+spring_2020',
                'PSYMEDIA+spring_2020_net',
                'CHEMSO+spring_2020',
                'CHEMSO+spring_2020_net',
                'INTROBE+spring_2020',
                'INTROBE+spring_2020_net',
                'ENGM+spring_2020',
                'ENGM+spring_2020_net',
                'INFENG+spring_2020',
                'HIST+spring_2020',
                'HIST+spring_2020_net',
                'RUBSCULT+spring_2020',
                'RUBSCULT+spring_2020_net',
                'ARCHC+spring_2020',
                'ARCHC+spring_2020_net',
                'DesignBasics+spring_2020',
                'DesignBasics+spring_2020_net',
                'ECOEFF+spring_2020',
                'ECOEFF+spring_2020_net',
                'ELB+spring_2020',
                'ELB+spring_2020_net',
                'SYSTENG+spring_2020',
                'SYSTENG+spring_2020_net',
                'CSHARP+spring_2020',
                'CSHARP+spring_2020_net',
                'Inclus_M2+spring_2020',
                'Inclus_M2+spring_2020_net',
                'SMNGM+spring_2020',
                'SMNGM+spring_2020_net',
                'ECOS+spring_2020',
                'ECOS+spring_2020_net',
                'TEPL+spring_2020',
                'TEPL+spring_2020_net',
                'PRGRMM+spring_2020',
                'PRGRMM+spring_2020_net',
                'TECO+spring_2020',
                'TECO+spring_2020_net',
                'MANEGEMACH+spring_2020',
                'EFFSOLUTION+spring_2020',
                'NUCMED+spring_2020',
                'NUCMED+spring_2020_net',
                'HIST_VIEW+spring_2020_net',
                'HIST_VIEW+spring_2020',
                'PersonalSafety+spring_2020',
                'PersonalSafety+spring_2020_net',
                'Crithink+spring_2020',
                'Crithink+spring_2020_net',
                'PHILOSOPHY+spring_2020',
                'PHILOSOPHY+spring_2020_net',
                'PHILS+spring_2020',
                'PHILSCI+spring_2020',
                'PHILSCI+spring_2020_net',
                ]

# Подготовка и запуск драйвера
login_url = 'https://sso.openedu.ru/login/'

profile = webdriver.FirefoxProfile()
# Установка директории для скачивания
profile.set_preference('browser.download.folderList', 2)
profile.set_preference("browser.download.dir", '/home/hinahin/PycharmProjects/Pandas_grade_analyse/grade_reports/')
# profile.set_preference("browser.download.dir", '/home/hinahin/PycharmProjects/Pandas_grade_analyse/exam_results/')
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
