import pandas as pnd

first_df = pnd.read_excel('РТФ_УИС_fall_2020.xlsx')
second_df = pnd.read_csv('urfu_INTPR_fall_2020_grade_report_2021-01-02-0921.csv', sep=',')

first_df.rename(columns={'Адрес электронной почты': 'Email'}, inplace=True)

third_df = pnd.merge(first_df, second_df[['Email', 'Grade']], on='Email', how='left')
third_df['Grade'] = third_df['Grade'] * 100
third_df['Grade'].convert_dtypes(convert_integer=True)
print(third_df)
third_df.to_excel('result.xlsx', index=None)
