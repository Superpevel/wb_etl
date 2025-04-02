from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from bs4 import BeautifulSoup as bs
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import logging
import os
from datetime import datetime
import time
from time import sleep
from dateutil.parser import parse
import re
import json
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium import webdriver
import logging.config
from typing import List
from dotenv import load_dotenv
from fastapi.responses import JSONResponse
from db.db_conf import get_db
from sqlalchemy.orm import Session
from models.user import User
from logs.logs_config import LOGGING_CONFIG
import logging
import json
from sqlalchemy.orm import Session
import requests 
from time import sleep
logging.config.dictConfig(LOGGING_CONFIG)

logger = logging.getLogger(__name__)

capabilities = DesiredCapabilities.CHROME
capabilities["goog:loggingPrefs"] = {"performance": "ALL"}  # chromedriver 75+

options = Options()
options.add_argument("--disable-infobars") 
options.add_argument("--headless")
# options.add_argument("--window-size=1920x1080")


def update_adv_stats(db: Session, item_id: int, rivals_list: list) -> None:


    driver: webdriver.Chrome = webdriver.Chrome(ChromeDriverManager().install(), options=options,  desired_capabilities=capabilities)


    for link in rivals_list: 
        driver.get(link)
        sleep(7)

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
            resp_url = log["params"]["response"]["url"]
            if 'price-history.json' in resp_url:
                price_history = requests.get(resp_url).json()
                print(price_history)