from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from bs4 import BeautifulSoup as bs
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager

from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
import logging
import os
from datetime import datetime
import time
import threading
from time import sleep
from multiprocessing import Process,Pool,Lock
from dateutil.parser import parse
import functools
import re
import json
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from selenium import webdriver
# from seleniumwire import webdriver 
# chrome_options = webdriver.ChromeOptions()
# chrome_options.set_capability(
#                         "goog:loggingPrefs", {"performance": "ALL", "browser": "ALL"}
#   
#                   )


capabilities = DesiredCapabilities.CHROME
capabilities["goog:loggingPrefs"] = {"performance": "ALL"}  # chromedriver 75+

options = Options()
options.add_argument("--disable-infobars") 
options.add_argument("--disable-infobars") 
options.add_argument("--window-size=1920x1080")

driver: webdriver.Chrome = webdriver.Chrome(ChromeDriverManager().install(), options=options,  desired_capabilities=capabilities)

# def process_browser_logs_for_network_events(logs):
#     """
#     Return only logs which have a method that start with "Network.response", "Network.request", or "Network.webSocket"
#     since we're interested in the network events specifically.
#     """
#     for entry in logs:
#         log = json.loads(entry["message"])["message"]
#         if (
#                 "Network.response" in log["method"]
#                 or "Network.request" in log["method"]
#                 or "Network.webSocket" in log["method"]
#         ):
#             yield log


driver.get("https://www.wildberries.ru/catalog/179437040/detail.aspx")
sleep(5)

logs_raw = driver.get_log("performance")
logs = [json.loads(lr["message"])["message"] for lr in logs_raw]

import requests

def log_filter(log_):
    return (
        # is an actual response
        log_["method"] == "Network.responseReceived"
        # and json
        and 
        "json" in log_["params"]["response"]["mimeType"]
    )

for log in filter(log_filter, logs):
    request_id = log["params"]["requestId"]
    resp_url = log["params"]["response"]["url"]
    if 'price-history.json' in resp_url:
        price_history = requests.get(resp_url).json()
        print(price_history)
    # print(f"Caught {resp_url}")
    # print(driver.execute_cdp_cmd("Network.getResponseBody", {"requestId": request_id}))


# sleep(10)

# print(res)
# logs = driver.get_log("performance")

# events = process_browser_logs_for_network_events(logs)
# with open("log_entries.txt", "wt") as out:
#     for event in events:
#         print(event)
#         out.write(str(event))