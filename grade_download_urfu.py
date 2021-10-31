from loguru import logger
import datetime
import time
import grade_settings as GS
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
import pandas as pd
import glob, os
import analyse
import grade_settings as gs

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


def grade_download_urfu(course_name: str, w_driver):
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
    course_url = f'https://courses.openedu.urfu.ru/courses/course-v1:UrFU+{course_name}/instructor#view-data_download'
    TDAY = str(datetime.date.today().strftime('%d.%m.%Y'))  # сегодняшняя дата для сравнения

    w_driver.get(course_url)
    w_driver.execute_script("window.scrollTo(0,1200)")
    WebDriverWait(w_driver, 30).until(expected_conditions.presence_of_element_located(
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

    w_driver.get('https://courses.openedu.urfu.ru/dashboard')


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
    course_url = f'https://courses.openedu.urfu.ru/courses/course-v1:UrFU+{course_name}/instructor#view-data_download'
    w_driver.get(course_url)
    time.sleep(2)
    w_driver.execute_script("window.scrollTo(0,1200)")
    WebDriverWait(w_driver, 30).until(expected_conditions.presence_of_element_located(
        (By.CLASS_NAME, "file-download-link")))
    w_driver.find_element_by_css_selector("input.async-report-btn:nth-child(1)").click()
    time.sleep(1)
    logger.info('Заказан отчет по курсу: ' + course_name)
    WebDriverWait(w_driver, 30).until(lambda x: expected_conditions.visibility_of_element_located(
        (By.CSS_SELECTOR, "#report-request-response")) or expected_conditions.visibility_of_element_located(
        (By.CSS_SELECTOR, "#report-request-response-error")))  # Проверка двух условий работает только через lambda
    w_driver.get('https://courses.openedu.urfu.ru/dashboard')


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
    WebDriverWait(w_driver, 30).until(expected_conditions.presence_of_element_located(
        (By.CLASS_NAME, "file-download-link")))
    w_driver.execute_script("window.scrollTo(0,500)")
    try:
        w_driver.find_element_by_css_selector(
            ".reports-download-container > p:nth-child(10) > input:nth-child(1)").click()
        WebDriverWait(w_driver, 30).until(lambda x: expected_conditions.visibility_of_element_located(
            (By.CSS_SELECTOR, "#report-request-response")) or expected_conditions.visibility_of_element_located(
            (By.CSS_SELECTOR, "#report-request-response-error")))  # Проверка двух условий работает только через lambda
    except NoSuchElementException:
        logger.warning(f"Нет наблюдаемых испытаний на курсе - {course_name}")
    w_driver.get('https://courses.openedu.urfu.ru/dashboard')


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


def login_urfu(web_driver):
    """
    Функция принимает в качестве параметра настроенный WebDriver и проводит авторизацию на портале openedu.ru

    :param web_driver:  WebDriver с которого ведется работа
    """
    # Авторизация на сайте openedu.ru
    web_driver.get('https://courses.openedu.urfu.ru/login')
    web_driver.set_window_size(1920, 1015)
    WebDriverWait(web_driver, 30).until(expected_conditions.presence_of_element_located((By.ID, 'login-email')))
    web_driver.find_element_by_id('login-email').send_keys(GS.USERNAME_URFU)
    web_driver.find_element_by_id('login-password').send_keys(GS.PASSWORD_URFU)
    web_driver.find_element_by_id('login-password').send_keys(Keys.ENTER)
    time.sleep(2)
    WebDriverWait(web_driver, 30).until(expected_conditions.presence_of_element_located((By.CLASS_NAME,
                                                                                            'toggle-user-dropdown')))


def make_grade_report_order():
    """
    Функция создает WebDriver с настрйоками для заказа отчета Grade report, проходит по списку курсов и в каждом
    из них нажимает на клавишу "Создать отчет" с помощью функции grade_order. Затем
    завершает работу WebDriver.
    """
    driver = make_web_driver()
    login_urfu(driver)
    for course in GS.LIST_COURSES_URFU:
        grade_order(course, driver)
    driver.close()


def make_exam_results_order():
    """
    Функция создает WebDriver с настрйоками для заказа отчета Grade report, проходит по списку курсов и в каждом
    из них нажимает на клавишу "Создать отчет наблюдаемых испытаний" с помощью функции order_exam_results. Затем
    завершает работу WebDriver.
    """
    driver = make_web_driver()
    login_urfu(driver)
    for course in GS.LIST_COURSES_URFU:
        order_exam_results_urfu(course, driver)
    driver.close()


def download_grade_report():
    """
    Функция создает WebDriver с настрйоками для скачивания отчета Grade report, проходит по списку курсов и в каждом
    из них пытается скачать Grade Report с помощью функции grade_download. Затем завершает работу WebDriver.
    """
    driver = make_web_driver('grade_report')
    login_urfu(driver)
    for course in GS.LIST_COURSES_URFU:
        grade_download_urfu(course, driver)
    driver.close()


def download_exam_results():
    """
    Функция создает WebDriver с настрйоками для скачивания отчета Exam Results, проходит по списку курсов и в каждом
    из них пытается скачать отчет Exam Results с помощью функции exam_results_download.
    Затем завершает работу WebDriver.
    """
    driver = make_web_driver('exam_results')
    login_urfu(driver)
    for course in GS.LIST_COURSES:
        exam_results_download(course, driver)
    driver.close()

if __name__ == '__main__':
    make_grade_report_order()   # Заказ отчета Grade Report
    # make_exam_results_order()   # Заказ отчета Exam Results
    # download_grade_report()     # Скачивание отчета Grade Report
    # download_exam_results()     # Скачивание отчета Exam Results

    # эксперименты над кроликами панды
    # # df = pd.read_excel("pc.xlsx", index_col="ID_stud_dckey")
    # # df = pd.read_excel("pc.xlsx")
    # df_profile = pd.read_csv("profile.csv", sep=",")
    # df_grade = pd.read_csv("grade.csv", sep=",")
    # df_profile = df_profile.set_index("id")
    # df_grade = df_grade.set_index("Student ID")
    # print(df_profile.columns)
    # print(df_grade.columns)
    # # print(df_profile.head(1))
    # # print(df_grade.head(1))
    # dictStudent = {'username': df_profile['username'], 'email': df_profile['email'], 'name': df_profile['name'], 'grade': df_grade['Grade']}
    # df_student = pd.DataFrame(dictStudent)
    # # print(df_student.head(1))
    # print(df_student.loc[df_student['email']=="Anfisa.Artsybasheva@urfu.me"])

    # # поиск новеньких
    # file = 'physcult.xlsx'
    # # файл запроса
    # df_list = pd.read_excel(gs.REQUESTS_DIRECTORY + '/' + file, sheet_name=1)
    # df_list_course = pd.read_excel(gs.REQUESTS_DIRECTORY + '/' + file, sheet_name=0)
    # session_course = df_list_course.iloc[9, 1]
    # df_list.rename(columns={'Адрес электронной почты': 'Email'}, inplace=True)
    # df_list['Email'].fillna('', inplace=True)
    # df_email = df_list.loc[df_list['Email'] != '']
    # df_email = df_email[['Email']]
    # df_email = df_email.drop_duplicates()
    # df_list = df_list.loc[pd.isna(df_list['login'])]
    # df_list['Отчество'].fillna('', inplace=True)
    # df_list['fio'] = df_list["Фамилия"] + df_list["Имя"] + df_list["Отчество"]
    # df_list['fio'] = df_list['fio'].str.lower()
    # df_list['fio'] = df_list['fio'].str.replace('ё', 'е', regex=False)
    # df_list['fio'] = df_list['fio'].str.replace(' ', '', regex=False)
    # df_list = df_list.drop_duplicates(subset=['fio'], keep=False)
    # df_list = df_list.set_index(['fio'])
    #
    # # подготовка grade report
    # # os.chdir('grade_reports')
    # # print(analyse.get_report_list("grade_reports"))
    # # lst = glob.glob("grade_reports/*PhysCult*_grade_report_*.csv")
    # # lst.sort(reverse=True)
    # # df_grade = pd.read_csv(lst[0], sep=',')
    # df_grade = pd.read_csv(gs.GRADE_REPORTS_DIRECTORY +'/' + analyse.get_grade_report_file(file), sep=',')
    # df_grade['Last Name'].fillna('', inplace=True)
    # df_grade['First Name'].fillna('', inplace=True)
    # df_grade['Second Name'].fillna('', inplace=True)
    # df_grade['fio'] = df_grade['Last Name'] + df_grade['First Name'] + df_grade['Second Name']
    # df_grade['fio'] = df_grade['fio'].str.lower()
    # df_grade['fio'] = df_grade['fio'].str.replace('ё', 'е', regex=False)
    # df_grade['fio'] = df_grade['fio'].str.replace(' ', '', regex=False)
    # df_grade = df_grade.drop_duplicates(subset=['fio'], keep=False)
    # df_grade = df_grade.set_index(['fio'])
    #
    # # слияние
    # # df_grade = df_grade.loc[~df_grade['Email'].isin(df_email['Email'])]
    # df_full = pd.merge(df_list, df_grade[['Student ID','Email','Username','Last Name','First Name','Second Name','Grade percent']], on='fio', how='left')
    # df_full = df_full.loc[pd.isna(df_full['Email_y']) == False]
    # df_full.to_excel(f'{session_course}_result.xlsx', index=False)