from loguru import logger
from os import listdir
import pandas as pnd
import grade_settings as gs
import datetime


file_list = listdir("./statements")     # Директория с отчетами

dict_data = {"№ Заявки": [],
             "Вуз участника": [],
             "Название курса": [],
             "Общее количество слушателей": [],
             "Нет на курсе": [],
             "Слушателей, изучивших более 0%": [],
             "Слушателей, изучивших более 50%": [],
             "Дата выгрузки": [],
             }


# noinspection PyTypeChecker
def get_string(file_name: str):
    # print(file_name)
    course_statement_df = pnd.read_excel('./statements/' + file_name, 0)  # DF отчета

    dict_data["№ Заявки"].append(course_statement_df["№ Заявки"][0])
    dict_data["Вуз участника"].append(course_statement_df["Вуз участника"][0])
    dict_data["Название курса"].append(course_statement_df["Название курса"][0])
    dict_data["Общее количество слушателей"].append(len(course_statement_df[course_statement_df["Роль"] == 'студент']))

    course_statement_df['Итоговый балл'].replace('Нет на курсе', -1, inplace=True)
    dict_data["Нет на курсе"].append(len(course_statement_df[course_statement_df["Итоговый балл"] == -1]))

    filter_more = course_statement_df['Итоговый балл'].astype('int') > 0
    dict_data["Слушателей, изучивших более 0%"].append(len(course_statement_df.loc[filter_more]))

    filter_more = course_statement_df['Итоговый балл'].astype('int') > 30
    dict_data["Слушателей, изучивших более 50%"].append(len(course_statement_df.loc[filter_more]))

    dict_data["Дата выгрузки"].append(file_name.split(sep='_')[-1][:-5])


for files_name in file_list:
    get_string(files_name)

result_df = pnd.DataFrame(dict_data)
result_df.sort_values(by='№ Заявки', inplace=True)
print(gs.STATISTIC_DIRECTORY + '/статистика_' + str(datetime.date.today()) + ".xlsx - Ok!")
result_df.to_excel(gs.STATISTIC_DIRECTORY + '/статистика_' + str(datetime.date.today()) + ".xlsx", index=False)

