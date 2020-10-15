
# -*- coding: utf-8 -*-

'''
name:       wos_spider.py
usage:      --
author:     Ruicheng
date:       2020-10-14 21:06:12
version:    1.0
Env.:       Python 3.7.3, WIN 10
'''

import time
import random
from selenium import webdriver
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.keys import Keys

# url
root_url = 'https://apps.webofknowledge.com'

# start browser
options = webdriver.ChromeOptions()
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
driver = webdriver.Chrome(options=options)
driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
    "source": """
    Object.defineProperty(navigator, 'webdriver', {
      get: () => undefined
    })
  """
})


driver.get(root_url)
title = driver.title
print(title)
time.sleep(3)



paper1 = 'Level set formulation for automatic medical image segmentation based on fuzzy clustering'

driver.find_element_by_xpath('//*[@id="addSearchRow1"]/a').click()

driver.find_element_by_xpath('//*[@id="value(input1)"]').send_keys(
    'Level set formulation for automatic medical image segmentation based on fuzzy clustering')
s1 = Select(driver.find_element_by_xpath('//*[@id="select1"]'))
s1.select_by_visible_text('标题')

driver.find_element_by_xpath('//*[@id="value(input1)"]').send_keys(paper1)
s1 = Select(driver.find_element_by_xpath('//*[@id="select1"]'))
s1.select_by_visible_text('标题')

driver.find_element_by_xpath('//*[@id="value(input2)"]').send_keys('Yang, Yunyun')
s2 = Select(driver.find_element_by_xpath('//*[@id="select2"]'))
s2.select_by_visible_text('作者')


driver.find_element_by_id('searchCell2').click()

driver.find_element_by_id('_summary_checkbox_1').send_keys(Keys.SPACE)
driver.find_element_by_id('markedListButton').click()

driver.find_element_by_xpath('//*[@id="RECORD_1"]/div[3]/div/div[1]/div/a').click()

driver.find_element_by_xpath('//*[@id="show_journal_overlay_link_1"]/p/a').click()
# time.sleep(3.14)
# driver.find_element_by_id('RECORD_1').text
# rc1 = driver.find_element_by_id('RECORD_1')
# paper_title = rc1.find_element_by_xpath('div[3]/div/div[1]').text

# 期刊
driver.find_element_by_css_selector('a.focusable-link').click()
driver.find_element_by_id('show_journal_overlay_1').text
driver.find_element_by_css_selector('#show_journal_overlay_1 > p.closeWindow > button').click()

# 引用次数 0 次
driver.find_element_by_css_selector('.flex-row-partition1 > sapn').text

# 引用次数 大于0
driver.find_element_by_css_selector('.flex-row-partition1 > a').text
driver.find_element_by_css_selector('.flex-row-partition1 > a').click()

# 返回搜索页
driver.find_element_by_xpath('//*[@id="skip-to-navigation"]/ul[1]/li[1]/a').click()

# 所有页面信息
driver.find_element_by_id('records_form').text.split('\n')

# 被引用的下一页
driver.find_element_by_css_selector('#paginationForm2 > span > a.paginationNext.snowplow-navigation-nextpage-bottom').click()

# 页码
driver.find_element_by_id('paginationForm2').text

