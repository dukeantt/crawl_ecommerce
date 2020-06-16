import os
import datetime
import logging
import nettool
from datetime import date
import psycopg2
import pandas as pd

logger = logging.getLogger(__name__)

db_info = {
    "host": "127.0.0.1",
    "database": "crawl_data",
    "user": "postgres",
    "password": "1",
    "schema": "data",
    "port": "5432",
}


def crawl_shopee():
    """
    start crawl a shopee shop
    :param shop_id: id of shop on fb
    :return:
    """

    item_step = 50
    item_counting = 0
    index = 0
    search_text = "Xe đẩy, nôi cũi"

    params = {
        "by": "relevancy",
        "order": "desc",
        "page_type": "search",
        "limit": item_step,
        "match_id": "8851",
        "version": "2",
        "keyword": search_text,
    }
    url_temp = "https://shopee.vn/api/v2/search_items/"

    start_time = datetime.datetime.now()

    # crawl and update products
    while True:
        logger.info("crawl page %s", str(index))
        try:
            params["newest"] = index
            items = get_item_list(url_temp, params)
            product_list = []
            for item in items:
                item_counting += 1
                logger.info("crawling the %s item", str(item_counting))
                product = crawl_item(item["itemid"], item["shopid"])
                product_list.append(product)
            if len(items) < item_step:
                break
            index += item_step
        except Exception as ex:
            logger.error(ex)

    x = 0

def get_item_list(url: str, params: dict) -> list:
    retry_number = 10

    while retry_number > 0:
        retry_number -= 1
        result = nettool.get(url, params)
        if result and 'items' in result:
            return result["items"]
    return []


def crawl_item(item_id: str, shop_market_place_id: str):
    item_url = "https://shopee.vn/api/v2/item/get"
    params = {"itemid": item_id, "shopid": shop_market_place_id}
    retry_number = 10
    result = None
    while retry_number > 0:
        retry_number -= 1
        result = nettool.get(item_url, params)
        if result:
            break
    if result is not None and "item" in result:
        item = result["item"]
        if item["shopid"]:
            shop_info = crawl_shop_info(item["shopid"])
            item["shop_info"] = shop_info
        try:
            product = process_item(item)
            return product
        except Exception as ex:
            logger.error(ex)
            return
    else:
        logger.error("cannot get product %s of shop %s on shopee", str(item_id), str(shop_market_place_id))


def crawl_shop_info(shop_id):
    shop_api_url = "https://shopee.vn/api/v2/shop/get"
    params = {"shopid": shop_id}
    retry_number = 10
    result = None
    while retry_number > 0:
        retry_number -= 1
        result = nettool.get(shop_api_url, params)
        if result:
            break
    if result is not None and "data" in result:
        shop_info = result["data"]
        return shop_info
    else:
        logger.error("cannot get shop info")


def process_item(item: dict):
    today = date.today()

    product = {
        "product_id": item["itemid"],
        "brand": item["brand"],
        "shop_id": str(item["shop_info"]["shopid"]),
        "product_url": "https://shopee.vn/product/" + str(item["shop_info"]["shopid"]) + "/" + str(item["itemid"]),
        "name": item["name"],
        "price": item["price_before_discount"] / 100000,
        "final_price": item["price"] / 100000,
        "shop_name": item["shop_info"]["name"],
        "shop_url": "https://shopee.vn/" + str(item["shop_info"]["account"]["username"]),
        "crawl_date": today
    }
    if product["price"] == 0:
        product["price"] = product["final_price"]
    return product


def insert_to_db(product):
    query = "insert into {} (product_id, brand, shop_id, product_url, name, price, " \
            "final_price, shop_name, shop_url, crawl_date) " \
            "VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) " \
            "returning id".format("data.shopee")
    params = [product["product_id"], product["brand"], product["shop_id"], product["product_url"],
              product["name"], product["price"],
              product["final_price"],
              product["shop_name"],
              product["shop_url"],
              product["crawl_date"]]

    connection = psycopg2.connect(user=db_info["user"], password=db_info["password"], host=db_info["host"],
                                  port=db_info["port"], database=db_info["database"])
    cursor = connection.cursor()
    connection.cursor().execute(query, tuple(params))
    try:
        cursor.execute(query, tuple(params))
        print("insert")
    except Exception as ex:
        logger.error(ex)
        logger.error("query:%s", cursor.query)
    finally:
        print("close")
        cursor.close()


crawl_shopee()
