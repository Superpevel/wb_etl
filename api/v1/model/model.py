import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings("ignore")
from sklearn.preprocessing import OneHotEncoder
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import LabelEncoder
from catboost import CatBoostRegressor
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression, Ridge, Lasso, ElasticNet
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import make_scorer, mean_squared_error
from db.db_conf import engine
from fastapi import APIRouter
import logging
from fastapi import FastAPI, Query, Request, Response, Depends, Header
import logging
from db.db_conf import get_db
from sqlalchemy.orm import Session
from models import *
from schemas.request_schemas.card_request import UserRegister,UserLogin
from models.user import User
import jwt
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.sql import func, desc
from api.v1.product.product import calculate_margin
import os
import pickle

load_dotenv()

SQLALCHEMY_DATABASE_URL = (f"postgresql://{os.environ.get('DB_USER')}"
                f":{os.environ.get('DB_PASSWORD')}"
                f"@{os.environ.get('DB_HOST')}"
                f"/{os.environ.get('DB_NAME')}")

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={}
)


from auth.auth import get_userdata_secure
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/model",
    tags=["model"],
    responses={404: {"description": "Not found"}},
)





def prepare_df(df):
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    df['day_of_week'] = df['date'].dt.dayofweek
    df = df.drop(columns=['brandName', 'date']) # brandName принимает только 1 значение, поэтому данная колонка несодержательна

    # создаём доп. фичи
    df['conversion'] = df['ordersCount'] / (df['openCardCount'] + 1) # конверсия
    df['cart_to_order_r'] = df['ordersCount'] / (df['addToCartCount'] + 1) # воронка перехода от корзины к заказу
    df['avg_order_value'] = df['ordersSumRub'] / (df['ordersCount'] + 1) # отношение суммы заказов к числу заказов

    le = LabelEncoder()
    df['vendorCode'] = le.fit_transform(df['vendorCode'])

    return df


def wape_func(y_true, y_pred):
    wape = np.sum(np.abs(y_true - y_pred)) / np.sum(y_true + 1e-7) * 100
    return wape

def find_optimal_price(model, product_data,db ,model_type='cat',
                      price_range=(100, 5000),check_competetive=False, competetive_sensetivity=30,competative_price=0, step=50, plot=True):

    prices = np.arange(price_range[0], price_range[1], step)
    orders_pred = []
    profit_dict = {}
    margin_dict = {}

    if check_competetive and competative_price>0:
        competative_price_low =  competative_price-(competative_price*competetive_sensetivity)/100
        competative_price_high =  competative_price+(competative_price*competetive_sensetivity)/100

    for price in prices:
        testt = product_data.copy()
        testt['avg_price_rub'] = price
        testt = testt.to_frame().T
        pred = round(model.predict(testt)[0], 0) 
        
        profit, margin =  calculate_margin(str(int(product_data['nmId'])),pred,db)

        if margin_dict.get(margin) and margin_dict[margin]['price']< price:
            if check_competetive and competative_price>0 and price>= competative_price_low and price<=competative_price_high:
                margin_dict.update({margin: {'pred': pred, 'price': price }}) 
                print(margin_dict[margin]['price'], price, 'upd')
        else:
            margin_dict.update({margin: {'pred': pred, 'price': price }}) 

        if profit_dict.get(profit) and profit_dict[profit]['price']< price:  
            if check_competetive and competative_price>0 and price>= competative_price_low and price<=competative_price_high:
                profit_dict.update({profit: {'pred': pred, 'price': price }})
                print(profit_dict[profit]['price'], price, 'upd')
        else:
            profit_dict.update({profit: {'pred': pred, 'price': price }})

        orders_pred.append(pred)

    # print(margin_dict)
    # return 1
    max_profit = max(profit_dict)
    count_orders_max_profit = profit_dict.get(max_profit)


    max_margin = max(margin_dict)
    count_orders_margin = margin_dict.get(max_margin)

    optimal_idx = np.argmax(orders_pred)

    optimal_price = prices[optimal_idx]
    max_orders = orders_pred[optimal_idx]


    return {'max_profit':[ max_profit, count_orders_max_profit], 'max_margin': [max_margin, count_orders_margin], 'max_orders': [optimal_price, max_orders]}


    # return optimal_price, max_orders



def evaluate_model(model, X_test, y_test, model_name):
    y_pred = model.predict(X_test)
    wape = wape_func(y_test, y_pred)
    
    print(f"В среднем модель {model_name} ошибается на {wape:.2f}%")

@router.post('/catboost')
def learn(db: Session = Depends(get_db)):
    # print(type(db.query(Stats).statement))
    # return

    with engine.connect() as conn:
        df = pd.read_sql(
            sql=str(db.query(Stats).statement),
            con=conn.connection
        )


    # with engine.connect() as connection:
    #     df = pd.read_sql(str(db.query(Stats).statement),connection.) 
    df.head()

    df_final = prepare_df(df)


    X = df_final.drop(['ordersCount', 'id'], axis=1)
    y = df_final['ordersCount']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)


    cat_model = CatBoostRegressor(
        iterations=1100,
        learning_rate=0.05,
        depth=6,
        loss_function='Poisson',
        verbose=100,
        early_stopping_rounds=50,
        random_seed=42
    )

    cat_model.fit(X_train, y_train, eval_set=(X_test, y_test))

    sample_product = X_test.iloc[10].copy()
    sample_product = sample_product.drop('avg_price_rub')

    opt_price_cat, max_orders_cat = find_optimal_price(cat_model, sample_product, model_type='cat')

    evaluate_model(cat_model, X_test, y_test, 'CatBoost')
    cat_model.save_model('Catboost.cbm')
    print(f"Пример CatBoost: Оптимальная цена = {opt_price_cat:.2f} руб., Прогноз заказов = {max_orders_cat:.1f}")



@router.get('/model_find_price')
def find_price(nmId: str,model_type: str = 'catboost',competetive_sensetivity: int = 30, check_competetive: bool =  False, db: Session = Depends(get_db)):

    with engine.connect() as conn:
        df = pd.read_sql(
            sql=f'SELECT stats.id, stats.date, stats."nmId", stats.product_id, stats."vendorCode", stats."brandName", stats."openCardCount", stats."addToCartCount", stats."ordersCount", stats."ordersSumRub", stats."buyoutsCount", stats."buyoutsSumRub", stats."cancelCount", stats."cancelSumRub", stats."addToCartPercent", stats."cartToOrderPercent", stats."buyoutsPercent", stats.avg_price_rub, stats.user_id FROM stats WHERE stats."nmId" = {nmId} ORDER BY stats.date DESC LIMIT 1',
            con=conn.connection
        )
    df_final = prepare_df(df)

    # df = pd.read_sql(str(db.query(Stats).filter(Stats.nmId==nmId).order_by(desc(Stats.date)).limit(1).statement),db.connect)


    df.head()
    looking = df_final.iloc[0].copy()
    avg_price = db.query(func.avg(Stats.avg_price_rub).label('avg_price')).filter(Stats.nmId==nmId).first().avg_price

    if model_type=='catboost':
        model = CatBoostRegressor()

        model.load_model('Catboost.cbm')


        # opt_price_ridge, max_orders_ridge = find_optimal_price(ridge, sample_product, model_type='ridge')

        # print(f"Пример Ridge-регрессии: Оптимальная цена = {opt_price_ridge:.2f} руб., Прогноз заказов = {max_orders_ridge:.1f}")
        # opt_price_cat, max_orders_cat = find_optimal_price(model, looking, db,'cat', (100, avg_price*1.3))
        return  find_optimal_price(model, looking, db,'cat', (100, avg_price*1.3))
    elif model_type=='linear':
        with open('model.pkl', 'rb') as f:
            model = pickle.load(f)
        
        df_final = df_final.replace('nan', np.nan)
        df_final = df_final.dropna()
        # print(df_final)
        df_final = df_final.drop(['ordersCount', 'id'], axis=1)
        
        
        looking = df_final.iloc[0].copy()
        # y = df_final['ordersCount']

        return find_optimal_price(model, looking,db, 'ridge', (100, avg_price*1.3))



@router.post('/linear_model_learn')
def linear_model_learn(db: Session = Depends(get_db)):
    # print(type(db.query(Stats).statement))
    # return

    with engine.connect() as conn:
        df = pd.read_sql(
            sql=str(db.query(Stats).statement),
            con=conn.connection
        )
    print("HERE?")

    # with engine.connect() as connection:
    #     df = pd.read_sql(str(db.query(Stats).statement),connection.) 
    df.head()

    df_final = prepare_df(df)
    df_final = df_final.replace('nan', np.nan)
    df_final = df_final.dropna()
    # print(df_final)
    X = df_final.drop(['ordersCount', 'id'], axis=1)
    y = df_final['ordersCount']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    print("HERE?")
    ridge = Ridge(alpha=10, fit_intercept=False)
    ridge.fit(X_train, y_train)
    print("HERE3")
    with open('model.pkl','wb') as f:
        pickle.dump(ridge,f)



    # def evaluate_model(model, X_test, y_test, model_name):
    #     y_pred = model.predict(X_test)
    #     wape = wape_func(y_test, y_pred)
    #     return f"В среднем модель {model_name} ошибается на {wape:.2f}%"

    # evaluate_model(ridge, X_test, y_test, 'Ridge-регрессия')
    return True