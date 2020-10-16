
# -*- coding: utf-8 -*-

'''
name:       wos_spider.py
usage:      --
author:     Ruicheng
date:       2020-10-14 21:06:12
version:    1.0
Env.:       Python 3.7.3, WIN 10
'''

import os
import re
import time
import random
import logging

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException


# logging configuration
logger = logging.getLogger('wos_spider_logger')
if (logger.hasHandlers()):
    logger.handlers.clear()
logger.setLevel('DEBUG')
BASIC_FORMAT = '[%(asctime)s - %(levelname)s]: %(message)s'
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
formatter = logging.Formatter(BASIC_FORMAT, DATE_FORMAT)
# console logger handler
chlr = logging.StreamHandler()
chlr.setFormatter(formatter)
chlr.setLevel('INFO')
# file logger handler
time_stamp = time.strftime('%b%d_%H_%M', time.localtime())
fhlr = logging.FileHandler(f'logs/wos_spider_{time_stamp}.log')
fhlr.setFormatter(formatter)
fhlr.setLevel('DEBUG')
# set logger handler
logger.addHandler(chlr)
logger.addHandler(fhlr)

# url
root_url = 'https://apps.webofknowledge.com'

# start browser
def initial_driver():
    options = webdriver.ChromeOptions()
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(10)
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
        Object.defineProperty(navigator, 'webdriver', {
        get: () => undefined
        })
    """
    })
    return driver


def search_paper(paper_title, author='Yang, Yunyun'):
    logger.info(f'Processing {paper}')
    # add a search row if there only exist one
    add_row_button = driver.find_element_by_xpath('//*[@id="addSearchRow1"]/a')
    if add_row_button.text == '+ 添加行':
        add_row_button.click()
        logger.info('Add new line in search block')
    random_sleep(mu=1)

    # put paper title
    input1 = driver.find_element_by_xpath('//*[@id="value(input1)"]')
    input1.clear()
    input1.send_keys(paper_title)
    s1 = Select(driver.find_element_by_xpath('//*[@id="select1"]'))
    s1.select_by_visible_text('标题')

    # put author name
    input2 = driver.find_element_by_xpath('//*[@id="value(input2)"]')
    input2.clear()
    input2.send_keys(author)
    s2 = Select(driver.find_element_by_xpath('//*[@id="select2"]'))
    s2.select_by_visible_text('作者')
    random_sleep(mu=1)

    # click search
    driver.find_element_by_id('searchCell2').click()


def add_to_monitor(num):
    checkbox = driver.find_element_by_id(f'_summary_checkbox_{num}')
    if not checkbox.is_selected():
        checkbox.send_keys(Keys.SPACE)
        driver.find_element_by_id('markedListButton').click()


def get_journal_info(idx):
    try:
        # click journal info button
        driver.find_element_by_css_selector('a.focusable-link').click()
        cite_text = driver.find_element_by_id(f'show_journal_overlay_{idx}').text

        # extract IF and JCR Rank
        impact_factor = [float(x) for x in cite_text.split('\n')[2].split()] # [this year, 5 year]
        jcr_rank = cite_text.split('\n')[5].split()[-1]

        logger.info(f'Journal IF is {impact_factor[0]}, JCR rank is {jcr_rank}')

        # close journal info window
        random_sleep(mu=2)
        driver.find_element_by_css_selector(f'#show_journal_overlay_{idx} > p.closeWindow > button').click()
        return impact_factor[0], jcr_rank, cite_text

    except ElementNotInteractableException:
        logger.info(f'Cannot find JCR report')
        return 0, None, None


def get_citation_num():
    cite_num_text = driver.find_element_by_class_name('flex-row-partition1').text
    cite_num = int(cite_num_text.split('\n')[0])
    logger.info(f'Cited by {cite_num} papers')
    return cite_num


def back_to_main():
    # back to search page
    driver.find_element_by_xpath('//*[@id="skip-to-navigation"]/ul[1]/li[1]/a').click()


def go_to_next_cite():
    # page number
    page_num = driver.find_element_by_id('paginationForm2').text
    logger.info(f'Processing citation in {page_num}')
    # click next page
    driver.find_element_by_css_selector('#paginationForm2 > span > a.paginationNext.snowplow-navigation-nextpage-bottom').click()


def random_sleep(mu=3, sigma=1, min=1):
    sleep_time = random.normalvariate(mu, sigma)
    sleep_time = max(sleep_time, min)
    time.sleep(sleep_time)


def verify_title(web_title, given_title):
    return True


def get_cite_detail(record_detail_text):
    
    address = []
    # locate address block
    address_block = re.search('地址:(((?!地址).)*?)电子邮件', record_detail_text, re.DOTALL)
    if address_block:
        address = address_block.group(1)
        # remove prefix like '\n[ 1 ]', using \n to avoid inside []
        address = re.sub('\n\[\s*?\d+?\s*?\]', '', address)
        # split to single address
        address = [x.strip() for x in address.split('\n')]
        address = list(filter(len, address))
        logger.debug(f'address: {address}')
    else:
        logger.error('No address found')

    authors = []
    # locate author block
    author_block = re.search('作者:(.*)', record_detail_text)
    if author_block:
        # split into single author
        for author in author_block.group(1).split(';'):
            # find the full name of author
            author_fullname = re.search('\((.*?)\)', author)
            if author_fullname:
                author = author_fullname.group(1)
            else:
                logger.warning(f'Author: {author} do not have full name')
            authors.append(author)
        logger.debug(f'authors: {authors}')
    else:
        logger.error('No author found')

    date = 'NA'
    # locate date
    date_block = re.search('((出版年)|(日期)):?\s*(.*)', record_detail_text)
    if date_block:
        date = date_block.group(4)
        logger.debug(f'date: {date}')
    else:
        logger.error('No date found')
    
    title = 'NA'
    # Title is the first row
    title_block = re.search('.*', record_detail_text)
    if title_block:
        title = title_block.group()
        logger.debug(f'title: {title}')
    else:
        logger.error('No title found')

    if record_detail_text.split('\n')[2] == '查看 Web of Science ResearcherID 和 ORCID':
        journal = record_detail_text.split('\n')[3]
    else:
        journal = record_detail_text.split('\n')[2]

    paper_info = {
        'title': title,
        'journal': journal,
        'address': address,
        'authors': authors,
        'date': date,
    }

    return paper_info


def search_paper_info(paper, record_folder):
    # search paper
    search_paper(paper)
    random_sleep(mu=5)

    # ------------------------------------------------------------ #
    # in search page
    # ------------------------------------------------------------ #

    idx = None               # paper rank in search page
    detail_link = None       # matched datail page link
    record_title_text = None # paper title
    record_brief_text = 'NA' # brief information of paper

    record_chunks = driver.find_elements_by_class_name('search-results-item')
    for idx, record in enumerate(record_chunks):
        # text of whole record, include title, author, journal, data, citation num
        record_brief_text = record.text
        # title object of record, which link to detail page
        record_title = record.find_element_by_xpath('div[3]/div/div[1]/div/a')
        record_title_text = record_title.text
        # Check the matching of the given paper title and current record
        if verify_title(record_title_text, paper) == True:
            # add record to monitor to obtain H-index
            add_to_monitor(idx + 1)
            # record detail link
            detail_link = driver.find_elements_by_class_name('search-results-item')[idx]
            detail_link = detail_link.find_element_by_xpath('div[3]/div/div[1]/div/a')
            break

    # no matched paper found
    if detail_link == None:
        logger.warning(f'Cannot find paper: {paper}')
        # result dict
        search_result = {
            'Paper': paper,
            'SearchTitle': None,
            'IF': None,
            'Rank': None,
            'Citation': None,
            'CiteDetail': [],
        }
        return search_result

    # random_sleep()

    # go into detail page
    detail_link.click()

    random_sleep()

    # ------------------------------------------------------------ #
    # in detail page
    # ------------------------------------------------------------ #

    # text of whole record page
    record_detail_text = driver.find_element_by_id('records_form').text

    # journal IF
    impact_factor, jcr_rank, _ = get_journal_info(idx + 1)

    # citation number
    cite_num = get_citation_num()

    # save record
    record_path = os.path.join(record_folder, paper.replace(':', '-'))
    with open(record_path, 'w', encoding='utf8') as fp:
        fp.write(record_brief_text)
        fp.write(f'\nIF: {impact_factor}, RANK: {jcr_rank}, Citaion: {cite_num}\n\n')
        fp.write(record_detail_text)

    # result dict
    search_result = {
        'Paper': paper,
        'SearchTitle': record_title_text,
        'IF': impact_factor,
        'Rank': jcr_rank,
        'Citation': cite_num,
        'CiteDetail': [],
    }

    # end searching if no citation
    if cite_num == 0:
        # go back to main search page
        back_to_main()
        return search_result

    random_sleep(mu=1)

    # ------------------------------------------------------------ #
    # follow link if the paper is cited
    # ------------------------------------------------------------ #

    # click citation number
    driver.find_element_by_css_selector('.flex-row-partition1 > a').click()
    random_sleep()
    # go to the detail page of first cite paper
    driver.find_element_by_xpath('//*[@id="RECORD_1"]/div[3]/div/div[1]/div/a').click()
    random_sleep()

    # ------------------------------------------------------------ #
    # in citation detail page
    # ------------------------------------------------------------ #

    # cite info
    cite_detail = []
    for aa in range(cite_num):
        cite_detail_text = driver.find_element_by_id('records_form').text
        cite_info = get_cite_detail(cite_detail_text)
        cite_detail.append(cite_info)
        if aa < cite_num-1:
            go_to_next_cite()
        random_sleep(mu=5)

    search_result['CiteDetail'] = cite_detail

    # go back to main search page, now finish a search cycle
    back_to_main()


    return search_result


if __name__ == '__main__':
    # initial driver and open website
    driver = initial_driver()
    driver.get(root_url)
    title = driver.title
    print(title)
    random_sleep()

    # read paper list
    with open('杨云云发表论文清单.txt', 'r', encoding='utf8') as fp:
        paper_list = fp.readlines()
        paper_list = [x.strip() for x in paper_list]
    # paper_list = [
    #     'Ultrasound pupil image segmentation based on edge detection and detection operators',
    #     'Level set formulation for automatic medical image segmentation based on fuzzy clustering',
    #     'A Novel Clustering Method for Static Video Summarization',
    #     'Split Bregman Method for Minimization of Fast Multiphase Image Segmentation Model for Inhomogeneous Images',
    # ]

    # make record folder
    record_folder = f'./logs/{time_stamp}'
    os.mkdir(record_folder)

    result_list = []
    for paper in paper_list:
        result = search_paper_info(paper, record_folder)
        result_list.append(result)
