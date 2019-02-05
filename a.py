from selenium import webdriver
import time
import pandas as pd
cols = ['']
url = 'http://ticket.gdcd.gov.cn:8010/IndustryData/Vehicle'
browser = webdriver.Firefox()
browser.get(url)
home_tag = browser.current_window_handle


input_str = browser.find_element_by_id('chepaihao')
input_str.send_keys("124432")
#input_str.clear()
#input_str.send_keys("MakBook pro")


# submit button:
# btn_2.m_r_10( mouse hang tag beside button ) not btn_2 m_r_10 (text show)
button = browser.find_element_by_class_name("btn_2.m_r_10")
button.click()
# reset button:
#button = browser.find_element_by_class_name('btn_3')

# find data table
time.sleep(2)
table = browser.find_element_by_class_name('data_table') # to ensure no same name 'tbody' in data_table
# find table body
table_body = table.find_element_by_tag_name('tbody') # only use elements when next step is iter
#print(table_body)
rows = table_body.find_elements_by_tag_name('tr') # only works in tbody! because thead has no tr
all_data = []
for r in rows:
    values = r.find_elements_by_tag_name('td')
    # find the button
    for value in values:
        if value.text == '详细':
            # open the button
            value.click()
            # switch to new tag:
            time.sleep(2)
            tags = browser.window_handles
            for tag in tags:
                if tag != home_tag:
                    # switch to new opened tag (make sure to switch, even if tag is switched apparently)
                    browser.switch_to_window(tag)
                    # find the table
                    table = browser.find_element_by_class_name("info_table")
                    # find heads in first step:
                    cols = []
                    table_heads = table.find_elements_by_tag_name("th")
                    for head in table_heads:
                        cols.append(head.text)
                    table_values = table.find_elements_by_tag_name("td")
                    # find values:
                    row_data = []
                    for value in table_values:
                        row_data.append(value.text)
                    all_data.append(row_data)
                    # switch back to home tag
                    browser.switch_to_window(home_tag)
print(cols)
all_data = pd.DataFrame(all_data)
all_data.columns = cols
print(all_data)




# data = []
# for r in rows:
#     values = r.find_elements_by_tag_name('td')
#     row = []
#     for value in values:
#         row.append(value.text)
#     data.append(row)

# print(data)
