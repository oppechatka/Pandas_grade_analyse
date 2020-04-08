import requests
from selenium import webdriver


driver = webdriver.Firefox()
driver.close()

# with requests.Session() as s:
#     r = s.get(url, headers=headers)
#     r1 = s.post(url, headers=headers)
#     if 'csrftoken' in s.cookies:
#         login_data['csrfmiddlewaretoken'] = r.cookies['csrftoken']
#     print(s.post(url, data=login_data))
