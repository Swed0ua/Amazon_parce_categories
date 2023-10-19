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


file_path = os.path.abspath(__file__)
file_name = file_path.split('\\')[-1]
dir_path = file_path.replace(f'\\{file_name}', '')


LINK = 'https://www.amazon.com/b?node=2617941011'
site_domen = 'https://www.amazon.com'
API_KEY = ''
HOST_URL = 'http://local.adspower.com:50325'
USER_ID = ''

open_browser_url = f'{HOST_URL}/api/v1/browser/start?user_id={USER_ID}'


headers = {
    'Authorization': f'Bearer {API_KEY}'
}


def get_json_data(name_ind, path = './'):
    with open(f'{path}{name_ind}.json', 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data

def set_json_data(data, name_ind, path = './'):
    with open(f'{path}{name_ind}.json', 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False)


def browser_init(resp):
    print(resp["data"]["webdriver"])
    chrome_driver = resp["data"]["webdriver"]
    chrome_options = Options()
    chrome_options.add_experimental_option("debuggerAddress", resp["data"]["ws"]["selenium"])
    browser = webdriver.Chrome(chrome_driver, options=chrome_options)
    # browser = webdriver.Chrome(service=Service(ChromeDriverManager(driver_version=chrome_driver).install()), options=chrome_options)
    return browser

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
        list =  soup.find(id='s-refinements').find(class_='a-section').find('ul').find_all('li', class_='a-spacing-micro')
        for item in list:
            if 'apb-browse-refinements-indent-2' in item.get("class"):
                break
            text += item.text.strip() + "/"
    except:
        exec


    text_format = text.replace(' ', "_").replace('Any_Department/', '').replace('\n', '').strip()
    return text_format

def select_deps_type (soup):
    deps = None
    try:
        deps = soup.find(id='s-refinements').find(class_='a-section').find('ul').find_all('li', class_='apb-browse-refinements-indent-2')
    except:
        exec
    try:
        deps = soup.find(id='departments').find('ul').find_all("li", class_='s-navigation-indent-2')
    except:
        exec
    return deps

def soup_initial(browser):
    return BeautifulSoup(browser.page_source, 'html.parser')

def get_node_id (url):
    def get_node_name(triger):
        return url.split(triger)[-1].split('&')[0].strip()
    
    node_name = None
    if url.find('node') >= 0:
        node_name = get_node_name('node=')
    elif url.find('3A') >= 0:
        node_name = get_node_name('3A')
    
    return node_name


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

    medium_price = sum_prices/len(products_list)
    products['max_price'] = max_price
    products['min_price'] = min_price
    products['medium_price'] = medium_price
    return products


def program ():
    resp = requests.get(open_browser_url, headers=headers)
    print(resp.json())
    browser = browser_init(resp.json())
    links = [LINK] # turn links for scraping
    ind = 0 # index turn links
    while True:
        try:
            if ind >= len(links):
                break
            obj = {}
            cat_link = links[ind]
            browser.get(cat_link)
            set_json_data([ind, links], 'links')
            print(f' Scraping new elment - {cat_link}')
            ind += 1
            
            soup = soup_initial(browser)
            deps = select_deps_type(soup)
            try:
                cat_path = get_cat_path(soup)
            except:
                cat_path = ''
            current_url = browser.current_url
            node_id = get_node_id(current_url)
            
            # Check if {objs} is have {node_id} element
            objs_lite = get_json_data('cat')
            if node_id in objs_lite:
                continue
            
            obj['node_id'] = node_id
            obj['link'] = cat_link
            obj['PATH'] = cat_path
            obj['child_nodes'] = []
            obj['child_links'] = []

            # Get all subcategories and write their links
            
            for dep in deps:
                dep_link = dep.find('a').get('href')
                full_dep_link = site_domen + dep_link
                dep_node_id = get_node_id(full_dep_link)
                links.append(full_dep_link)
                obj['child_nodes'].append(dep_node_id)
                obj['child_links'].append(full_dep_link)
            
            
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

            # Check if have sort select ablock
            def get_filtr_element(browser):
                try:
                    filtr_element = browser.find_element(By.ID, 's-result-sort-select')
                    # print(f'Filtr is {filtr_element}')
                except:
                    exec
                return filtr_element
        
            filtr_element = get_filtr_element(browser)
            obj['results'] = {

            }

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
                print(e)
            
            set_json_data(obj, obj['node_id'], './jsons/')

            objs_lite = get_json_data('cat')
            objs_lite[node_id] = obj['link']
            set_json_data(objs_lite, 'cat')
            # print(links)
            
            ind += 1
            

        except Exception as e: 
            print(e)
            err = get_json_data('err')
            err.append([links[ind], str(e)])
            set_json_data(err, 'err')
            ind += 1

if __name__ == '__main__':
    program()