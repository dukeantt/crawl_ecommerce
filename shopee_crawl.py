import os
import datetime
import logging
import nettool

logger = logging.getLogger(__name__)


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
            for item in items:
                item_counting += 1
                logger.info("crawling the %s item", str(item_counting))
                crawl_item(item["itemid"], item["shopid"])
            if len(items) < item_step:
                break
            index += item_step
        except Exception as ex:
            logger.error(ex)


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
    if result is not None and "item" in result:
        shop_info = result["item"]
    else:
        logger.error("cannot get shop info")


crawl_shopee()