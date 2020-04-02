import pandas as pnd
import grade_settings as gs

TEST_FILE_NAME = "UrFU_0001.xlsx"
TEST_GRADE_REPORT = "urfu_CALC_spring_2020_grade_report_2020-04-02-0401.csv"

gr_rep = pnd.read_csv(TEST_GRADE_REPORT, delimiter=',')[gs.calc["Columns_for_report"]]

course_ord = pnd.read_excel(TEST_FILE_NAME, 0)    # Берем первый лист заявки
course_cipher = course_ord.iloc[9, 1]             # Получаем шифр курса. Всегда в одной ячейке

course_ord = pnd.read_excel(TEST_FILE_NAME, 1)    # Берем второй лист заявки

poss_mail = gr_rep["Email"].tolist()            # Список возможных почт, для обработки отсутствия почты


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


for x, y in zip(gs.calc["Columns_for_report"][1:], gs.calc["Columns_for_order"]):
    test_list = make_grade_column(course_ord, gr_rep, poss_mail, x, gs.calc[x])
    course_ord[y] = test_list

course_ord.to_excel("UrFU_0001_ведомость.xlsx", index=False)  # Запись в файл без столбца индексов
