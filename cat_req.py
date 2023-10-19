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
from prg import get_cat_items


def get_parrent_categories(browser, mn_id = 'zg_left_col2'):
    soup = soup_initial(browser)
    cat_list = soup.find(id=mn_id).find('div', attrs={"role":"group"}).find_all('div', attrs={"role":"treeitem"})
    res = []
    try:
        for cat_item in cat_list:
            cat_name = cat_item.text.strip()
            cat_url_half = cat_item.find('a').get('href')
            cat_url_ful = f'{MAIN_DOMAIN}{cat_url_half}'
            par_refact_cat_name = refact_name_item(cat_name)
            # res.append([cat_url_ful, par_refact_cat_name, cat_name])
            res.append([cat_url_ful])
    except:
        res = []
    return res

def get_all_cat(i = 0):
    # Open Profile browser
    ads_prof_data = get_ads_profile()
    browser = ads_browser_init(ads_prof_data)
    browser.get(ALL_CATEGORIES_LINK)
    time.sleep(1)

    # par_cats = get_parrent_categories(browser)
    par_cats = get_json_data('lnks')
    
    

    for ind in range(i, i+1):
        par_cat =  par_cats[ind]
        par_cat_url = par_cat[0]
        par_cat_name = par_cat[1]
        par_refact_cat_name = refact_name_item(par_cat_name)
        print(f'Cat get {par_refact_cat_name} | {par_cat_url}')
        
        arr = [[par_cat_url]]
        s_ind = 0
        while True:
            try:
                if s_ind >= len(arr):
                    break
                # if len(arr) > 4000:
                #     break
                s_url = arr[s_ind][0]
                browser.get(s_url)
                
                # Get node id with Link page
                node = get_node(s_url)
                print(node)
                sub_arr = get_parrent_categories(browser, 'zg-left-col')
                arr += sub_arr
                arr[s_ind] = [arr[s_ind][0],sub_arr]
                print(arr[s_ind])
                print(len(arr))
            except:
                exec
            s_ind += 1


        # write all links from this category in Parce_Link BD
                    # l = get_json_data('l')
                    # l += arr
        set_json_data(arr, 'l')
        # get_cat_items()
get_all_cat(34) #8 16 22