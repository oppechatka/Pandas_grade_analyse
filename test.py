from os import listdir
import pandas as pnd

DIRECTORY = './grade_reports/full_grade_name/'

file_list = listdir(DIRECTORY)
dict_file = dict()

for x in range(len(file_list)):
	file = file_list[x].split(sep="_")
	file = file[1:-3]
	if file[-1] == "net":
		key_str = '_'.join(file[:-3]) + '_' + ''.join(file[-3:])
		dict_file[key_str] = file_list[x]
	else:
		key_str = '_'.join(file[:-2]) + '_' + ''.join(file[-2:])
		dict_file[key_str] = file_list[x]


print(dict_file)

# print(new_list.index('Grade'), new_list.index('Cohort Name'))
