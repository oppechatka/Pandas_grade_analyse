from loguru import logger
from datetime import date
from os import listdir
import pandas as pnd
import grade_settings as gs


def get_report_list(directory: str, report_type='grade') -> dict:
    # TODO переработать функцию. Возможны сбои при создании скрытого курса в названии которого больше чем 2 слова
    """
    Функция получает на входе строкой директорию, где находятся файлы с отчетами Grade Report, пробегает по всем файлам
    и формирует словарь в виде:

    {шифр курса: "имя файла отчета"}

    Работает только с openedu.ru

    :param report_type: тип отчета для которого составляем список "grade|exam". По умолчанию 'grade'
    :param directory: путь к директории
    :return: Cловарь, где ключом является шифр курса (прим. ecos_fall2020net ), значение полное имя файла с отчетом
    """
    file_list = listdir(directory)
    dict_file = dict()
    x_end = -3  # Делаем срез для названия в отчете Grade Report

    if report_type == 'exam':
        x_end = -5  # Делаем срез для названия в отчете Exam Results

    for x in range(len(file_list)):
        file_grade = file_list[x].split(sep="_")
        file_grade = file_grade[1:x_end]
        if file_grade[-1] == "net" or file_grade[-1] == "npr":
            key_str = '_'.join(file_grade[:-3]) + '_' + ''.join(file_grade[-3:])
            dict_file[key_str] = file_list[x]
        else:
            key_str = '_'.join(file_grade[:-2]) + '_' + ''.join(file_grade[-2:])
            dict_file[key_str] = file_list[x]
    return dict_file


def get_columns(list_columns: list) -> list:
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


def get_exam_results_file(request_file: str):
    """
    Функция получает на входе имя файла-запроса из папки Requests, на первом листе файла обращается к ячейке
    с шифром курса, и возвращает соответствующий ему файл отчета Exam Results в одноименной папке

    :param request_file: имя файла запроса из папки Requests
    :return: имя файла отчета Exam Results из которого будут браться статусы прокторинга
    """
    try:
        crs_request_df = pnd.read_excel(gs.REQUESTS_DIRECTORY + '/' + request_file, 0)  # Берем первый лист заявки
    except FileNotFoundError:
        logger.error(f'Отсутствует файл {request_file} в папке requests')
        return -1
    try:
        exam_results_file = get_report_list(gs.EXAM_RESULTS_DIRECTORY, report_type='exam')[crs_request_df.iloc[9, 1]]
    except KeyError:
        logger.error(f'Нет файла Exam_Results для запроса {crs_request_df.iloc[9, 1]}')
        return 0
    else:
        return exam_results_file


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
    elif statement_type == 'middle' or statement_type == 'proctor':
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

    if statement_type == 'proctor':
        exam_result_file = get_exam_results_file(file_name)  # Получаем имя файла отчета
        if exam_result_file == -1:
            return 0  # Отсутствует файл-запроса request
        elif exam_result_file == 0:
            return 0  # Отсутствует файл exam result
    else:
        exam_result_file = 0

    gr_settings = get_report_settings(file_name, statement_type=statement_type)  # Получаем словарь настроек
    if gr_settings == 0:
        return 0  # Обработка отсутствия словаря
    if gr_settings == -1:
        return 0  # Не правильный тип отчета

    grade_date_list = gr_report_file.split(sep='_')[-1].split(sep='-')[2::-1]  # получаем дату отчета из файла
    grade_date = '.'.join(grade_date_list)  # дата выгрузки Grade Report
    tday = str(date.today().strftime('%d.%m.%Y'))  # сегодняшняя дата

    if exam_result_file != 0:
        exam_date_list = exam_result_file.split(sep='_')[-1].split(sep='-')[2::-1]  # получаем дату exam_results
        exam_date = '.'.join(exam_date_list)  # дата выгрузки exam result
        if tday != exam_date:
            logger.warning(f'Дата отчета Exam_Result для курса {"_".join(gr_report_file.split(sep="_")[:-3])}'
                           f' не является актуальной')  # Предупреждение: дата не актуальная

    if tday != grade_date:
        logger.warning(f'Дата отчета Grade_Report для курса {"_".join(gr_report_file.split(sep="_")[:-3])}'
                       f' не является актуальной')  # Предупреждение: дата не актуальная

    return [gr_report_file, gr_settings, exam_result_file]  # Подтверждаем что все в порядке


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
        gr_report_file, gr_settings, exam_results_file = check_list  # Файл отчета и файл настроек

    dir_file_request = f'{gs.REQUESTS_DIRECTORY}/{file_name}'  # Полный путь к файлу заявки
    dir_file_report = f'{gs.GRADE_REPORTS_DIRECTORY}/{gr_report_file}'  # Полный путь к файлу отчету GR

    grade_date_list = gr_report_file.split(sep='_')[-1].split(sep='-')[2::-1]  # Берем дату отчета из имени файла
    grade_date = '.'.join(grade_date_list)  # И сохраняем ее в нужном формате

    # Путь для будущего файла отчета. Пипец длинный, поэтому отдельной строкой
    dir_file_statement = f'{gs.STATEMENTS_DIRECTORY}/{file_name.rstrip(".xlsx")}_{statement_type}_{grade_date}.xlsx'

    course_request_df = pnd.read_excel(dir_file_request, 1)  # DF заявки
    grade_report_df = pnd.read_csv(dir_file_report, delimiter=',')  # DF выгрузки
    exam_results_df = 0

    if statement_type == 'proctor':
        dir_file_exam_results = f'{gs.EXAM_RESULTS_DIRECTORY}/{exam_results_file}'
        exam_results_df = pnd.read_csv(dir_file_exam_results, decimal=',')[['exam_name', 'email', 'status']]
        exam_results_file = get_exam_results_file(file_name)
        gr_settings = change_dict_settings(gr_settings, exam_results_file, grade_report_df)

    if statement_type == 'full':  # Полный отчет
        for x, y in zip(gr_settings["Columns_for_report"][1:], gr_settings["Columns_for_order"][1:]):
            test_list = make_grade_column(course_request_df, grade_report_df, x, 0.01)
            course_request_df[y] = test_list
    elif statement_type == 'proctor':  # Отчет с прокторингом
        for x, y in zip(gr_settings["Columns_for_report"][1:], gr_settings["Columns_for_order"]):
            if '_Status' in x:
                test_list = make_status_column(course_request_df, exam_results_df, x)
            else:
                test_list = make_grade_column(course_request_df, grade_report_df, x, gr_settings[x])
            course_request_df[y] = test_list
    else:  # Короткий и средний отчеты
        for x, y in zip(gr_settings["Columns_for_report"][1:], gr_settings["Columns_for_order"]):
            test_list = make_grade_column(course_request_df, grade_report_df, x, gr_settings[x])
            course_request_df[y] = test_list

    course_request_df.to_excel(dir_file_statement, index=False)
    logger.info(f'{file_name.rstrip(".xlsx")}_{statement_type}_{grade_date}.xlsx - OK!')


def get_exam_names(filename: str):
    df_exam_result = pnd.read_csv(gs.EXAM_RESULTS_DIRECTORY + '/' + filename)
    exam_set = set(df_exam_result['exam_name'])
    exam_set = list(exam_set)
    exam_set.sort()
    return exam_set


def change_dict_settings(dict_settings: dict, exam_results_file: str, grade_report_df: pnd.DataFrame):
    exam_list = (get_exam_names(exam_results_file))
    exam_list.append('Восстановление баллов')
    new_settings = dict.copy(dict_settings)
    column_list = grade_report_df.columns.tolist()

    a = new_settings['Columns_for_report'].pop(-2)
    new_settings['Columns_for_order'].pop(-2)
    new_settings.__delitem__(a)

    for _ in exam_list:
        for column in column_list:
            if _ in column:
                if _ == "Восстановление баллов":
                    new_settings['Columns_for_report'].insert(-1, column)
                    new_settings['Columns_for_order'].insert(-1, column)
                    new_settings[column] = 0.01
                else:
                    new_settings['Columns_for_report'].insert(-1, column)
                    new_settings['Columns_for_report'].insert(-1, _ + '_Status')
                    new_settings['Columns_for_order'].insert(-1, column)
                    new_settings['Columns_for_order'].insert(-1, _ + '_Status')
                    new_settings[column] = 0.01

    return new_settings


def make_status_column(request_df: pnd.DataFrame, exam_results_df: pnd.DataFrame, exam_name: str):
    result_col = []
    possible_emails = request_df['Адрес электронной почты'].str.lower()
    possible_emails = possible_emails.tolist()

    exam_results_df = exam_results_df[exam_results_df['exam_name'] == exam_name[:-7]]

    for _ in possible_emails:
        try:
            value = exam_results_df[exam_results_df['email'] == _]['status'].iloc[0]
        except IndexError:
            value = 'Не сдавал'
        if value == 'verified':
            result_col.append('Подтверждено')
        elif value == 'rejected':
            result_col.append('Отклонено')
        elif value == 'submitted':
            result_col.append('Отправлено на проверку')
        elif value == 'created':
            result_col.append('Создано')
        else:
            result_col.append(value)
    return result_col


def get_status_df(proctor_file: str):
    first_df = pnd.read_csv(gs.EXAM_RESULTS_DIRECTORY + '/' + proctor_file, sep=',')
    first_df = first_df[['exam_name', 'username', 'email', 'status']]

    final_df = first_df[['username', 'email']].drop_duplicates()
    list_exam = first_df['exam_name'].tolist()
    list_exam = list(set(list_exam))
    list_exam.sort()
    map_filter = {'created': 'Создано',
                  'submitted': 'Отправлено на проверку',
                  'verified': 'Подтверждено',
                  'rejected': 'Отклонено',
                  }

    for x in list_exam:
        my_filter = first_df['exam_name'] == x
        temp_df = first_df.loc[my_filter]
        final_df = pnd.merge(final_df, temp_df[['email', 'status']], on='email', how='left')
        final_df['status'] = final_df['status'].map(map_filter)
        final_df['status'].fillna('Не сдавал', inplace=True)
        final_df.rename(columns={'status': x + '_Status'}, inplace=True)

    return final_df


def get_proctor_report(request_file: str):

    check_list = check_settings(request_file, statement_type='proctor')
    if check_list == 0:
        return 0  # Если были ошибки при проверке
    else:
        gr_report_file, gr_settings, exam_results_file = check_list  # Файл отчета и файл настроек

    report_file = gr_report_file    # get_grade_report_file(request_file)
    report_df = pnd.read_csv(gs.GRADE_REPORTS_DIRECTORY + '/' + report_file, delimiter=',')
    report_df['Email'] = report_df['Email'].str.lower()

    # Рассчитываем поле "прогресс" и добавляем его в таблицу с grade report
    rate = 0
    for col in gr_settings['Columns_for_report'][1:-2]:
        rate += gr_settings[col]
    report_df['Прогресс в БРС'] = ((report_df[gr_settings['Columns_for_report'][1:-2]].sum(axis=1))/rate).__round__(0)

    request_df = pnd.read_excel(gs.REQUESTS_DIRECTORY + '/' + request_file, 1)
    request_df['Адрес электронной почты'] = request_df['Адрес электронной почты'].str.lower()
    request_df.rename(columns={'Адрес электронной почты': 'Email'}, inplace=True)

    grade_date_list = gr_report_file.split(sep='_')[-1].split(sep='-')[2::-1]  # Берем дату отчета из имени файла
    grade_date = '.'.join(grade_date_list)  # И сохраняем ее в нужном формате
    dir_file_statement = f'{gs.STATEMENTS_DIRECTORY}/{request_file.rstrip(".xlsx")}_new_proctor_{grade_date}.xlsx'

    report_settings = get_report_settings(request_file, 'proctor')
    report_settings = change_dict_settings(report_settings, exam_results_file, report_df)
    report_settings['Columns_for_report'].append('Прогресс в БРС')
    report_settings['Columns_for_order'].append('Прогресс в БРС')
    report_settings['Прогресс в БРС'] = 1

    status_df = get_status_df(exam_results_file)
    status_df['email'] = status_df['email'].str.lower()
    status_df = status_df.rename(columns={'email': 'Email'})

    temp_df = pnd.merge(report_df, status_df, on='Email', how='left')
    result_df = pnd.merge(request_df, temp_df[report_settings['Columns_for_report']], on='Email', how='left')

    # Костыли-велосипеды наши лучшие соседы!
    for column in report_settings['Columns_for_report'][1:]:
        if '_Status' not in column:
            result_df[column].fillna(report_settings[column]*-1, inplace=True)
            result_df[column].replace('Not Available', report_settings[column]*-2, inplace=True)
            result_df[column] = result_df[column].astype('float')
            result_df[column] = (result_df[column] / report_settings[column]).__round__(0)

            result_df[column].replace(-1, 'Нет на курсе', inplace=True)
            result_df[column].replace(-2, 'Не доступно', inplace=True)
        else:
            result_df[column].fillna('Не сдавал', inplace=True)

    for column_rep, column_ord in zip(report_settings['Columns_for_report'][1:], report_settings['Columns_for_order']):
        result_df.rename(columns={column_rep: column_ord}, inplace=True)

    result_df.to_excel(dir_file_statement, index=False)
    logger.info(f'{request_file.rstrip(".xlsx")}_new_proctor_{grade_date}.xlsx - OK!')


if __name__ == "__main__":
    for file in gs.REQUESTS_FILES:
        if '.~' in file or '~$' in file:  # игнорируем временные файлы, которые создаются при открытии
            continue
        else:
            # get_statement(file, 'proctor')  # statement_type= mini|middle|full|proctor
            get_proctor_report(file)

    # get_statement('РТФ_УИС_fall_2020.xlsx', statement_type='middle')  # Заказ конкретного отчета
    # get_statement('РТФ_УИС_fall_2020.xlsx', statement_type='full')  # Заказ конкретного отчета
