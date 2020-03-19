import os
import time

import requests

# parse html
from bs4 import BeautifulSoup
# browser mok
from selenium import common, webdriver
# element location
from selenium.webdriver.common.by import By
# key mok to scroll the body of html
from selenium.webdriver.common.keys import Keys

option = webdriver.ChromeOptions()
# open chorme silently
option.add_argument('headless')
browser = webdriver.Chrome(chrome_options=option)

browser.maximize_window()

BASE_URL = "https://huaban.com/%s/"

ALL_USERS = ['s0skxej3vpq']

BOARDS_DIR = "boards"

# checke if the boards directory exists
if not os.path.exists(BOARDS_DIR):
    os.mkdir(BOARDS_DIR)


def split():
    """
        split one line
    """
    print("----------------------------------")


def scroll_forward_bottom():
    js = "var q=document.documentElement.scrollTop=100000"
    scroll_times = 1
    # scroll down util the end
    while scroll_times < 200:
        # scroll one time
        browser.execute_script(js)
        print("scrolled", scroll_times,
              "time(s), and waiting 5 second for loading new imagines")
        scroll_times += 1
        # waiting for loading new images
        time.sleep(5)
        try:
            # down forward the bottom
            if not browser.find_element(By.CLASS_NAME, "loading").is_displayed():
                break
        except:
            continue
    print("down forward the bottom")


def spider_board_cata(id):
    """
        board_cata
    """
    url = BASE_URL % (id)
    print("starting to open", url)
    browser.get(url)
    print("sleeping 10 seconds for loading the whole html")
    time.sleep(10)

    scroll_forward_bottom()

    cards = browser.find_elements(
        By.XPATH, "//div[@class='Board wfc']/a[@class='link x']")

    board_urls = list(map(lambda a: a.get_attribute('href'), cards))
    print("find", len(board_urls), "board(s) of her(him)")
    return board_urls


def suffix_of_content_type(ct):
    """
        find the file type which matches the content-type
    """
    if ct == 'image/png':
        return '.png'
    elif ct == 'image/jpeg':
        return '.jpeg'
    elif ct == 'image/x-icon':
        return '.ico'
    elif ct == 'image/gif':
        return '.git'
    elif ct == 'application/x-bmp':
        return '.bmp'
    elif ct == 'image/pnetvue':
        return '.net'
    elif ct == 'image/vnd.rn-realpix':
        return '.rp'
    elif ct == 'image/tiff':
        return '.tif'
    elif ct == 'image/vnd.wap.wbmp':
        return '.wbmp'
    return ct


def spider_board_content(board_url):
    print("starting to open one board", board_url)
    browser.get(board_url)
    print("sleeping 10 seconds for loading the whole html")
    time.sleep(10)

    scroll_forward_bottom()

    # get all images' url
    img_xpath = "//div[@class='pin wfc wft']//a[@class='img x layer-view loaded']"
    all_imgs = list(map(lambda i: i.get_attribute('href'),
                        browser.find_elements(By.XPATH, img_xpath)
                        ))
    # id and name for naming directory
    # e.g. https://huaban.com/boards/52230810/
    board_id = board_url[26:-1]
    board_title = browser.find_element(By.CLASS_NAME, 'board-name')
    board_name = board_title.get_attribute("innerText")

    print(len(all_imgs),
          "images found in board:%s[%s]" % (board_name, board_id))

    split()

    board_dir_name = None
    # determine what's the name of this board
    # because the board_name has been maybe renamed
    for existing_file in os.listdir(BOARDS_DIR):
        if existing_file.startswith(board_id):
            board_dir_name = existing_file
            break

    # no file exsits before
    if not board_dir_name:
        board_dir_name = board_id + "_" + board_name

    board_dir_path = BOARDS_DIR+'/'+board_dir_name
    # check if the dir exsits
    if not os.path.exists(board_dir_path):
        os.mkdir(board_dir_path)

    # filter new images to download
    downloaded_imgs = os.listdir(board_dir_path)
    # start to spider the images
    for url in all_imgs:
        # e.g. https://huaban.com/pins/2366213472/
        image_id = url[24:-1]
        if not len(list(filter(lambda d: d.startswith(image_id), downloaded_imgs))):
            # not downloaded before
            browser.get(url)
            print("starting open one image", url+",",
                  "and sleeping 3 seconds to load it")
            # waiting forwart the real image
            time.sleep(3)
            image_get_url = browser.find_element(
                By.XPATH, "//div[@class='image-holder']//img").get_attribute("src")
            response = requests.get(image_get_url)
            # get suffix of file according the content-type of response
            content_type = response.headers['Content-Type']
            suffix = suffix_of_content_type(content_type)
            with open(board_dir_path+'/' + image_id + suffix, 'wb') as f:
                f.write(response.content)
                print("download finished")
        else:
            print('downloaded %s before' % (image_id))
    # board_name =


for id in ALL_USERS:
    board_urls = spider_board_cata(id)
    split()
    print("starting spider all the boards...")
    split()
    for url in board_urls:
        spider_board_content(url)
        split()

# spider_board_content("https://huaban.com/boards/38532914/")

browser.close()
