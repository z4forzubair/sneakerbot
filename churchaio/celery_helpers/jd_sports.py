import json
import random
import re

import requests
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from churchaio.celery_helpers.discord_message import successful_checkout
from churchaio.celery_helpers.task_data import get_task_attr
from churchaio.models import Task


class MyException(Exception):
    pass


def bot(task_id):
    def task_failed(status):
        try:
            task = Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            msg = "Task not found"
        else:
            task.status = status
            try:
                task.save()
            except Exception:
                msg = "Task not found"
        finally:
            raise MyException

    task_attr = get_task_attr(task_id=task_id)

    session = requests.session()

    payload = {}
    headers = {
        'authority': 'www.jd-sports.com.au',
        'sec-ch-ua': '"Google Chrome";v="95", "Chromium";v="95", ";Not A Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Linux"',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'sec-fetch-site': 'none',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-user': '?1',
        'sec-fetch-dest': 'document',
        'accept-language': 'en-US,en;q=0.9,ur;q=0.8'
    }

    main_url = task_attr["sku_link"]
    try:
        response = session.request("GET", main_url, headers=headers, data=payload, timeout=120)
    except Exception:
        task_failed(Task.STATUS.NO_SKU)
    print(response)
    if not response.ok:
        task_failed(Task.STATUS.NO_SKU)

    # add to cart
    payload = json.dumps({
        "customisations": False,
        "cartPosition": None,
        "recaptchaResponse": False,
        "cartProductNotification": None,
        "quantityToAdd": 1
    })
    headers = {
        'authority': 'www.jd-sports.com.au',
        'sec-ch-ua': '"Google Chrome";v="95", "Chromium";v="95", ";Not A Brand";v="99"',
        'accept': '*/*',
        'content-type': 'application/json',
        'x-requested-with': 'XMLHttpRequest',
        'sec-ch-ua-mobile': '?0',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36',
        'sec-ch-ua-platform': '"Linux"',
        'origin': 'https://www.jd-sports.com.au',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': main_url,
        'accept-language': 'en-US,en;q=0.9,ur;q=0.8'
    }

    size_regex = re.compile('\\s*page_id_variant: "(.*)"')
    size_no_regex = re.compile('\\s*name:"(.*)"')
    sizes = size_regex.findall(response.content.decode())
    if task_attr["shoe_size"] == -1:
        size = random.choice(sizes)
    else:
        size_nos = size_no_regex.findall(response.content.decode())
        if str(task_attr["shoe_size"]) in size_nos:
            index = size_nos.index(str(task_attr["shoe_size"]))
            size = size_nos[index]
        else:
            task_failed(Task.STATUS.NO_SHOE)
    cart_url = f"https://www.jd-sports.com.au/cart/{size}/"
    try:
        cart_resp = session.request("POST", url=cart_url, headers=headers, data=payload, timeout=120)
    except Exception:
        task_failed(Task.STATUS.CART_FAIL)
    print(cart_resp)
    print(cart_resp.ok)
    if not cart_resp.ok:
        task_failed(Task.STATUS.CART_FAIL)

    # login as guest
    deliveryMethodID = cart_resp.json()["delivery"]["deliveryMethodID"]
    payload = json.dumps({
        "email": task_attr["email"]
    })
    headers = {
        'authority': 'www.jd-sports.com.au',
        'sec-ch-ua': '"Google Chrome";v="95", "Chromium";v="95", ";Not A Brand";v="99"',
        'accept': '*/*',
        'content-type': 'application/json',
        'x-requested-with': 'XMLHttpRequest',
        'sec-ch-ua-mobile': '?0',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36',
        'sec-ch-ua-platform': '"Linux"',
        'origin': 'https://www.jd-sports.com.au',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': 'https://www.jd-sports.com.au/checkout/login/',
        'accept-language': 'en-US,en;q=0.9,ur;q=0.8'
    }
    guest_url = "https://www.jd-sports.com.au/checkout/guest/"
    try:
        guest_resp = session.request("POST", guest_url, headers=headers, data=payload, timeout=120)
    except Exception:
        task_failed(Task.STATUS.CHECKOUT_FAIL)
    print(guest_resp)
    if not guest_resp.ok:
        task_failed(Task.STATUS.CHECKOUT_FAIL)

    payload = json.dumps({'deliveryMethodID': deliveryMethodID, 'deliveryLocation': 'au'})
    headers = {
        'authority': 'www.jd-sports.com.au',
        'sec-ch-ua': '"Google Chrome";v="95", "Chromium";v="95", ";Not A Brand";v="99"',
        'accept': '*/*',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'x-requested-with': 'XMLHttpRequest',
        'sec-ch-ua-mobile': '?0',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36',
        'sec-ch-ua-platform': '"Linux"',
        'origin': 'https://www.jd-sports.com.au',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': 'https://www.jd-sports.com.au/checkout/delivery/',
        'accept-language': 'en-US,en;q=0.9,ur;q=0.8'
    }
    cart_s_url = "https://www.jd-sports.com.au/cart/"
    try:
        cart_s_resp = session.request("PUT", cart_s_url, headers=headers, data=payload, timeout=120)
    except Exception:
        task_failed(Task.STATUS.CHECKOUT_FAIL)
    print(cart_s_resp)
    if not cart_s_resp.ok:
        task_failed(Task.STATUS.CHECKOUT_FAIL)

    payload = {}
    headers = {
        'authority': 'www.jd-sports.com.au',
        'sec-ch-ua': '"Google Chrome";v="95", "Chromium";v="95", ";Not A Brand";v="99"',
        'accept': '*/*',
        'x-requested-with': 'XMLHttpRequest',
        'sec-ch-ua-mobile': '?0',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36',
        'sec-ch-ua-platform': '"Linux"',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': 'https://www.jd-sports.com.au/checkout/delivery/',
        'accept-language': 'en-US,en;q=0.9,ur;q=0.8'
    }
    order_total_url = f"https://www.jd-sports.com.au/checkout/orderTotals/?deliveryLocation=au&AJAX=1&deliveryMethodID={deliveryMethodID}"
    try:
        order_total_resp = session.request("GET", url=order_total_url, headers=headers, data=payload, timeout=120)
    except Exception:
        task_failed(Task.STATUS.CHECKOUT_FAIL)
    print(order_total_resp)
    if not order_total_resp.ok:
        task_failed(Task.STATUS.CHECKOUT_FAIL)

    payload = json.dumps({
        "useDeliveryAsBilling": True,
        "firstName": task_attr["first_name"],
        "lastName": task_attr["last_name"],
        "phone": task_attr["contact"],
        "country": "Australia|au",
        "locale": "",
        "address1": task_attr["address1"],
        "address2": task_attr["address2"],
        "town": task_attr["city"],
        "county": task_attr["state"],
        "postcode": task_attr["postal_code"],
        "addressPredict": "",
        "setOnCart": "deliveryAddressID",
        "addressPredictflag": "true"
    })
    headers = {
        'authority': 'www.jd-sports.com.au',
        'sec-ch-ua': '"Google Chrome";v="95", "Chromium";v="95", ";Not A Brand";v="99"',
        'accept': '*/*',
        'content-type': 'application/json',
        'x-requested-with': 'XMLHttpRequest',
        'sec-ch-ua-mobile': '?0',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36',
        'sec-ch-ua-platform': '"Linux"',
        'origin': 'https://www.jd-sports.com.au',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': 'https://www.jd-sports.com.au/checkout/delivery/',
        'accept-language': 'en-US,en;q=0.9,ur;q=0.8'
    }
    address_book_url = "https://www.jd-sports.com.au/myaccount/addressbook/add/"
    try:
        address_book_resp = session.request("POST", address_book_url, headers=headers, data=payload, timeout=120)
    except Exception:
        task_failed(Task.STATUS.CHECKOUT_FAIL)
    print(address_book_resp)
    if not address_book_resp.ok:
        task_failed(Task.STATUS.CHECKOUT_FAIL)

    address_book_resp_json = address_book_resp.json()
    addressId = address_book_resp_json["ID"]
    payload = json.dumps({
        "addressId": addressId,
        "methodId": deliveryMethodID,
        "deliverySlot": {}
    })
    headers = {
        'authority': 'www.jd-sports.com.au',
        'sec-ch-ua': '"Google Chrome";v="95", "Chromium";v="95", ";Not A Brand";v="99"',
        'accept': '*/*',
        'content-type': 'application/json',
        'x-requested-with': 'XMLHttpRequest',
        'sec-ch-ua-mobile': '?0',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36',
        'sec-ch-ua-platform': '"Linux"',
        'origin': 'https://www.jd-sports.com.au',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': 'https://www.jd-sports.com.au/checkout/delivery/',
        'accept-language': 'en-US,en;q=0.9,ur;q=0.8'
    }
    delivery_add_update_url = "https://www.jd-sports.com.au/checkout/updateDeliveryAddressAndMethod/ajax/"
    try:
        delivery_add_update_resp = session.request("POST", delivery_add_update_url, headers=headers, data=payload,
                                                   timeout=120)
    except Exception:
        task_failed(Task.STATUS.CHECKOUT_FAIL)
    print(delivery_add_update_resp)
    if not delivery_add_update_resp.ok:
        task_failed(Task.STATUS.CHECKOUT_FAIL)

    payload = "paySelect=card&isSafari=true"
    headers = {
        'authority': 'www.jd-sports.com.au',
        'sec-ch-ua': '"Google Chrome";v="95", "Chromium";v="95", ";Not A Brand";v="99"',
        'accept': '*/*',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'x-requested-with': 'XMLHttpRequest',
        'sec-ch-ua-mobile': '?0',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36',
        'sec-ch-ua-platform': '"Linux"',
        'origin': 'https://www.jd-sports.com.au',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': 'https://www.jd-sports.com.au/checkout/billing/',
        'accept-language': 'en-US,en;q=0.9,ur;q=0.8',
    }
    payment_v3_url = "https://www.jd-sports.com.au/checkout/paymentV3/"
    try:
        payment_v3_resp = session.request("POST", payment_v3_url, headers=headers, data=payload, timeout=120)
    except Exception:
        task_failed(Task.STATUS.PAYMENT_FAIL)
    print(payment_v3_resp)
    if not payment_v3_resp.ok:
        task_failed(Task.STATUS.PAYMENT_FAIL)
    payload_url = payment_v3_resp.text.replace("\\", "").replace("\"", "")

    def wait_by_xpath(element_path, wait_count=None, first_try=True):
        try:
            wait.until(
                EC.visibility_of_element_located((By.XPATH, element_path))
            )
        except TimeoutException:
            if first_try: wait_count = 0
            wait_count += 1
            if wait_count < 3:
                wait_by_xpath(element_path, wait_count, False)
            else:
                task_failed(Task.STATUS.PAYMENT_FAIL)
        finally:
            pass

    def wait_by_id(element_path, wait_count=None, first_try=True):
        try:
            wait.until(
                EC.visibility_of_element_located((By.ID, element_path))
            )
        except TimeoutException:
            if first_try: wait_count = 0
            wait_count += 1
            if wait_count < 3:
                wait_by_id(element_path, wait_count, False)
            else:
                task_failed(Task.STATUS.PAYMENT_FAIL)
        finally:
            pass

    def insert_input_by_id(element_path, element_val):
        wait_by_id(element_path)
        element_input = driver.find_element_by_id(element_path)
        element_input.clear()
        element_input.send_keys(element_val)

    options = Options()
    options.headless = True
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    driver.maximize_window()
    wait = WebDriverWait(driver, 10)

    driver.get(payload_url)
    driver.delete_all_cookies()
    cookie_dict = session.cookies.get_dict()
    for cookie in cookie_dict:
        driver.add_cookie({'name': cookie, 'value': cookie_dict[cookie]})
    driver.get(payload_url)

    card_number_path = "card.cardNumber"
    insert_input_by_id(card_number_path, task_attr["cc_number"])

    card_holder_path = "card.cardHolderName"
    insert_input_by_id(card_holder_path, task_attr["first_name"] + " " + task_attr["last_name"])

    month_path = "card.expiryMonth"
    month_value = task_attr["month"]
    month_value_path = f"//option[text()='{month_value}']"
    month = driver.find_element_by_id(month_path).find_element_by_xpath(month_value_path)
    month.click()

    year_path = "card.expiryYear"
    year_value = '20' + task_attr["year"]
    year_value_path = f"//option[text()='{year_value}']"
    year = driver.find_element_by_id(year_path).find_element_by_xpath(year_value_path)
    year.click()

    cvc_code_path = "card.cvcCode"
    insert_input_by_id(cvc_code_path, task_attr["cc_code"])

    pay_btn_path = "//INPUT[@class='paySubmit paySubmitcard']"
    wait_by_xpath(pay_btn_path)
    pay_btn = driver.find_element_by_xpath(pay_btn_path)
    pay_btn.click()

    driver.close()

    def task_completed():
        try:
            task = Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            msg = "Task not found"
        else:
            task.status = Task.STATUS.COMPLETED
            try:
                task.save()
            except Exception:
                msg = "Task not found"

    task_completed()
    title_regex = re.compile('\\s*<title\>(.*)\<')
    return title_regex.findall(response.content.decode())[0]


def jd_sports_bot(task_id, user_id):
    try:
        title = bot(task_id=task_id)
        successful_checkout(user_id, title)
    except MyException:
        return
