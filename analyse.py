from loguru import logger
from datetime import date
from os import listdir
import pandas as pnd
import grade_settings as gs

REQUESTS_FILES = listdir(gs.REQUESTS_DIRECTORY)
GRADE_REPORT_FILES = listdir(gs.GRADE_REPORTS_DIRECTORY)


def get_report_list(directory: str):
    """
    Функция получает на входе строкой директорию, где находятся файлы с отчетами Grade Report, пробегает по всем файлам
    и формирует словарь в виде:

    {шифр курса: "имя файла отчета"}

    Работает только с openedu.ru

    :param directory: путь к директории
    :return: Cловарь, где ключом является шифр курса (прим. ecos_fall2020net ), значение полное имя файла с отчетом
    """
    file_list = listdir(directory)
    dict_file = dict()

    for x in range(len(file_list)):
        file_grade = file_list[x].split(sep="_")
        file_grade = file_grade[1:-3]
        if file_grade[-1] == "net":
            key_str = '_'.join(file_grade[:-3]) + '_' + ''.join(file_grade[-3:])
            dict_file[key_str] = file_list[x]
        else:
            key_str = '_'.join(file_grade[:-2]) + '_' + ''.join(file_grade[-2:])
            dict_file[key_str] = file_list[x]
    return dict_file


def get_columns(list_columns: list):
    """
    Функция получает на вход список всех столбцов в файле отчета Grade Report и сохраняет в новый список
    столбцы с оценками от столбца "Grade" до "Cohort Name"(не включительно). Из списка также исключаются столбцы
    со средними значениями по блокам (Avg) и столбец Grade Percent, который является дублирующим значением
    столбца Grade, умноженный на 100.

    :param list_columns: список всех столбцов в файле отчета Grade Report. Тип - List
    :return: список столбцов всех заданий на курсе, без Avg и Grade Percent
    """
    new_list = list_columns[list_columns.index('Grade'):list_columns.index('Cohort Name')]
    for name in new_list:
        if ('(Avg)' in name) or ("Grade percent" in name):
            new_list.pop(new_list.index(name))
    final_list = ['Email'] + new_list
    return final_list


def get_grade_report_file(request_file: str):
    """
    Функция получает на входе имя файла-запроса из папки Requests, на первом листе файла обращается к ячейке
    с шифром курса, и возвращает соответствующий ему файл отчета Grade Report в одноименной папке

    :param request_file: имя файла запроса из папки Requests
    :return: имя файла отчета Grade Report из которого будут браться оценки для ведомости
    """
    try:
        crs_request_df = pnd.read_excel(gs.REQUESTS_DIRECTORY + '/' + request_file, 0)  # Берем первый лист заявки
    except FileNotFoundError:
        logger.error(f'Отсутствует файл {request_file} в папке requests')
        return -1
    try:
        grade_report_file = get_report_list(gs.GRADE_REPORTS_DIRECTORY)[crs_request_df.iloc[9, 1]]  # файл выгрузки
    except KeyError:
        logger.error(f'Нет файла Grade_Report для запроса {crs_request_df.iloc[9, 1]}')
        return 0
    else:
        return grade_report_file


def get_report_settings(request_file: str, statement_type: str):
    """
    Функция принимает на входе имя файла запроса и тип отчета, для которого нужны настройки.

    Типы отчетов: mini, middle, full.

    Возвращает словарь настроек по курсу в зависимости от получаемого отчета.
    Подходит для любого онлайн-курса на openedu.ru и openedu.urfu.ru

    :param request_file: Строка. Имя файла запроса из папки Requests.
    :param statement_type: Строка. Тип отчета. Существует три типа: mini | middle | full
    :return: словарь с настройками для генерации отчета.
    """
    # Настройки для отчета mini
    if statement_type == 'mini':
        grade_settings = {'Grade': 0.01,
                          "Columns_for_order": ['Итоговый балл'],
                          "Columns_for_report": ['Email', 'Grade'],
                          }
        return grade_settings  # Настройки для mini отчета. Только столбец grade.

    # Настройки для отчета middle
    elif statement_type == 'middle':
        crs_request_df = pnd.read_excel(gs.REQUESTS_DIRECTORY + '/' + request_file, 0)  # Берем первый лист заявки
        grade_cipher = "_".join(crs_request_df.iloc[9, 1].split(sep='_')[:-1]).casefold()  # Берем шифр курса
        try:
            grade_settings = gs.courses[grade_cipher]
        except KeyError:
            logger.error(f'Нет словаря с настройками для курса {grade_cipher.upper()} в grade_settings.py')
            return 0  # обработка отсутствия словаря с настройками
        else:
            return grade_settings

    # Настройки для отчета full
    elif statement_type == 'full':
        crs_request_df = pnd.read_excel(gs.REQUESTS_DIRECTORY + '/' + request_file, 0)  # Берем первый лист заявки
        grade_report_file = get_report_list(gs.GRADE_REPORTS_DIRECTORY)[crs_request_df.iloc[9, 1]]  # файл выгрузки
        grade_report_df = pnd.read_csv(gs.GRADE_REPORTS_DIRECTORY + '/' + grade_report_file)  # DF файла выгрузки
        columns_list = get_columns(grade_report_df.columns.tolist())  # получаем список всех столбцов с оценками

        grade_settings = {"Columns_for_order": columns_list,  # создаем словарь настроек для всех столбцов
                          "Columns_for_report": columns_list,
                          }

        return grade_settings

    else:
        logger.error(f'Выбранный тип отчета - {statement_type} - не существует')
        return -1


def make_grade_column(course_order: pnd.DataFrame,  # DataFrame заявки на курс
                      grade_report: pnd.DataFrame,  # DataFrame отчета об оценках курса
                      col_name: str,  # Название столбца, из которого забираем оценку
                      rate: float,  # Коэффициент для итоговой оценки
                      ):
    """
    Функция принимает в себя DataFrame заявки, DataFrame отчета Grade Report, название столбца,
    из которого будем брать оценку и коэффициент преобразования этого столбца.

    На выходе отдает список оценок в формате List, который добавляется в итоговый DataFrame как столбец справа.

    :param course_order: DataFrame заявки на курс
    :param grade_report: DataFrame отчета об оценках курса
    :param col_name: Название столбца, из которого забираем оценку. Содержится в словаре с настройками
    :param rate: Коэффициент оценки. Для столбцов AVG хранится в словаре, иначе 0,01
    :return: Список оценок, который вставляется как столбец в итоговый DataFrame
    """
    grade_list = []  # Пустой список с оценками. Добавлется в DataFrame столбцом
    number_of_rows = course_order.shape[0]  # Количество строк в DataFrame заявки на курс

    grade_report["Email"] = grade_report.Email.str.lower()  # Копируем столбец адресов из GR в нижний регистр
    possible_mail = grade_report["Email"].tolist()  # И сохраняем в отдельный список

    for x in range(number_of_rows):
        email = str(course_order["Адрес электронной почты"][x]).lower()  # Переводим почту в нижний регистр
        if email in possible_mail:
            grade = grade_report[grade_report["Email"] == email][col_name].iloc[0]
            if (grade == "Not Attempted") or (grade == "Not Available"):
                grade_list.append("Не приступал")
            else:
                tst = float(grade_report[grade_report["Email"] == email][col_name].iloc[0])
                digit = tst / rate
                grade_list.append(int(digit.__round__(0)))  # Округляем до целого значения
        else:
            grade_list.append("Нет на курсе")  # Если нет совпадения по адресу электронной почты
    return grade_list


def check_settings(file_name: str, statement_type: str):
    """
    Функция проверяет основные ошибки, которые возникаеют в следующих случаях:

    1. Отсутствует файл запроса в папке Requests с указанным в параметрах именем
    2. Отсутствует файл отчета Grade Report, по которому должен проходить поиск
    3. Отсутствует словарь настроек для курса, указанного в файле запроса
    4. Дата выгрузки не совпадает с текущей датой. (Предупреждение о неактульных данных)

    :param file_name: Имя файла-запроса. Строка.
    :param statement_type: Типа запрашиваемого отчета mini|middle|full
    :return: Проверенные файлы отчета и настроек. При наличии ошибок возвращает 0
    """
    gr_report_file = get_grade_report_file(file_name)  # Получаем имя файла отчета
    if gr_report_file == -1:
        return 0  # Отсутствует файл-запроса request
    elif gr_report_file == 0:
        return 0  # Отсутствует файл grade report

    gr_settings = get_report_settings(file_name, statement_type=statement_type)  # Получаем словарь настроек
    if gr_settings == 0:
        return 0  # Обработка отсутствия словаря
    if gr_settings == -1:
        return 0  # Не правильный тип отчета

    grade_date_list = gr_report_file.split(sep='_')[-1].split(sep='-')[2::-1]  # получаем дату отчета из файла
    grade_date = '.'.join(grade_date_list)  # дата выгрузки Grade Report
    tday = str(date.today().strftime('%d.%m.%Y'))  # сегодняшняя дата

    if tday != grade_date:
        logger.warning(f'Дата отчета Grade_Report для курса {"_".join(gr_report_file.split(sep="_")[:-3])}'
                       f' не является актуальной')  # Предупреждение: дата не актуальная

    return [gr_report_file, gr_settings]  # Подтверждаем что все в порядке


def get_statement(file_name: str, statement_type: str):
    """
    Функция принимаем на вход в качестве строки имя файла запроса, и тип отчета (mini|middle|full)

    Проверяет входные данные через функцию проверки check_settings и в случае если нет ошибок, то от нее же принимает
    полное имя файла и словарь с настройками. В случае ошибок пропускает обработку.

    Формирует новый DataFrame со второго листа файла запроса и через фукнцию make_grade_column по одному столбцу
    добавляет оценки, соотнося данные по адресу электронной почты.

    В конце выполнения в зависимости от выбранного типа отчета сохраняет в файл с генерируемым названием

    :param file_name: Имя файла запроса
    :param statement_type: Тип запрашиваемого отчета
    """
    check_list = check_settings(file_name, statement_type)
    if check_list == 0:
        return 0  # Если были ошибки при проверке
    else:
        gr_report_file, gr_settings = check_list  # Файл отчета и файл настроек

    dir_file_request = f'{gs.REQUESTS_DIRECTORY}/{file_name}'  # Полный путь к файлу заявки
    dir_file_report = f'{gs.GRADE_REPORTS_DIRECTORY}/{gr_report_file}'  # Полный путь к файлу отчету GR

    grade_date_list = gr_report_file.split(sep='_')[-1].split(sep='-')[2::-1]  # Берем дату отчета из имени файла
    grade_date = '.'.join(grade_date_list)  # И сохраняем ее в нужном формате

    # Путь для будущего файла отчета. Пипец длинный, поэтому отдельной строкой
    dir_file_statement = f'{gs.STATEMENTS_DIRECTORY}/{file_name.rstrip(".xlsx")}_{statement_type}_{grade_date}.xlsx'

    course_request_df = pnd.read_excel(dir_file_request, 1)  # DF заявки
    grade_report_df = pnd.read_csv(dir_file_report, delimiter=',')[gr_settings["Columns_for_report"]]  # DF выгрузки

    if statement_type == 'full':  # Полный отчет
        for x, y in zip(gr_settings["Columns_for_report"][1:], gr_settings["Columns_for_order"][1:]):
            test_list = make_grade_column(course_request_df, grade_report_df, x, 0.01)
            course_request_df[y] = test_list
    else:  # Короткий и средний отчеты
        for x, y in zip(gr_settings["Columns_for_report"][1:], gr_settings["Columns_for_order"]):
            test_list = make_grade_column(course_request_df, grade_report_df, x, gr_settings[x])
            course_request_df[y] = test_list

    course_request_df.to_excel(dir_file_statement, index=False)
    logger.info(f'{file_name.rstrip(".xlsx")}_{statement_type}_{grade_date}.xlsx - OK!')


if __name__ == "__main__":
    for file in REQUESTS_FILES:
        if '.~' in file:         # игнорируем временные файлы, которые создаются при открытии
            continue             # необходимо проверить префикс в Windows
        else:
            get_statement(file, 'middle')  # statement_type= mini|middle|full

    # get_statement('UrFU_0079.xlsx', statement_type='middle')  # Заказ конкретного отчета
