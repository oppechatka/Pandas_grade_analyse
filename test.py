import pandas as pnd

grade_report_df = pnd.read_csv('././grade_reports/ARCHC_spring2020.csv')

new_list = grade_report_df.columns.tolist()		# Список столбцов

new_list = new_list[new_list.index('Grade'):new_list.index('Cohort Name') + 1]

for name in new_list:
	if ('(Avg)' in name) or ("Grade Percent" in name):
		new_list.pop(new_list.index(name))
final_list = ['Email'] + new_list
print(final_list)

# print(new_list.index('Grade'), new_list.index('Cohort Name'))
