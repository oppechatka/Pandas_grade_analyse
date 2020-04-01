import pandas as pnd

TEST_FILE_NAME = "KSE.xlsx"

data = pnd.read_excel(TEST_FILE_NAME)


print(data[["Код студента", "Фамилия", "Имя"]][data["Фамилия"] == 'Васильева'])


for x, y in data.iterrows():
	print(x, y)
	break

