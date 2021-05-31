import random
import time

import openpyxl
from bs4 import BeautifulSoup
from selenium import webdriver

driver = webdriver.Chrome()
welcomePage = driver.get("https://passport.weibo.com/")
time.sleep(3)
id = driver.find_element_by_name("username")
id.send_keys("13400062406")
time.sleep(3)
password = driver.find_element_by_name("password")
password.send_keys("s123456!")
time.sleep(3)
login = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div[2]/form/div[2]/div/ul/li[7]/div[1]/input")
login.click()
time.sleep(10)
search = driver.find_element_by_xpath('/html/body/div[3]/div/div[3]/form/input[1]')
search.send_keys("UIC")
search = driver.find_element_by_xpath('/html/body/div[3]/div/div[3]/form/input[2]')
search.click()
time.sleep(5)
handles = driver.window_handles
driver.switch_to.window(handles[1])
file = openpyxl.Workbook()
table=file.active
table.append(["words", "time"])
for i in range(1, 46):
    html_soup = BeautifulSoup(driver.page_source, "html.parser")
    print(driver.current_url)
    # div = html_soup.find('div', class_='m-wrap')
    count = 0
    for div1 in html_soup.find_all('div', class_="card-feed"):
        if count > 20:
            break
        wo = div1.find('p', class_='txt').text.strip().split('展开全文')[0]
        da = div1.find('p', class_='from').text.strip().split("\n")[0]
        if da.find("年") == -1:
            da = "2021年"+da
        if da.find("转赞") != -1:
            da = da[0:da.find("转赞")]
        da=da.rstrip()
        count += 1
        table.append([wo,da])
    nex_page = driver.find_element_by_class_name("next")
    nex_page.click()
    time.sleep(random.randint(3,6))
file.save("Weibo_result.xlsx")
file.close()
driver.close()
