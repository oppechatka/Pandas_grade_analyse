from loguru import logger
import datetime
import grade_settings as GS
import pandas as pnd
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from datetime import date, timedelta
import time

def count_students(course_name: str, w_driver):
    """
    Функция переходит на страницу "Преподаватель" внутри курса и считывает общее число записанных пользователей
    В качестве результата возвращается строка для дальнейшей вставки в csv файл

    :param course_name: Шифр курса (прим. ARCHC+fall_2020)
    :param w_driver: WebDriver с которого ведется работа
    :return: Строка для добавления в csv файл
    """
    course_url = f'https://courses.openedu.ru/courses/course-v1:urfu+{course_name}/instructor#view-course_info'
    w_driver.get(course_url)
    count = w_driver.find_element_by_xpath('//*[@id="course_info"]/div[1]/table/tbody/tr[5]/td/strong').text
    csv_string = course_name + ';' + count + ';' + str(datetime.date.today())
    w_driver.get('https://openedu.ru/')
    return csv_string


def grade_download(course_name: str, w_driver):
    """
    Функция переходит на страницу "Преподаватель", подраздел "Скачивание данных". Прокручивает страницу до
    таблицы с выгрузками и ожидает ее загрузки. Затем находит все элементы с классом "file-download-link", и
    записывает их в список.

    Проходим циклом по списку отсекая расширенные отчеты с содержанием слова Problem и скачиваем первый сверху
    отчет Grade Report. Если дата не является сегодняшней, то файл скачает, но выведется предупреждение, что файл
    не является актуальным.

    Если отчета Grade Report нет в списке, то выводится предупреждение "Нет отчета Grade Report"

    :param course_name: Шифр курса (прим. ARCHC+fall_2020)
    :param w_driver: WebDriver с которого ведется работа
    """
    course_url = f'https://courses.openedu.ru/courses/course-v1:urfu+{course_name}/instructor#view-data_download'
    TDAY = str(datetime.date.today().strftime('%d.%m.%Y'))  # сегодняшняя дата для сравнения

    w_driver.get(course_url)
    w_driver.execute_script("window.scrollTo(0,1200)")
    WebDriverWait(w_driver, 30000).until(expected_conditions.presence_of_element_located(
        (By.CLASS_NAME, "file-download-link")))

    # Поиск строки, где есть grade report
    file_list = w_driver.find_elements_by_class_name('file-download-link')
    flag = 1
    for i in file_list:
        if 'problem' in i.text:
            continue
        elif 'grade_report' in i.text:
            grade_date_list = i.text.split(sep='_')[-1].split(sep='-')[2::-1]  # получаем дату отчета из имени файла
            grade_date = '.'.join(grade_date_list)                             # дата скачиваемого Grade Report

            if TDAY != grade_date:
                logger.warning(f'Дата скачиваемого отчета Grade_Report для курса'
                               f' {course_name} не является актуальной')       # дата не актуальная

            w_driver.find_element_by_link_text(i.text).click()
            flag -= 1
            logger.info(i.text)
            break
    if flag == 1:
        logger.warning('Нет отчета Grade Report для курса: ' + course_name)

    w_driver.get('https://openedu.ru/')


def exam_results_download(course_name: str, w_driver):
    """
    Функция переходит на страницу "Преподаватель", подраздел "Скачивание данных". Прокручивает страницу до
    таблицы с выгрузками и ожидает ее загрузки. Затем находит все элементы с классом "file-download-link", и
    записывает их в список.

    Проходим циклом по списку и скачиваем первый сверху отчет Exam Results. Если дата не является сегодняшней,
    то файл скачает, но выведется предупреждение, что файл не является актуальным.
    Если отчета Exam_Results нет в списке, то выводится предупреждение "Нет отчета Exam Results"

    :param course_name: Шифр курса (прим. ARCHC+fall_2020)
    :param w_driver: WebDriver с которого ведется работа
    """
    course_url = f'https://courses.openedu.ru/courses/course-v1:urfu+{course_name}/instructor#view-data_download'
    TDAY = str(datetime.date.today().strftime('%d.%m.%Y'))  # сегодняшняя дата для сравнения

    w_driver.get(course_url)
    w_driver.execute_script("window.scrollTo(0,1200)")
    WebDriverWait(w_driver, 30000).until(expected_conditions.presence_of_element_located(
        (By.CLASS_NAME, "file-download-link")))

    # Поиск строки, где есть exam results
    file_list = w_driver.find_elements_by_class_name('file-download-link')
    flag = 1
    for i in file_list:
        if 'exam_results_report' in i.text:
            grade_date_list = i.text.split(sep='_')[-1].split(sep='-')[2::-1]  # получаем дату отчета из имени файла
            grade_date = '.'.join(grade_date_list)                             # дата скачиваемого Exam Results

            if TDAY != grade_date:
                logger.warning(f'Дата скачиваемого отчета Exam_Results для курса'
                               f' {course_name} не является актуальной')  # дата не актуальная

            w_driver.find_element_by_link_text(i.text).click()
            flag -= 1
            logger.info(i.text)
            break
    if flag == 1:
        logger.warning('Нет отчета Exam Results для курса: ' + course_name)

    w_driver.get('https://openedu.ru/')


def grade_order(course_name: str, w_driver):
    """
    Функция переходит на страницу "Преподаватель", подраздел "Скачивание данных". Прокручивает страницу до
    таблицы с выгрузками и ожидает ее загрузки. Затем нажимает на клавишу "Создать оценочный лист", ожидает появления
    сообщения о том, что заказ принят или ошибку и переходит на главную страницу портала

    :param course_name: Шифр курса (прим. ARCHC+fall_2020)
    :param w_driver: WebDriver с которого ведется работа
    """
    course_url = f'https://courses.openedu.ru/courses/course-v1:urfu+{course_name}/instructor#view-data_download'
    w_driver.get(course_url)
    w_driver.execute_script("window.scrollTo(0,1200)")
    WebDriverWait(w_driver, 30000).until(expected_conditions.presence_of_element_located(
        (By.CLASS_NAME, "file-download-link")))
    w_driver.find_element_by_css_selector("input.async-report-btn:nth-child(1)").click()
    logger.info('Заказан отчет по курсу: ' + course_name)
    WebDriverWait(w_driver, 30000).until(lambda x: expected_conditions.visibility_of_element_located(
        (By.CSS_SELECTOR, "#report-request-response")) or expected_conditions.visibility_of_element_located(
        (By.CSS_SELECTOR, "#report-request-response-error")))  # Проверка двух условий работает только через lambda
    w_driver.get('https://openedu.ru/')


def order_exam_results(course_name: str, w_driver):
    """
    Функция переходит на страницу "Преподаватель", подраздел "Скачивание данных". Прокручивает страницу до
    таблицы с выгрузками и ожидает ее загрузки. Затем нажимает на клавишу
    "Создать отчёт о результатах наблюдаемого испытания", ожидает появления сообщения о том, что заказ принят
    или ошибку и переходит на главную страницу портала.

    :param course_name: Шифр курса (прим. ARCHC+fall_2020)
    :param w_driver: WebDriver с которого ведется работа
    """
    course_url = f'https://courses.openedu.ru/courses/course-v1:urfu+{course_name}/instructor#view-data_download'
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


def make_web_driver(type_driver: str = 'none'):
    """
    Функция создает и возвращает WebDriver для вызываемой задачи с указанным типом,
    чтобы не комментировать строки с настройками.

    :param type_driver: Тип WebDriver для установки директории скачивания
    :return: WebDriver
    """
    profile = webdriver.FirefoxProfile()

    # Установка директории для скачивания
    profile.set_preference('browser.download.folderList', 2)

    if type_driver == 'grade_report':
        profile.set_preference("browser.download.dir", GS.GRADE_REPORTS_DIR)
    elif type_driver == 'exam_results':
        profile.set_preference("browser.download.dir", GS.EXAM_RESULTS_DIR)
    else:
        profile.set_preference("browser.download.dir", GS.DEFAULT_DOWNLOAD_DIR)

    profile.set_preference('browser.download.manager.showWhenStarting', False)
    profile.set_preference('browser.helperApps.neverAsk.saveToDisk', 'text/csv')
    driver = webdriver.Firefox(profile)

    return driver


def login(web_driver):
    """
    Функция принимает в качестве параметра настроенный WebDriver и проводит авторизацию на портале openedu.ru

    :param web_driver:  WebDriver с которого ведется работа
    """
    # Авторизация на сайте openedu.ru
    web_driver.get('https://sso.openedu.ru/login/')
    web_driver.set_window_size(1920, 1015)
    WebDriverWait(web_driver, 30000).until(expected_conditions.presence_of_element_located((By.ID, 'id_password')))
    web_driver.find_element_by_id('id_username').send_keys(GS.USERNAME)
    web_driver.find_element_by_id('id_password').send_keys(GS.PASSWORD)
    web_driver.find_element_by_id('id_password').send_keys(Keys.ENTER)
    WebDriverWait(web_driver, 30000).until(expected_conditions.presence_of_element_located((By.CLASS_NAME,
                                                                                            'dropdown-login__text')))


def make_grade_report_order():
    """
    Функция создает WebDriver с настрйоками для заказа отчета Grade report, проходит по списку курсов и в каждом
    из них нажимает на клавишу "Создать отчет" с помощью функции grade_order. Затем
    завершает работу WebDriver.
    """
    driver = make_web_driver()
    login(driver)
    for course in GS.LIST_COURSES:
        grade_order(course, driver)
    driver.close()


def make_exam_results_order():
    """
    Функция создает WebDriver с настрйоками для заказа отчета Grade report, проходит по списку курсов и в каждом
    из них нажимает на клавишу "Создать отчет наблюдаемых испытаний" с помощью функции order_exam_results. Затем
    завершает работу WebDriver.
    """
    driver = make_web_driver()
    login(driver)
    for course in GS.LIST_COURSES:
        order_exam_results(course, driver)
    driver.close()


def download_grade_report():
    """
    Функция создает WebDriver с настрйоками для скачивания отчета Grade report, проходит по списку курсов и в каждом
    из них пытается скачать Grade Report с помощью функции grade_download. Затем завершает работу WebDriver.
    """
    driver = make_web_driver('grade_report')
    login(driver)
    for course in GS.LIST_COURSES:
        grade_download(course, driver)
    driver.close()


def download_exam_results():
    """
    Функция создает WebDriver с настрйоками для скачивания отчета Exam Results, проходит по списку курсов и в каждом
    из них пытается скачать отчет Exam Results с помощью функции exam_results_download.
    Затем завершает работу WebDriver.
    """
    driver = make_web_driver('exam_results')
    login(driver)
    for course in GS.LIST_COURSES:
        exam_results_download(course, driver)
    driver.close()


def change_deadlines(course_name: str, email: str, deadline: str):
    driver = make_web_driver()
    login(driver)
    course_url = f'https://courses.openedu.ru/courses/course-v1:urfu+{course_name}/instructor#view-extensions'
    driver.get(course_url)
    driver.set_window_size(1920, 1022)

    driver.find_element(By.NAME, "student").send_keys(email)
    driver.find_element(By.NAME, "due_datetime").send_keys(deadline)

    css_selector = '#set-extension > p:nth-child(4) > select:nth-child(1) > option'
    task_list = driver.find_elements_by_css_selector(css_selector)

    for task in task_list:
        if 'Выберите один' in task.text or\
                'Итогов' in task.text or\
                'команда курса' in task.text or\
                'Эссе' in task.text:
            logger.info(f'Не было включено в обработку задание \"{task.text}\" для пользователя \"{email}\"')
            continue
        else:
            task.click()
            driver.find_element(By.NAME, "change-due-date").click()
            WebDriverWait(driver, 2000).until(
                expected_conditions.visibility_of_element_located((By.CSS_SELECTOR, '#set-extension > p:nth-child(7)')))
    driver.close()

def change_scores(file):
    df = pnd.read_excel('./scores/Book1.xlsx', sheet_name=0)
    df = df.sort_values(by='course')
    print(df)
    driver = make_web_driver()
    login(driver)

    for i in range(len(df) - 1):
        score = df.at[i, 'scores']
        logname = df.at[i, 'logname']
        block = df.at[i, 'block']
        course_name = df.at[i, 'course']
        print(score, logname, block, course_name)
        course_url = f'https://courses.openedu.ru/courses/course-v1:urfu+{course_name}/instructor#view-student_admin'
        driver.get(course_url)
        driver.set_window_size(1920, 1022)

        WebDriverWait(driver, 2000).until(
            expected_conditions.visibility_of_element_located((By.CSS_SELECTOR, '#set-extension > p:nth-child(7)')))
        driver.find_element(By.NAME, "score-select-single").send_keys(score)
        driver.find_element(By.NAME, "student-select-grade").send_keys(logname)
        driver.find_element(By.NAME, "problem-select-single").send_keys(block)
        driver.find_element(By.NAME, "override-problem-score-single").click()

    driver.close()

def date_open(txt: str):
    i_month, i_day, i_year = txt.split('/')
    p = date(int(i_year), int(i_month), int(i_day)) - timedelta(days=161)
    return p.strftime('%m/%d/%Y')


def datetostr(txt: str):
    i_month, i_day, i_year = txt.split('/')
    p = date(int(i_year), int(i_month), int(i_day))
    return p.strftime('%d.%m.%Y')


def todate(txt: str):
    i_month, i_day, i_year = txt.split('/')
    p = date(int(i_year), int(i_month), int(i_day))
    return p

def get_struct(course_name: str):
    driver = make_web_driver()
    login(driver)
    driver.set_window_size(1920, 800)
    course_url = f'https://studio.openedu.ru/course/course-v1:urfu+{course_name}'
    driver.get(course_url)
    WebDriverWait(driver, 30).until(expected_conditions.invisibility_of_element((By.CLASS_NAME, 'ui-loading')))

    # Находим все элементы разделов и меняем им дату открытия
    section_list = driver.find_elements_by_class_name('outline-section')
    ids_sections = [subsection.get_attribute('Id') for subsection in section_list]

    logger.info('Разделы')

    for idd in ids_sections:
        driver.implicitly_wait(10)

        # открытие настроек раздела
        driver.find_element_by_id(idd).find_element_by_class_name('configure-button').click()

        # увеличение даты на определенное кол-во дней - для постепенного открытия материалов

        # проверка даты открытия на случай сбоя - может часть уже поменяли и трогать дату не надо
        if todate(driver.find_element_by_xpath('//*[ @ id = "start_date"]').get_attribute('value')) >= todate(
                '09/06/2021'):
            # print(datetostr(driver.find_element_by_xpath('//*[ @ id = "start_date"]').get_attribute(
            #     'value')) + ";" + driver.find_element_by_xpath('//*[ @ id="modal-window-title"]').text)
            # print("<tr><td>" + datetostr(driver.find_element_by_xpath('//*[ @ id = "start_date"]').get_attribute(
            #     'value')) + "</td><td>" + driver.find_element_by_xpath('//*[ @ id="modal-window-title"]').text + "</td></tr>")

            # лог для быстрой правки html графика открытия материалов
            print("<tr><th colspan=2>" + driver.find_element_by_xpath(
                '//*[ @ id="modal-window-title"]').text + "</th></tr>")
            driver.find_element_by_css_selector('.action-cancel').click()
        else:
            new_date = date_open(driver.find_element_by_xpath('//*[ @ id = "start_date"]').get_attribute('value'))
            # print(datetostr(new_date) + ";" + driver.find_element_by_xpath('//*[ @ id="modal-window-title"]').text)
            print("<tr><th colspan=2>" + driver.find_element_by_xpath(
                '//*[ @ id="modal-window-title"]').text + "</th></tr>")
            # print("<tr><td>" + datetostr(new_date) + '</td><td>' + driver.find_element_by_xpath('//*[ @ id="modal-window-title"]').text + "</td></tr>")
            driver.find_element_by_xpath('//*[ @ id = "start_date"]').clear()
            driver.find_element_by_xpath('//*[ @ id = "start_date"]').send_keys(new_date)
            driver.find_element_by_xpath('//*[ @ id = "start_time"]').clear()
            driver.find_element_by_xpath('//*[ @ id = "start_time"]').send_keys('00:00')
            driver.find_element_by_xpath('//*[ @ id = "start_time"]').click()
            driver.find_element_by_class_name('modal-section-title').click()
            driver.find_element_by_css_selector('.action-save').click()
        time.sleep(2)  # ожидание 2 секунды, чтобы прогрузилось

        #  ИЛИ   открыть все сразу
        # driver.find_element_by_xpath('//*[ @ id = "start_date"]').clear()
        # driver.find_element_by_xpath('//*[ @ id = "start_date"]').send_keys('30/06/2021')
        # driver.find_element_by_xpath('//*[ @ id = "start_time"]').clear()
        # driver.find_element_by_xpath('//*[ @ id = "start_time"]').send_keys('23:00')
        # # driver.find_element_by_xpath('//*[ @ id = "start_time"]').click()
        # driver.find_element_by_class_name('modal-section-title').click()
        # driver.find_element_by_css_selector('.action-save').click()
        # time.sleep(2)

    # Находим все элементы подразделов и меняем им дату открытия. Заодно раскрываем списки
    # driver.refresh()
    subsection_list = driver.find_elements_by_class_name('outline-subsection')
    ids_subsections = [subsection.get_attribute('Id') for subsection in subsection_list]

    logger.info('Подразделы')

    for idd in ids_subsections:
        driver.implicitly_wait(10)
        driver.find_element_by_id(idd).find_element_by_class_name('configure-button').click()

        # постепенное открытие материалов по графику с проверкой сбоя скрипта - измененные даты не трогает
        if todate(driver.find_element_by_xpath('//*[ @ id = "start_date"]').get_attribute('value')) >= todate(
                '09/06/2021'):
            print("<tr><td>" + datetostr(driver.find_element_by_xpath('//*[ @ id = "start_date"]').get_attribute(
                'value')) + "</td><td>" + driver.find_element_by_xpath(
                '//*[ @ id="modal-window-title"]').text + "</td></tr>")
            driver.find_element_by_css_selector('.action-cancel').click()
        else:
            new_date = date_open(driver.find_element_by_xpath('//*[ @ id = "start_date"]').get_attribute('value'))
            print("<tr><td>" + datetostr(new_date) + "</td><td>" + driver.find_element_by_xpath(
                '//*[ @ id="modal-window-title"]').text + "</td></tr>")
            driver.find_element_by_xpath('//*[ @ id = "start_date"]').clear()
            driver.find_element_by_xpath('//*[ @ id = "start_date"]').send_keys(new_date)
            driver.find_element_by_xpath('//*[ @ id = "start_time"]').clear()
            driver.find_element_by_xpath('//*[ @ id = "start_time"]').send_keys('00:00')
            driver.find_element_by_class_name('modal-section-title').click()
            time.sleep(1)

            # сброс всех дат на дефолтную дату открытия курса
            # driver.find_element_by_xpath('//*[ @ id = "due_date"]').clear()
            # driver.find_element_by_xpath('//*[ @ id = "due_time"]').clear()
            # driver.find_element_by_class_name('modal-section-title').click()
            # time.sleep(1)
            # driver.find_element_by_css_selector('.action-save').click()

        # ИЛИ открыть все сразу
        # driver.find_element_by_xpath('//*[ @ id = "start_date"]').clear()
        # driver.find_element_by_xpath('//*[ @ id = "start_date"]').send_keys('09/06/2021')
        # driver.find_element_by_xpath('//*[ @ id = "start_time"]').clear()
        # driver.find_element_by_xpath('//*[ @ id = "start_time"]').send_keys('00:00')
        # driver.find_element_by_class_name('modal-section-title').click()
        # time.sleep(1)
        # driver.find_element_by_css_selector('.action-save').click()
        # time.sleep(1)

        # открытие содержимого подраздела - для изменения дедлайнов заданий
        driver.find_element_by_id(idd).find_element_by_class_name('fa-caret-down').click()
        time.sleep(1)

    # Находим все элементы тем курса и меняем им дату дедлайна.
    # driver.refresh()
    unit_list = driver.find_elements_by_class_name('outline-unit')
    ids_units = [unit.get_attribute('id') for unit in unit_list]

    for idd in ids_units:
        if len(driver.find_element_by_id(idd).find_elements_by_class_name('status-grading-label')) > 0:
            # driver.implicitly_wait(10)
            driver.find_element_by_id(idd).find_element_by_class_name('configure-button').click()
            driver.find_element_by_xpath('//*[ @ id = "due_date"]').clear()
            driver.find_element_by_xpath('//*[ @ id = "due_date"]').send_keys('01/10/2022')
            driver.find_element_by_xpath('//*[ @ id = "due_time"]').clear()
            driver.find_element_by_xpath('//*[ @ id = "due_time"]').send_keys('23:00')
            driver.find_element_by_class_name('modal-section-title').click()
            time.sleep(1)
            driver.find_element_by_css_selector('.action-save').click()
            time.sleep(2)
        else:
            continue

    # Применяем обновления
    for idd in ids_sections:
        if len(driver.find_element_by_id(idd).find_elements_by_class_name('publish-button')) > 0:
            # driver.implicitly_wait(10)
            driver.find_element_by_id(idd).find_element_by_class_name('publish-button').click()
            btn_name = driver.find_element_by_class_name('action-publish').text
            btn_name = str.capitalize(btn_name)
            driver.find_element_by_link_text(btn_name).click()
            time.sleep(2)

    driver.close()




def change_score (course_name: str, score: str, logname: str, block):   # подставление баллов  по одному слушателю
    driver = make_web_driver()
    login(driver)
    course_url = f'https://courses.openedu.ru/courses/course-v1:urfu+{course_name}/instructor#view-student_admin'
    driver.get(course_url)
    driver.set_window_size(1920, 1022)

    driver.find_element(By.NAME, "score-select-single").send_keys(score)
    driver.find_element(By.NAME, "student-select-grade").send_keys(logname)
    driver.find_element(By.NAME, "problem-select-single").send_keys(block)
    driver.find_element(By.NAME, "override-problem-score-single").click()
    WebDriverWait(driver, 2000).until(
        expected_conditions.visibility_of_element_located((By.CSS_SELECTOR, '#set-extension > p:nth-child(7)')))
    driver.close()



def login_urfu(web_driver):
    """
    Функция принимает в качестве параметра настроенный WebDriver и проводит авторизацию на портале openedu.ru

    :param web_driver:  WebDriver с которого ведется работа
    """
    # Авторизация на сайте openedu.ru
    web_driver.get('https://courses.openedu.urfu.ru/login')
    web_driver.set_window_size(1280, 720)
    WebDriverWait(web_driver, 30000).until(expected_conditions.presence_of_element_located((By.ID, 'login-email')))
    web_driver.find_element_by_id('login-email').send_keys(GS.USERNAME_URFU)
    web_driver.find_element_by_id('login-password').send_keys(GS.PASSWORD_URFU)
    web_driver.find_element_by_id('login-password').send_keys(Keys.ENTER)
    # WebDriverWait(web_driver, 30000).until(expected_conditions.presence_of_element_located((By.CLASS_NAME, 'username')))
    # WebDriverWait(web_driver, 30000).until(expected_conditions.presence_of_element_located((By.XPATH, '//*[@id="navbarDropdown"]')))
    WebDriverWait(web_driver, 30000).until(expected_conditions.presence_of_element_located((By.CLASS_NAME, 'user-image-frame')))

def grade_order_urfu(course_name: str, w_driver):
    """
    Функция переходит на страницу "Преподаватель", подраздел "Скачивание данных". Прокручивает страницу до
    таблицы с выгрузками и ожидает ее загрузки. Затем нажимает на клавишу "Создать оценочный лист", ожидает появления
    сообщения о том, что заказ принят или ошибку и переходит на главную страницу портала

    :param course_name: Шифр курса (прим. ARCHC+fall_2020)
    :param w_driver: WebDriver с которого ведется работа
    """
    print("grade_order_urfu")
    course_url = f'https://courses.openedu.urfu.ru/courses/course-v1:UrFU+{course_name}/instructor#view-data_download'
    w_driver.get(course_url)
    w_driver.execute_script("window.scrollTo(0,1200)")
    WebDriverWait(w_driver, 30000).until(expected_conditions.presence_of_element_located(
        (By.CLASS_NAME, "file-download-link")))
    w_driver.find_element_by_css_selector("input.async-report-btn:nth-child(1)").click()
    logger.info('Заказан отчет по курсу: ' + course_name)
    WebDriverWait(w_driver, 30000).until(lambda x: expected_conditions.visibility_of_element_located(
        (By.CSS_SELECTOR, "#report-request-response")) or expected_conditions.visibility_of_element_located(
        (By.CSS_SELECTOR, "#report-request-response-error")))  # Проверка двух условий работает только через lambda
    w_driver.get('https://courses.openedu.urfu.ru/dashboard')

def make_grade_report_order_urfu():
    """
    Функция создает WebDriver с настройками для заказа отчета Grade report, проходит по списку курсов и в каждом
    из них нажимает на клавишу "Создать отчет" с помощью функции grade_order. Затем
    завершает работу WebDriver.
    """
    print("make_grade_report_order_urfu")
    driver = make_web_driver()
    login_urfu(driver)
    for course in GS.LIST_COURSES_URFU:
        grade_order_urfu(course, driver)
    driver.close()

def make_exam_results_order_urfu():
    """
    Функция создает WebDriver с настрйоками для заказа отчета Grade report, проходит по списку курсов и в каждом
    из них нажимает на клавишу "Создать отчет наблюдаемых испытаний" с помощью функции order_exam_results. Затем
    завершает работу WebDriver.
    """
    driver = make_web_driver()
    login_urfu(driver)
    if driver.find_element_by_class_name('cc-dismiss'):
        driver.find_element_by_class_name('cc-dismiss').click()
    for course in GS.LIST_COURSES_URFU:
        order_exam_results_urfu(course, driver)
    driver.close()

def order_exam_results_urfu(course_name: str, w_driver):
    """
    Функция переходит на страницу "Преподаватель", подраздел "Скачивание данных". Прокручивает страницу до
    таблицы с выгрузками и ожидает ее загрузки. Затем нажимает на клавишу
    "Создать отчёт о результатах наблюдаемого испытания", ожидает появления сообщения о том, что заказ принят
    или ошибку и переходит на главную страницу портала.

    :param course_name: Шифр курса (прим. ARCHC+fall_2020)
    :param w_driver: WebDriver с которого ведется работа
    """
    course_url = f'https://courses.openedu.urfu.ru/courses/course-v1:UrFU+{course_name}/instructor#view-data_download'
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
            (By.CSS_SELECTOR,
                "#report-request-response-error")))  # Проверка двух условий работает только через lambda
    except NoSuchElementException:
        print("Нет наблюдаемых испытаний на курсе - " + course_name)
    w_driver.get('https://courses.openedu.ru/')

if __name__ == '__main__':
    # make_grade_report_order()   # Заказ отчета Grade Report
    # make_exam_results_order()   # Заказ отчета Exam Results
    make_grade_report_order_urfu()    # Заказ отчета с внутренней платформе Grade Report
    # make_exam_results_order_urfu()  # Заказ отчета Exam Results с внутренней платформе
    # download_grade_report()     # Скачивание отчета Grade Report
    # download_exam_results()     # Скачивание отчета Exam Results
    # get_struct('ARCHC+fall_2021')
    # change_deadlines('PHILSCI+fall_2020', 'i.shaikhutdinova@mail.ru', '01/28/2021 23:30')
    # change_score('TRIZ+spring_2021', '0.652', 'nikitamelnikov2', 'block-v1:urfu+TRIZ+spring_2021+type@problem+block@b665b9da521d4b80813aa9f7324aa094')  # Восстановление баллов
    # change_scores('Book1.xlsx')  # Восстановление баллов