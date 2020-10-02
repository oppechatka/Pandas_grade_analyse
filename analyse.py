from loguru import logger
from os import listdir
import pandas as pnd
import grade_settings as gs

REQUESTS_FILES = listdir(gs.REQUESTS_DIRECTORY)
GRADE_REPORT_FILES = listdir(gs.GRADE_REPORTS_DIRECTORY)


def get_report_list(directory: str):
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
    new_list = list_columns[list_columns.index('Grade'):list_columns.index('Cohort Name')]
    for name in new_list:
        if ('(Avg)' in name) or ("Grade Percent" in name):
            new_list.pop(new_list.index(name))
    final_list = ['Email'] + new_list
    return final_list


def get_nano_report_settings(request_file: str):
    crs_request_df = pnd.read_excel(gs.REQUESTS_DIRECTORY + '/' + request_file, 0)  # Берем первый лист заявки
    grade_report_file = get_report_list(gs.GRADE_REPORTS_DIRECTORY)[crs_request_df.iloc[9, 1]]  # файл выгрузки

    grade_settings = {'Grade': 0.01,
                      "Columns_for_order": ['Итоговый балл'],
                      "Columns_for_report": ['Email', 'Grade'],
                      }

    if grade_report_file not in GRADE_REPORT_FILES:
        print("Нет файла с выгрузкой в папке для " + grade_report_file)
        return 0
    else:
        return [grade_report_file, grade_settings]


def get_min_report_settings(request_file: str):
    crs_request_df = pnd.read_excel(gs.REQUESTS_DIRECTORY + '/' + request_file, 0)  # Берем первый лист заявки
    grade_settings = "_".join(crs_request_df.iloc[9, 1].split(sep='_')[:-1]).casefold()  # Берем шифр курса
    grade_report_file = get_report_list(gs.GRADE_REPORTS_DIRECTORY)[crs_request_df.iloc[9, 1]]  # файл выгрузки

    if grade_report_file not in GRADE_REPORT_FILES:
        print("Нет файла с выгрузкой в папке для " + grade_report_file)
        return 0
    elif grade_settings not in gs.courses:
        print("Нет словаря с настройками для курса для " + grade_settings)
        return 0
    else:
        grade_settings = gs.courses[grade_settings]
        return [grade_report_file, grade_settings]


def get_max_report_settings(request_file: str):
    crs_request_df = pnd.read_excel(gs.REQUESTS_DIRECTORY + '/' + request_file, 0)  # Берем первый лист заявки
    grade_report_file = get_report_list(gs.GRADE_REPORTS_DIRECTORY)[crs_request_df.iloc[9, 1]]  # файл выгрузки
    grade_report_df = pnd.read_csv(gs.GRADE_REPORTS_DIRECTORY + '/' + grade_report_file)
    columns_list = get_columns(grade_report_df.columns.tolist())

    grade_settings = {"Columns_for_order": list(columns_list),
                      "Columns_for_report": list(columns_list),
                      }

    if grade_report_file not in GRADE_REPORT_FILES:
        print("Нет файла с выгрузкой в папке для " + grade_report_file)
        return 0
    else:
        return [grade_report_file, grade_settings]


def make_grade_column(course_order,             # DataFrame заявки на курс
                      grade_report,             # DataFrame отчета об оценках курса
                      possible_mail: list,      # Список возможных электронных адресов
                      col_name: str,            # Название столбца, из которого забираем оценку
                      rate: float,              # Коэффициент для итоговой оценки
                      ):
    grade_list = []                             # Пустой список с оценками. Добавлется в DataFrame столбцом
    number_of_rows = course_order.shape[0]      # Количество строк в DataFrame заявки на курс

    # lower_possible_mail = [x.lower() for x in possible_mail]
    # print(possible_mail)
    # print(lower_possible_mail)

    for x in range(number_of_rows):
        email = str(course_order["Адрес электронной почты"][x]).lower()  # Переводим почту в нижний регистр
        if email in possible_mail:
            grade = grade_report[grade_report["Email"] == email][col_name].iloc[0]
            if (grade == "Not Attempted") or (grade == "Not Available"):
                grade_list.append("Не приступал")
            else:
                tst = float(grade_report[grade_report["Email"] == email][col_name].iloc[0])
                digit = tst / rate
                grade_list.append(int(digit.__round__(0)))
        else:
            # print(email)
            grade_list.append("Нет на курсе")
    return grade_list


def get_mini_statement(file_name: str):
    gr_report_file, gr_settings = get_nano_report_settings(file_name)              # Получаем ссылки на настройки

    course_request_df = pnd.read_excel(gs.REQUESTS_DIRECTORY + '/' + file_name, 1)  # DF заявки

    grade_date_list = gr_report_file.split(sep='_')[-1].split(sep='-')[2::-1]
    grade_date = '.'.join(grade_date_list)                                          # дата выгрузки Grade Report

    grade_report_df = pnd.read_csv(gs.GRADE_REPORTS_DIRECTORY +
                                   '/' + gr_report_file, delimiter=',')[
        gr_settings["Columns_for_report"]]                                          # DF выгрузки

    grade_report_df["Email"] = grade_report_df.Email.str.lower()    # Копируем столбец, переводим в нижний регистр
    possible_mail = grade_report_df["Email"].tolist()               # список возможных почт для обработки исключений

    for x, y in zip(gr_settings["Columns_for_report"][1:], gr_settings["Columns_for_order"]):
        test_list = make_grade_column(course_request_df, grade_report_df, possible_mail, x, gr_settings[x])
        course_request_df[y] = test_list

    course_request_df.to_excel(gs.STATEMENTS_DIRECTORY +
                               '/' + file_name.rstrip('.xlsx') + "_итоговый балл_" + grade_date + ".xlsx", index=False)

    print(file_name.rstrip('.xlsx') + "_итоговый балл_" + grade_date + ".xlsx" + " - OK!")


def get_statement(file_name: str):
    # print(file_name)
    gr_report_file, gr_settings = get_min_report_settings(file_name)              # Получаем ссылки на настройки

    course_request_df = pnd.read_excel(gs.REQUESTS_DIRECTORY + '/' + file_name, 1)  # DF заявки

    grade_date_list = gr_report_file.split(sep='_')[-1].split(sep='-')[2::-1]
    grade_date = '.'.join(grade_date_list)                                          # дата выгрузки Grade Report

    grade_report_df = pnd.read_csv(gs.GRADE_REPORTS_DIRECTORY +
                                   '/' + gr_report_file, delimiter=',')[
        gr_settings["Columns_for_report"]]                                          # DF выгрузки

    grade_report_df["Email"] = grade_report_df.Email.str.lower()    # Копируем столбец, переводим в нижний регистр
    possible_mail = grade_report_df["Email"].tolist()               # список возможных почт для обработки исключений

    for x, y in zip(gr_settings["Columns_for_report"][1:], gr_settings["Columns_for_order"]):
        test_list = make_grade_column(course_request_df, grade_report_df, possible_mail, x, gr_settings[x])
        course_request_df[y] = test_list

    course_request_df.to_excel(gs.STATEMENTS_DIRECTORY +
                               '/' + file_name.rstrip('.xlsx') + "_ведомость_" + grade_date + ".xlsx", index=False)

    print(file_name.rstrip('.xlsx') + "_ведомость_" + grade_date + ".xlsx" + " - OK!")


def get_full_statement(file_name: str):
    gr_report_file, gr_settings = get_max_report_settings(file_name)                # Получаем ссылки на настройки

    course_request_df = pnd.read_excel(gs.REQUESTS_DIRECTORY + '/' + file_name, 1)  # DF заявки

    grade_date_list = gr_report_file.split(sep='_')[-1].split(sep='-')[2::-1]
    grade_date = '.'.join(grade_date_list)                                          # дата выгрузки Grade Report

    grade_report_df = pnd.read_csv(gs.GRADE_REPORTS_DIRECTORY +
                                   '/' + gr_report_file, delimiter=',')[
        gr_settings["Columns_for_report"]]                                          # DF выгрузки

    grade_report_df["Email"] = grade_report_df.Email.str.lower()    # переводим все почты в нижний регистр
    possible_mail = grade_report_df["Email"].tolist()           # Делаем список почт для проверки

    for x, y in zip(gr_settings["Columns_for_report"][1:], gr_settings["Columns_for_order"][1:]):
        test_list = make_grade_column(course_request_df, grade_report_df, possible_mail, x, 0.01)
        course_request_df[y] = test_list

    course_request_df.to_excel(gs.STATEMENTS_DIRECTORY +
                               '/' + file_name.rstrip('.xlsx') + "_полная_ведомость_" + grade_date + ".xlsx",
                               index=False)

    print(file_name.rstrip('.xlsx') + "_полная_ведомость_" + grade_date + ".xlsx" + " - OK!")


for file in REQUESTS_FILES:
    get_mini_statement(file)
    # get_statement(file)
    # get_full_statement(file)


# get_statement('UrFU_0079.xlsx')
# get_full_statement('UrFU_0079.xlsx')
