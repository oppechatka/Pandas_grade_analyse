from os import listdir
import pandas as pnd
import grade_settings as GS

REQUESTS_FILES = listdir(GS.REQUESTS_DIRECTORY)
GRADE_REPORT_FILES = listdir(GS.GRADE_REPORTS_DIRECTORY)


def get_grade_report(request_file: str):
    crs_request_df = pnd.read_excel(GS.REQUESTS_DIRECTORY + '/' + request_file, 0)  # Берем первый лист заявки
    grade_report_file = crs_request_df.iloc[9, 1] + '.csv'                          # Получаем имя выгрузки
    grade_settings = "_".join(grade_report_file.split(sep='_')[:-1]).casefold()     # ключ настроек
    if grade_report_file not in GRADE_REPORT_FILES:
        print("Нет файла с выгрузкой в папке для " + grade_report_file)
        return 0
    elif grade_settings not in GS.courses:
        print("Нет словаря с настройками для курса для" + grade_settings)
        return 0
    else:
        grade_settings = GS.courses[grade_settings]
        return [grade_report_file, grade_settings]


def make_grade_column(course_order,             # DataFrame заявки на курс
                      grade_report,             # DataFrame отчета об оценках курса
                      possible_mail: list,      # Список возможных электронных адресов
                      col_name: str,            # Название столбца, из которого забираем оценку
                      rate: float,              # Коэффициент для итоговой оценки
                      ):
    grade_list = []                             # Пустой список с оценками. Добавлется в DataFrame столбцом
    number_of_rows = course_order.shape[0]      # Количество строк в DataFrame заявки на курс
    for x in range(number_of_rows):
        email = course_order["Адрес электронной почты"][x]
        if email in possible_mail:
            digit = grade_report[grade_report["Email"] == email][col_name].iloc[0] / rate
            grade_list.append(int(digit.__round__(0)))
        else:
            grade_list.append("Нет на курсе")
    return grade_list


for file in REQUESTS_FILES:
    gr_report_file, gr_settings = get_grade_report(file)                       # Получаем файл и настройки

    course_request_df = pnd.read_excel(GS.REQUESTS_DIRECTORY + '/' + file, 1)  # Берем второй лист заявки

    grade_report_df = pnd.read_csv(GS.GRADE_REPORTS_DIRECTORY +
                               '/' + gr_report_file, delimiter=',')[gr_settings["Columns_for_report"]]  # DF выгрузки

    possible_mail = grade_report_df["Email"].tolist()    # список возможных почт для обработки исключений

    for x, y in zip(gr_settings["Columns_for_report"][1:], gr_settings["Columns_for_order"]):
        test_list = make_grade_column(course_request_df, grade_report_df, possible_mail, x, gr_settings[x])
        course_request_df[y] = test_list

    course_request_df.to_excel(GS.STATEMENTS_DIRECTORY + '/' + file.rstrip('.xlsx') + "_ведомость.xlsx", index=False)
    print(file.rstrip('.xlsx') + "_ведомость.xlsx" + " - OK!")
