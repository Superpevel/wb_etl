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
from models import Product, Competitor, CompetitorPrices
import datetime
import requests

logging.config.dictConfig(LOGGING_CONFIG)

logger = logging.getLogger(__name__)

capabilities = DesiredCapabilities.CHROME
capabilities["goog:loggingPrefs"] = {"performance": "ALL"}  # chromedriver 75+

options = Options()
options.add_argument("--disable-infobars") 
# options.add_argument("--headless")
options.add_argument("--window-size=1920x1080")


def update_prices_history(db: Session, prodct: Product, rivals_list: List[Competitor]) -> None:


    driver: webdriver.Chrome = webdriver.Chrome(ChromeDriverManager().install(), options=options,  desired_capabilities=capabilities)
    for rival in rivals_list: 
        link = f"https://www.wildberries.ru/catalog/{rival.competitor_nmID}/detail.aspx"
        driver.get(link)
        print("pre sleep")
        sleep(10)

        print("HERE?")
        sleep(25)
        print("sleep again")
        logs_raw = driver.get_log("performance")
        logs = [json.loads(lr["message"])["message"] for lr in logs_raw]


        def log_filter(log_):
            return (
                # is an actual response
                log_["method"] == "Network.responseReceived"
                # and json
                and 
                "json" in log_["params"]["response"]["mimeType"]
            )

        print("LOGGING")
        for log in filter(log_filter, logs):
            resp_url = log["params"]["response"]["url"]
            print(resp_url, "RESP URL")
            if 'price-history.json' in resp_url:
                print("ENTER!!!")
                price_history = requests.get(resp_url).json()
                for price in price_history:
                    print(price_history)
                # timestamp = 1737849600
                    
                    date = datetime.datetime.fromtimestamp(price['dt'])
                    price_val = price['price']['RUB']
                    exist = db.query(CompetitorPrices).filter(CompetitorPrices.date==date, CompetitorPrices.competitor_id==rival.id).first()
                    if exist:
                        print('exists!')
                        continue

                    c_price = CompetitorPrices()
                    c_price.date = date
                    c_price.price = price_val
                    c_price.competitor_id = rival.id

                    db.add(c_price)
                    db.commit()
                    print("SAVING!")