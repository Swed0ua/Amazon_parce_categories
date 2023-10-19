import sys
import requests
from bs4 import BeautifulSoup
import time
import json
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import codecs

from main import browser_init, ads_browser_init, get_ads_profile, get_json_data, set_zip_code, soup_initial, refact_name_item, set_json_data, get_json_data, get_node
from main import ALL_CATEGORIES_LINK, ZIP_CODE, MAIN_DOMAIN

def select_deps_type (soup):
    deps = []
    try:
        deps = soup.find(id='s-refinements').find(class_='a-section').find('ul').find_all('li', class_='apb-browse-refinements-indent-2')
    except:
        exec
    try:
        deps = soup.find(id='departments').find('ul').find_all("li", class_='s-navigation-indent-2')
    except:
        exec
    return deps

def get_cat_path(soup):
    text = ''
    try:
        list = soup.find(id='departments').find('ul').find_all("li", class_='a-spacing-micro')
        for item in list:
            if 's-navigation-indent-2' in item.get("class"):
                break
            text += item.text.strip() + "/"
            if 's-navigation-indent-1' in item.get("class"):
                break
    except:
        exec

    try:
        if text == '':
            list_selections =  soup.find(id='s-refinements').find_all(class_='a-section')
            for list_selection in list_selections:
                selection_name = list_selection.find('span').text.strip()
                if selection_name == 'Department':
                    list =  list_selection.find('ul').find_all('li', class_='a-spacing-micro')
                    for item in list:
                        if 'apb-browse-refinements-indent-2' in item.get("class"):
                            break
                        text += item.text.strip() + "/"
    except:
        exec


    text_format = text.replace(' ', "_").replace('Any_Department/', '').replace('\n', '').strip()
    return text_format

def get_all_products(browser) :
    try:
        products_list = browser.find_element(By.CLASS_NAME, 's-result-list').find_elements(By.CLASS_NAME, 's-result-item')
    except:
        products_list = []
    products = {
        "list" :[]
    }
    min_price = ''
    max_price = 0
    medium_price = 0
    sum_prices = 0
    print('product analiz...')
    for product_item in products_list:
        try:
            try:
                if 's-search-result' in product_item.get_attribute('data-component-type'):
                    exec
                else:
                    continue
            except:
                continue
            product = {}

            product_info = product_item.find_element(By.TAG_NAME, 'h2').find_element(By.TAG_NAME, 'a')
            
            try:
                product_price = product_item.find_element(By.CLASS_NAME, 'a-price').text.replace(' ', '').replace('\n', '.').strip()
            except:
                product_price = '' 
                
            # print(product_info.text.strip())
        
            product['asin'] = product_item.get_attribute('data-asin')
            product['title'] = product_info.text.strip()
            product['href'] = product_info.get_attribute('href')
            product['img'] = product_item.find_element(By.TAG_NAME,'img').get_attribute('src')
            product['srcset'] = product_item.find_element(By.TAG_NAME,'img').get_attribute('srcset')
            product['price'] = product_price
            products['list'].append(product)
            if product_price!='':
                product_price = float(product_price.replace('$', '').replace(',', '').strip())
                if min_price == '':
                    min_price = product_price
                if min_price > product_price:
                    min_price = product_price
                if max_price < product_price:
                    max_price = product_price
                sum_prices += product_price
        except:
            exec
    try:
        medium_price = sum_prices/len(products_list)
    except:
        exec
    products['max_price'] = max_price
    products['min_price'] = min_price
    products['medium_price'] = medium_price
    return products


def get_cat_items():
    # BD with parces items
    inds_data = get_json_data('ids', './names/')
    path_data = get_json_data('names', './names/')
    wlinks_data = get_json_data('l')


    # Open Profile browser
    ads_prof_data = get_ads_profile()
    browser = ads_browser_init(ads_prof_data)
    browser.get(ALL_CATEGORIES_LINK)
    time.sleep(1)
    start_pos = 430 #430 250   #2035 2900


    score = start_pos + 1 
    for link_dt_ind in range(start_pos,len(wlinks_data)):
        link_dt = wlinks_data[link_dt_ind]
        link = link_dt[0]
        obj = {}
        # Get node id with Link page
        node = get_node(link)
        if node != 0:
            cat_link = f'https://www.amazon.com/b?node={node}'
        else:
            cat_link = link
            node = link.split(MAIN_DOMAIN)[-1].split('/')[1].replace('Best-Sellers-', '')
        print(f'{node} | # {score} | Scraping new elment - {cat_link}')

        if node in inds_data:
            obj = get_json_data(node,'./3/')
            print('This item is scrap brfore')
        else:
            browser.get(cat_link)
            soup = soup_initial(browser)
            deps = select_deps_type(soup)
            try:
                cat_path = get_cat_path(soup)
            except:
                cat_path = ''

            obj['link'] = cat_link
            obj['PATH'] = cat_path
            obj['child_nodes'] = []
            obj['child_links'] = []


            # Get all subcategories and write their links
            try:
                for dep in link_dt[1]:
                    full_dep_link = dep[0]
                    dep_node = get_node(full_dep_link)
                    obj['child_nodes'].append(dep_node)
                    obj['child_links'].append(full_dep_link)
            except:
                exec

            filtr_element = None
            see_all_btn = None
            # Check if page have see all button
            try:
                see_all_btn = browser.find_element(By.ID, 'apb-desktop-browse-search-see-all')
                see_all_url = see_all_btn.get_attribute('href')
                browser.get(see_all_url)
                print(f'All res in {see_all_url}')
            except:
                exec

            # Check if have sort select a block
            def get_filtr_element(browser):
                try:
                    filtr_element = browser.find_element(By.ID, 's-result-sort-select')
                    # print(f'Filtr is {filtr_element}')
                except:
                    exec
                return filtr_element
            
            # Get all products in page with param:SORT_BY
            obj['results'] = {}
            
            def param_switch(browser, param_ind):
                try:
                    filtr_element = get_filtr_element(browser)
                    browser.execute_script("arguments[0].click();", filtr_element) 
                    time.sleep(0.2)
                    filtr_params = browser.find_element(By.CLASS_NAME, 'a-popover-inner').find_elements(By.TAG_NAME, 'a')
                    browser.execute_script("arguments[0].click();", filtr_params[param_ind]) 
                    time.sleep(0.8)
                except Exception as e:
                    exec

            products_def = get_all_products(browser=browser)
            obj['results']['default'] = products_def
            param_switch(browser, 1)
            products_def = get_all_products(browser=browser)
            obj['results']['lows'] = products_def
            param_switch(browser, 2)
            products_def = get_all_products(browser=browser)
            obj['results']['highs'] = products_def


            # Get all params for results page
            def get_params(browser):
                dps = browser.find_element(By.ID,'s-refinements').find_elements(By.CLASS_NAME, 'a-spacing-none')
                objs_param = {}
                for dp in dps:
                    obj = []
                    soup_dp = BeautifulSoup(dp.get_attribute('outerHTML'), 'html.parser')
                    title = soup_dp.find('span').text.strip()
                    if 'Department' in title:
                        continue
                    values = soup_dp.find_all('li')
                    for value in values:
                        value_text = value.text.strip()
                        obj.append(value_text)
                    objs_param[title] = obj
                return objs_param

            try:
                obj['params'] = get_params(browser)
            except Exception as e:
                exec

        obj['node_id'] = node

        set_json_data(obj, obj['node_id'], './jsons/')
        score += 1
get_cat_items()

