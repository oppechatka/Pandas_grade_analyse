STATEMENTS_DIRECTORY = './statements'
REQUESTS_DIRECTORY = './requests'
GRADE_REPORTS_DIRECTORY = './grade_reports'

calc = {"Тест (Avg)": 0.001,
        "Рубежный тест (Avg)": 0.005,
        "Итоговый контроль (Avg)": 0.004,
        "Grade Percent": 1,
        "Columns_for_order": ["Тесты", "Рубежные тесты", "Экзамен", "Итоговый балл"],
        "Columns_for_report": ["Email", "Тест (Avg)", "Рубежный тест (Avg)", "Итоговый контроль (Avg)", "Grade Percent"]
        }

tepl = {"Техническая термодинамика (Avg)": 0.002,
        "Теплообмен (Avg)": 0.002,
        "Энергетическое оборудование (Avg)": 0.002,
        "Итоговый контроль (Avg)": 0.004,
        "Grade Percent": 1,
        "Columns_for_order": ["Техническая термодинамика",
                              "Теплообмен",
                              "Энергетическое оборудование",
                              "Экзамен",
                              "Итоговый балл"],
        "Columns_for_report": ["Email",
                               "Техническая термодинамика (Avg)",
                               "Теплообмен (Avg)",
                               "Энергетическое оборудование (Avg)",
                               "Итоговый контроль (Avg)",
                               "Grade Percent"]
        }

teco = {"Тест для самоконтроля (Avg)": 0.003,
        "Задание (Avg)": 0.003,
        "Итоговое тестирование (Avg)": 0.004,
        "Grade Percent": 1,
        "Columns_for_order": ["Тесты",
                              "Задания",
                              "Экзамен",
                              "Итоговый балл"],
        "Columns_for_report": ["Email",
                               "Тест для самоконтроля (Avg)",
                               "Задание (Avg)",
                               "Итоговое тестирование (Avg)",
                               "Grade Percent"]
        }

chemso = {"Задание (Avg)": 0.006,
          "Итоговый контроль (Avg)": 0.004,
          "Grade Percent": 1,
          "Columns_for_order": ["Задания",
                                "Экзамен",
                                "Итоговый балл"],
          "Columns_for_report": ["Email",
                                 "Задание (Avg)",
                                 "Итоговый контроль (Avg)",
                                 "Grade Percent"]
          }

elb = {"Домашная работа (Avg)": 0.006,
       "Итоговое задание (Avg)": 0.004,
       "Grade Percent": 1,
       "Columns_for_order": ["Домашняя работа",
                             "Экзамен",
                             "Итоговый балл"],
       "Columns_for_report": ["Email",
                              "Домашная работа (Avg)",
                              "Итоговое задание (Avg)",
                              "Grade Percent"]
       }

ecos = {"Задание (Avg)": 0.0015,
        "Практическое задание (Avg)": 0.004,
        "Эссе": 0.0005,
        "Итоговое тестирование (Avg)": 0.004,
        "Grade Percent": 1,
        "Columns_for_order": ["Задания",
                              "Практические задания",
                              "Эссе",
                              "Экзамен",
                              "Итоговый балл"],
        "Columns_for_report": ["Email",
                               "Задание (Avg)",
                               "Практическое задание (Avg)",
                               "Эссе",
                               "Итоговое тестирование (Avg)",
                               "Grade Percent"]
        }

lifesafety = {"Тестовое задание (Avg)": 0.004,  # Требует доработки после доабвления экзамена
              "Grade Percent": 1,
              "Columns_for_order": ["Тесты",
                                    "Итоговый балл"],
              "Columns_for_report": ["Email",
                                     "Тестовое задание (Avg)",
                                     "Grade Percent"]
              }

mcs = {"Тестовое задание (Avg)": 0.0015,
       "Учебное задание (Avg)": 0.0015,
       "Контрольные задания (Avg)": 0.003,
       "Итоговый контроль (Avg)": 0.004,
       "Grade Percent": 1,
       "Columns_for_order": ["Тесты",
                             "Учебные задания",
                             "Контрольные задания",
                             "Экзамен",
                             "Итоговый балл"],
       "Columns_for_report": ["Email",
                              "Тестовое задание (Avg)",
                              "Учебное задание (Avg)",
                              "Контрольные задания (Avg)",
                              "Итоговый контроль (Avg)",
                              "Grade Percent"]
       }

hist_view = {"Test (Avg)": 0.003,
             "modul (Avg)": 0.003,
             "Final Exam (Avg)": 0.004,
             "Grade Percent": 1,
             "Columns_for_order": ["Тесты",
                                   "Учебные задания",
                                   "Экзамен",
                                   "Итоговый балл"],
             "Columns_for_report": ["Email",
                                    "Test (Avg)",
                                    "modul (Avg)",
                                    "Final Exam (Avg)",
                                    "Grade Percent"]
             }

courses = {'calc':        calc,
           'tepl':        tepl,
           'teco':        teco,
           'chemso':      chemso,
           'elb':         elb,
           'ecos':        ecos,
           'lifesafety':  lifesafety,
           'mcs':         mcs,
           'hist_view':   hist_view,
           }
