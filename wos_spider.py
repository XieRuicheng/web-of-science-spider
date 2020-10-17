
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
import yaml
import random
import logging

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select

from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.common.exceptions import TimeoutException, ElementNotInteractableException


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

desired_capabilities = DesiredCapabilities.CHROME
desired_capabilities["pageLoadStrategy"] = "none"

# start browser
def initial_driver():
    options = webdriver.ChromeOptions()
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(30)
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
        Object.defineProperty(navigator, 'webdriver', {
        get: () => undefined
        })
    """
    })
    return driver


def log_in(email, passwd):
    driver.find_element_by_id('signin').click()
    driver.find_element_by_xpath('/html/body/div[1]/div[22]/ul[2]/li[1]/ul/li[1]/a').click()
    driver.find_element_by_id('email').send_keys(email)
    driver.find_element_by_id('password').send_keys(passwd)
    driver.find_element_by_id('signInButton').click()


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


def get_journal_info():
    # page number
    current_page, *_ = get_page_num()


    # click journal info button
    try:
        driver.find_element_by_css_selector('a.focusable-link').click()
    except ElementNotInteractableException:
        logger.info(f'Cannot find JCR report')
        return 0, 'NA', [], 'NA'

    cite_text = driver.find_element_by_id(f'show_journal_overlay_{current_page}').text

    # extract IF and JCR Rank
    # TODO: select rank in MATH or Image
    impact_factor = [float(x) for x in cite_text.split('\n')[2].split()] # [this year, 5 year]
    jcr_rank = cite_text.split('\n')[5].split()[-1]

    logger.info(f'Journal IF is {impact_factor[0]}, JCR rank is {jcr_rank}')

    # JCR sort
    jcr_sort = re.search('分区(.*?)数据来自', cite_text, re.DOTALL)
    if jcr_sort:
        jcr_sort = [x.strip() for x in jcr_sort.group(1).split('\n')]
        jcr_sort = list(filter(len, jcr_sort))
        logger.debug(f'JCR Sort is {jcr_sort}')
    else:
        logger.error('JCR Sort RE error')

    # close journal info window
    random_sleep(mu=2)
    driver.find_element_by_css_selector(f'#show_journal_overlay_{current_page} > p.closeWindow > button').click()

    return impact_factor[0], jcr_rank, jcr_sort, cite_text


def get_citation_num():
    cite_num_text = driver.find_element_by_class_name('flex-row-partition1').text
    cite_num = int(cite_num_text.split('\n')[0])
    logger.info(f'Cited by {cite_num} papers')
    return cite_num


def back_to_main():
    # back to search page
    driver.find_element_by_xpath('//*[@id="skip-to-navigation"]/ul[1]/li[1]/a').click()


def get_page_num():
    # page number
    page_num_text = driver.find_element_by_id('paginationForm2').text

    page_group = re.search('第 (\d+) 条，共 (\d+) 条', page_num_text)
    current_page = int(page_group.group(1))
    total_page = int(page_group.group(2))

    return current_page, total_page, page_num_text


def go_to_next_cite():
    # page number
    current_page, total_page, page_num_text = get_page_num()
    logger.info(f'Processing citation in {page_num_text}')

    if current_page < total_page:
        # click next page
        driver.find_element_by_css_selector(
            '#paginationForm2 > span > a.paginationNext.snowplow-navigation-nextpage-bottom'
        ).click()
    else:
        logger.debug('In the last page')

    return 0


def random_sleep(mu=5, sigma=2, min_time=3, max_time=15):
    sleep_time = random.normalvariate(mu, sigma)
    sleep_time = max(sleep_time, min_time)
    sleep_time = min(sleep_time, max_time)
    logger.debug(f'Sleeping {sleep_time}s')
    time.sleep(sleep_time)


def verify_title(web_title, given_title):
    return True


def wait_find(driver, loc_m, loc):
    return WebDriverWait(driver, 120).until(EC.visibility_of_element_located((loc_m, loc)))


def wait_find_all(driver, loc_m, loc):
    try:
        elem = WebDriverWait(driver, 30).until(EC.visibility_of_all_elements_located((loc_m, loc)))
    except TimeoutException:
        elem = []
    return elem


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
        # remove prefix like '[ 1 ] ', using ^ to avoid inside []
        address = [re.sub('^\s*\[\s*?\d+?\s*?\]\s*', '', x) for x in address]
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

    record_chunks = wait_find_all(driver, By.CLASS_NAME, 'search-results-item')
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
            detail_link = wait_find_all(driver, By.CLASS_NAME, 'search-results-item')[idx]
            detail_link = wait_find(detail_link, By.XPATH, 'div[3]/div/div[1]/div/a')
            break

    # no matched paper found
    if detail_link == None:
        logger.warning(f'Cannot find paper: {paper}')
        # result dict
        search_result = {
            'Paper': paper,
            'SearchTitle': 'NA',
            'IF': 'NA',
            'Rank': 'NA',
            'Sort': [],
            'Citation': 'NA',
            'CiteDetail': [],
            'Journal': 'NA',
            'address': 'NA',
            'authors': 'NA',
            'date': 'NA',
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
    record_detail_text = wait_find(driver, By.ID, 'records_form').text

    # journal IF
    impact_factor, jcr_rank, jcr_sort, cite_text = get_journal_info()

    # citation number
    cite_num = get_citation_num()

    # save record
    record_path = os.path.join(record_folder, paper.replace(':', '-'))
    with open(record_path, 'w', encoding='utf8') as fp:
        fp.write(record_brief_text)
        fp.write(f'\nIF: {impact_factor}, RANK: {jcr_rank}, Citaion: {cite_num}\n\n')
        fp.write(cite_text)
        fp.write(record_detail_text)

    # extract journal, author, address from record
    record_info_dict = get_cite_detail(record_detail_text)

    # result dict
    search_result = {
        'Paper': paper,
        'SearchTitle': record_title_text,
        'IF': impact_factor,
        'Rank': jcr_rank,
        'Sort': jcr_sort,
        'Citation': cite_num,
        'CiteDetail': [],
        'Journal': record_info_dict['journal'],
        'address': record_info_dict['address'],
        'authors': record_info_dict['authors'],
        'date': record_info_dict['date'],
    }

    # end searching if no citation
    if cite_num == 0:
        # go back to main search page
        back_to_main()
        return search_result

    random_sleep()

    # ------------------------------------------------------------ #
    # follow link if the paper is cited
    # ------------------------------------------------------------ #

    # click citation number
    wait_find(driver, By.CSS_SELECTOR, '.flex-row-partition1 > a').click()
    random_sleep()

    # go to the detail page of first cite paper, if citation library is book
    cite_chunks = driver.find_elements_by_xpath('//*[@id="RECORD_1"]/div[3]/div/div[1]/div/a')
    if len(cite_chunks) > 0:
        cite_chunks[0].click()
    elif len(driver.find_elements_by_id('noRecordsDiv')) > 0:
        cite_error_text = driver.find_elements_by_id('noRecordsDiv')
        logger.warning(f'Citation is not booked: {cite_error_text[0].text}')
    else:
        logger.error('Citation page abnormal')
    random_sleep()

    # ------------------------------------------------------------ #
    # in citation detail page
    # ------------------------------------------------------------ #

    # cite info
    cite_detail = []
    for aa in range(cite_num):
        # Title, author, address of citing paper
        cite_detail_text = wait_find(driver, By.ID, 'records_form').text
        cite_info = get_cite_detail(cite_detail_text)
        # JCR info of citing paper
        cite_if, cite_jcr_rank, cite_jcr_sort, _ = get_journal_info()
        cite_info['IF'] = cite_if
        cite_info['Rank'] = cite_jcr_rank
        cite_info['Sort'] = cite_jcr_sort
        cite_detail.append(cite_info)
        go_to_next_cite()
        random_sleep(mu=8)

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

    # login for H-Index
    # log_in('x_rc@qq.com', 'Wos123%890')
    # random_sleep()

    # read paper list
    with open('杨云云发表论文清单.txt', 'r', encoding='utf8') as fp:
        paper_list = fp.readlines()
        paper_list = [x.strip() for x in paper_list]

    # make record folder
    record_folder = f'./logs/{time_stamp}'
    os.mkdir(record_folder)

    total_paper = len(paper_list)
    result_list = []
    for aa, paper in enumerate(paper_list):
        # if aa + 1 < 12:
        #     continue
        logger.info(f'Processing {aa + 1} in {total_paper}')
        result = search_paper_info(paper, record_folder)
        result_list.append(result)

    # save to YAML file
    result_dict = {f'paper{aa+1}': x for aa, x in enumerate(result_list)}
    with open(f'./result/{time_stamp}_result.yaml', 'w') as fp:
        yaml.dump(result_dict, fp)

    # citation report
    # driver.find_element_by_xpath('//*[@id="skip-to-navigation"]/ul[2]/li[4]/a').click()
