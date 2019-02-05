from selenium import webdriver
from selenium.webdriver.common.action_chains import *
import time
import pandas as pd

class grabber(object):
    def __init__(self, url = 'http://ticket.gdcd.gov.cn:8010/IndustryData/Vehicle', txtfilepath = 'list_9.txt'):
        self.url = url
        self.txtfile = txtfilepath
        self.browser = webdriver.Firefox() # firefox
        self.plates = []
        self.result = []
        self.result_cols = []
        # open web page
        self.browser.get(url)
        self.home_tag = self.browser.current_window_handle

    def read_data(self):
        with open(self.txtfile, 'r') as f:
            for line in f:
                self.plates.append(line.replace('\n', '')) # remove '\n'

    def submit_search_content(self, content):
        # find search box:
        search_box = self.browser.find_element_by_id('chepaihao')
        # clear search box:
        search_box.clear()
        # enter vehicle plate in search box:
        search_box.send_keys(str(content))
        # find submit button:
        button = self.browser.find_element_by_class_name("btn_2.m_r_10")
        # avoid float image:
        try:
            #button.click()
            #self.browser.execute_script("document.getElementsByClassName('btn_2.m_r_10')[0].click()")
            #self.browser.execute_script("""$("btn_2.m_r_10").click(function(){})""")
            self.browser.execute_script("(arguments[0]).click()", button)
        except Exception as E:
            print(E)
            print('refresh')
            self.browser.refresh()
            time.sleep(10)
            self.submit_search_content(content)

    # function for get the table values in home tag
    def grab_on_home_tag(self):
        try:
            # wait long enough for the search results be loaded, if grab empty content, errors will come out
            time.sleep(1.5)
            # find data table
            table = self.browser.find_element_by_class_name('data_table') # to ensure no same name 'tbody' in data_table
            # find table body
            table_body = table.find_element_by_tag_name('tbody') # only use elements when next step is iter
            # find all the values in the table
            values = table_body.find_elements_by_tag_name('td')
            self.home_tag_values = values
        except Exception as E:
            print('home page Error:{}'.format(E))
            time.sleep(5)
            self.grab_on_home_tag()

    # function for click the detial button:
    def grab_detail(self):
        # find the detail button in all values
        for value in self.home_tag_values:
            if value.text == '详细':
                # click the button to open the detailed tag
                value.click()
                #self.browser.execute_script("(arguments[0]).onclick()", value)
                # switch to new tag:
                time.sleep(1.5)
                tags = self.browser.window_handles
                # find new tag and switch to it
                for tag in tags:
                    if tag != self.home_tag:
                        # switch to new opened tag
                        self.browser.switch_to_window(tag)
                # grab in new tag
                self.grab_on_new_tag()

    # function for grab on new tag
    def grab_on_new_tag(self):
        try:
            # find the detailed table
            table = self.browser.find_element_by_class_name("info_table")
            # find heads in first step:
            if len(self.result_cols) == 0:
                # find all head values
                table_heads = table.find_elements_by_tag_name("th")
                for head in table_heads:
                    self.result_cols.append(head.text)
            # find all table values as a row in result
            table_values = table.find_elements_by_tag_name("td")
            row_data = []
            for item in table_values:
                row_data.append(item.text)
            # save to result
            self.result.append(row_data)
            # close the tag
            self.browser.close()
            # switch back to home tag
            self.browser.switch_to_window(self.home_tag)
        except Exception as E:
            print('new page Error:{}'.format(E))
            # **switch to home tag if needed (if not the click action cannot be done and will keep recursiving)
            time.sleep(5)
            self.grab_on_new_tag()
        

    def result2CSV(self):
        self.result = pd.DataFrame(self.result)
        self.result.columns = self.result_cols
        self.result.to_csv('result.csv', encoding='utf-8')


    def run_single_plate(self, step):
        try:
            self.submit_search_content(self.plates[step])
            self.grab_on_home_tag()
            self.grab_detail()
        except:
            # switch to home tag:
            self.browser.switch_to_window(self.home_tag)
            # refresh
            self.browser.refresh()
            time.sleep(15)
            self.run_single_plate(step)

    # main loop:
    def run(self):
        self.read_data()
        # loop for every plate:
        step = 0 # record step for rerun 
        while step < len(self.plates):
            # hang mouse to stop the floating image
            #floating_image = self.browser.find_element_by_id('floatImg')
            #ActionChains(self.browser).move_to_element(floating_image).perform()
            MyGrabber.run_single_plate(step)
            step += 1
            print('done {} out of {}'.format(step, len(self.plates)))
        self.result2CSV()


if __name__ == '__main__':
    MyGrabber = grabber()
    MyGrabber.run()