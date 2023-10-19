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


ALL_CATEGORIES_LINK = 'https://www.amazon.com/Best-Sellers/zgbs/ref=zg_bs_unv_photo_0_499234_4'
MAIN_DOMAIN = 'https://www.amazon.com'
ZIP_CODE = '94016'

# ADS vars
API_KEY = ''
HOST_URL = 'http://local.adspower.com:50325'
USER_ID = ''
headers = {
    'Authorization': f'Bearer {API_KEY}'
}
open_browser_url = '{HOST_URL}/api/v1/browser/start?user_id={USER_ID}'
# # # # # #

def refact_name_item(name):
    return name.replace(' ', '_')

def browser_init():
    browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    return browser

def get_ads_profile(uid = USER_ID, host_url = HOST_URL):
    resp = requests.get(open_browser_url.format(HOST_URL=host_url, USER_ID=uid), headers=headers)
    return resp.json()

def ads_browser_init(resp):
    print(resp["data"]["webdriver"])
    chrome_driver = resp["data"]["webdriver"]
    chrome_options = Options()
    chrome_options.add_experimental_option("debuggerAddress", resp["data"]["ws"]["selenium"])
    browser = webdriver.Chrome(chrome_driver, options=chrome_options)
    # browser = webdriver.Chrome(service=Service(ChromeDriverManager(driver_version=chrome_driver).install()), options=chrome_options)
    return browser

def soup_initial(browser):
    return BeautifulSoup(browser.page_source, 'html.parser')

def get_json_data(name_ind, path = './'):
    with open(f'{path}{name_ind}.json', 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data

def set_json_data(data, name_ind, path = './'):
    with open(f'{path}{name_ind}.json', 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False)

def set_zip_code(browser, zip_code):
    zp_popup = browser.find_element(By.ID, 'nav-global-location-slot').find_element(By.TAG_NAME, 'span')
    browser.execute_script("arguments[0].click();", zp_popup)

    time.sleep(2)

    zp_input = browser.find_element(By.CLASS_NAME, 'GLUX_Full_Width')
    zp_input.send_keys(zip_code)
    zp_input.send_keys(Keys.ENTER)

    time.sleep(1)
    
    zp_btn = browser.find_element(By.ID, 'GLUXConfirmClose')
    browser.execute_script("arguments[0].click();", zp_btn)

def get_node(url):
    try:
        return int(url.split('/')[-2])
    except:
        exec
    try:
        return int(url.split('/')[-1].split('_')[-1])
    except:
        exec
    return url
