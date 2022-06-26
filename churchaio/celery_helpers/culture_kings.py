import random
import re
import urllib.parse

import requests
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from churchaio.celery_helpers.discord_message import successful_checkout
from churchaio.celery_helpers.task_data import get_task_attr
from churchaio.celery_helpers.task_operations import MyException, task_failed, task_completed
from churchaio.models import Task


def bot(task_id):
    print("Starting " + str(task_id))
    import time
    time.sleep(15)
    print("END " + str(task_id))

    task_failed(task_id, Task.STATUS.CHECKOUT_FAIL)

    task_attr = get_task_attr(task_id=task_id)

    session = requests.session()

    payload = {}
    headers = {
        'authority': 'www.culturekings.com.au',
        'cache-control': 'max-age=0',
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
        task_failed(task_id, Task.STATUS.NO_SKU)
    print(response)
    if not response.ok:
        task_failed(task_id, Task.STATUS.NO_SKU)

    html = response.text
    parsed_html = bs(html, 'html.parser')  # parsing # and I have toled Beautiful to parse it as an html file
    # all the info is present in input tags only, it also contains a lot of other html
    spans = parsed_html.findAll('span', {'class': 'nosto_sku'})
    ids_list = []
    size_names = []
    for span in spans:
        availability = span.find('span', {'class': 'availability'}).get_text()
        if availability == "InStock":
            ids_list.append(span.find('span', {'class': 'id'}).get_text())
            size_names.append(span.find('span', {'class': 'name'}).get_text())
        else:
            pass
    if not ids_list:
        task_failed(task_id, Task.STATUS.CART_FAIL)
    else:
        if task_attr["shoe_size"] == -1:
            size_id = random.choice(ids_list)
            size_name = size_names[ids_list.index(size_id)]
        else:
            size_name = str(task_attr["shoe_size"])
            if size_name in size_names:
                size_id = ids_list[size_names.index(size_name)]
            else:
                task_failed(task_id, Task.STATUS.CART_FAIL)
    print(size_name)
    print(size_id)
    payload = {
        "option1": size_name,
        "id[]": size_id,
        "event_id": "1234"
    }
    payload = urllib.parse.urlencode(payload, encoding='utf-8')
    headers = {
        'authority': 'www.culturekings.com.au',
        'sec-ch-ua': '"Google Chrome";v="95", "Chromium";v="95", ";Not A Brand";v="99"',
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'x-requested-with': 'XMLHttpRequest',
        'sec-ch-ua-mobile': '?0',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36',
        'sec-ch-ua-platform': '"Linux"',
        'origin': 'https://www.culturekings.com.au',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': main_url,
        'accept-language': 'en-US,en;q=0.9,ur;q=0.8'
    }
    cart_url = "https://www.culturekings.com.au/cart/add.js"
    try:
        cart_resp = session.request("POST", cart_url, headers=headers, data=payload, timeout=120)
    except Exception:
        task_failed(task_id, Task.STATUS.CART_FAIL)
    print(cart_resp)
    if not cart_resp.ok:
        task_failed(task_id, Task.STATUS.CART_FAIL)

    payload = {
        "updates[]": "1",
        "updates[]": "1",
        "checkout": ""
    }
    payload = urllib.parse.urlencode(payload, encoding='utf-8')
    headers = {
        'authority': 'www.culturekings.com.au',
        'cache-control': 'max-age=0',
        'sec-ch-ua': '"Google Chrome";v="95", "Chromium";v="95", ";Not A Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Linux"',
        'upgrade-insecure-requests': '1',
        'origin': 'https://www.culturekings.com.au',
        'content-type': 'application/x-www-form-urlencoded',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-user': '?1',
        'sec-fetch-dest': 'document',
        'referer': main_url,
        'accept-language': 'en-US,en;q=0.9,ur;q=0.8'
    }
    checkout_url = "https://www.culturekings.com.au/cart"
    try:
        checkout_resp = session.request("POST", checkout_url, headers=headers, data=payload, timeout=120)
    except Exception:
        task_failed(task_id, Task.STATUS.CHECKOUT_FAIL)
    print(checkout_resp)
    if not checkout_resp.ok:
        task_failed(task_id, Task.STATUS.CHECKOUT_FAIL)

    authenticity_token_regex = re.compile('name="authenticity_token"\s*value=\"(.*)\"')
    authenticity_token = authenticity_token_regex.findall(checkout_resp.content.decode())[0]
    if '"' in authenticity_token: authenticity_token = authenticity_token.split('"')[0]
    print(authenticity_token)
    payload = {
        "_method": "patch",
        "authenticity_token": authenticity_token,
        "previous_step": "contact_information",
        "step": "shipping_method",
        "checkout[email]": task_attr["email"],
        "checkout[buyer_accepts_marketing]": "0",
        "checkout[shipping_address][first_name]": task_attr["first_name"],
        "checkout[shipping_address][last_name]": task_attr["last_name"],
        "checkout[shipping_address][company]": "",
        "checkout[shipping_address][address1]": urllib.parse.quote_plus(task_attr["address1"]),
        "checkout[shipping_address][address2]": urllib.parse.quote_plus(task_attr["address2"]),
        "checkout[shipping_address][city]": task_attr["city"],
        "checkout[shipping_address][country]": "",
        "checkout[shipping_address][province]": "",
        "checkout[shipping_address][zip]": task_attr["postal_code"],
        "checkout[shipping_address][phone]": task_attr["contact"],
        "checkout[shipping_address][first_name]": task_attr["first_name"],
        "checkout[shipping_address][last_name]": task_attr["last_name"],
        "checkout[shipping_address][company]": "",
        "checkout[shipping_address][address1]": urllib.parse.quote_plus(task_attr["address1"]),
        "checkout[shipping_address][address2]": urllib.parse.quote_plus(task_attr["address2"]),
        "checkout[shipping_address][city]": task_attr["city"],
        "checkout[shipping_address][country]": task_attr["country"],
        "checkout[shipping_address][zip]": task_attr["postal_code"],
        "checkout[shipping_address][phone]": task_attr["contact"],
        "checkout[client_details][browser_width]": "1293",
        "checkout[client_details][browser_height]": "340",
        "checkout[client_details][javascript_enabled]": "1",
        "checkout[client_details][color_depth]": "24",
        "checkout[client_details][java_enabled]": "false",
        "checkout[client_details][browser_tz]": "-300"

    }
    payload = urllib.parse.urlencode(payload, encoding='utf-8')
    headers = {
        'authority': 'www.culturekings.com.au',
        'cache-control': 'max-age=0',
        'sec-ch-ua': '"Google Chrome";v="95", "Chromium";v="95", ";Not A Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Linux"',
        'upgrade-insecure-requests': '1',
        'origin': 'https://www.culturekings.com.au',
        'content-type': 'application/x-www-form-urlencoded',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-user': '?1',
        'sec-fetch-dest': 'document',
        'referer': 'https://www.culturekings.com.au/',
        'accept-language': 'en-US,en;q=0.9,ur;q=0.8'
    }
    page_url_regex = re.compile('"pageurl":\s*\"(.*)\"')
    shipping_url = page_url_regex.findall(checkout_resp.content.decode())[0]
    if '"' in shipping_url: shipping_url = shipping_url.split('"')[0]
    shipping_url = "https://" + shipping_url.replace("\\", "")
    print(shipping_url)
    try:
        contact_resp = session.request("POST", shipping_url, headers=headers, data=payload, timeout=120)
    except Exception:
        task_failed(task_id, Task.STATUS.CHECKOUT_FAIL)
    print(contact_resp)
    if not contact_resp.ok:
        task_failed(task_id, Task.STATUS.CHECKOUT_FAIL)

    # authenticity_token = authenticity_token_regex.findall(contact_resp.content.decode())[0]
    # if '"' in authenticity_token: authenticity_token = authenticity_token.split('"')[0]
    # payload = {
    #     "_method": "patch",
    #     "authenticity_token": authenticity_token,
    #     "previous_step": "shipping_method",
    #     "step": "payment_method",
    #     "checkout[shipping_rate][id]": urllib.parse.quote_plus("Openstyle6 - Shipping Rates Provider-AU-STD-0-0.00"),
    #     "checkout[client_details][browser_width]": "1293",
    #     "checkout[client_details][browser_height]": "402",
    #     "checkout[client_details][javascript_enabled]": "1",
    #     "checkout[client_details][color_depth]": "24",
    #     "checkout[client_details][java_enabled]": "false",
    #     "checkout[client_details][browser_tz]": "-300"
    # }
    # payload = urllib.parse.urlencode(payload, encoding='utf-8')
    # headers = {
    #     'authority': 'www.culturekings.com.au',
    #     'cache-control': 'max-age=0',
    #     'sec-ch-ua': '"Google Chrome";v="95", "Chromium";v="95", ";Not A Brand";v="99"',
    #     'sec-ch-ua-mobile': '?0',
    #     'sec-ch-ua-platform': '"Linux"',
    #     'upgrade-insecure-requests': '1',
    #     'origin': 'https://www.culturekings.com.au',
    #     'content-type': 'application/x-www-form-urlencoded',
    #     'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36',
    #     'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    #     'sec-fetch-site': 'same-origin',
    #     'sec-fetch-mode': 'navigate',
    #     'sec-fetch-user': '?1',
    #     'sec-fetch-dest': 'document',
    #     'referer': 'https://www.culturekings.com.au/',
    #     'accept-language': 'en-US,en;q=0.9,ur;q=0.8'
    # }

    # shipping_resp = session.request("POST", shipping_url, headers=headers, data=payload)
    # print(shipping_resp)

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
                task_failed(task_id, Task.STATUS.PAYMENT_FAIL)
        finally:
            pass

    def wait_presence_by_class_name(element_path, wait_count=None, first_try=True):
        try:
            wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, element_path))
            )
        except TimeoutException:
            if first_try: wait_count = 0
            wait_count += 1
            if wait_count < 3:
                wait_presence_by_class_name(element_path, wait_count, False)
            else:
                task_failed(task_id, Task.STATUS.PAYMENT_FAIL)
        finally:
            pass

    options = Options()
    options.headless = True
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    driver.maximize_window()
    wait = WebDriverWait(driver, 10)

    driver.get(shipping_url)
    driver.delete_all_cookies()
    cookie_dict = session.cookies.get_dict()
    for cookie in cookie_dict:
        driver.add_cookie({'name': cookie, 'value': cookie_dict[cookie]})
    driver.get(shipping_url)

    to_pay_btn_path = "continue_button"
    wait_by_id(to_pay_btn_path)
    to_pay_btn = driver.find_element_by_id(to_pay_btn_path)
    to_pay_btn.click()

    iframes_path = "card-fields-iframe"
    wait_presence_by_class_name(iframes_path)
    iframes = driver.find_elements_by_class_name(iframes_path)

    num_frame = iframes[0]
    driver.switch_to.frame(num_frame)
    num_elem = driver.find_element_by_id("number")
    num_elem.clear()
    i = 0
    for j in range(4):
        num_elem.send_keys(task_attr["cc_number"][i:i + 4])
        i += 4
    driver.switch_to.default_content()

    name_frame = iframes[1]
    driver.switch_to.frame(name_frame)
    name_elem = driver.find_element_by_id("name")
    name_elem.clear()
    name_elem.send_keys(f'{task_attr["first_name"]} {task_attr["last_name"]}')
    driver.switch_to.default_content()

    expiry_frame = iframes[2]
    driver.switch_to.frame(expiry_frame)
    expiry_elem = driver.find_element_by_id("expiry")
    expiry_elem.clear()
    expiry_elem.send_keys(task_attr["month"])
    expiry_elem.send_keys(task_attr["year"])
    driver.switch_to.default_content()

    cvc_frame = iframes[3]
    driver.switch_to.frame(cvc_frame)
    cvc_elem = driver.find_element_by_id("verification_value")
    cvc_elem.clear()
    cvc_elem.send_keys(task_attr["cc_code"])
    driver.switch_to.default_content()

    same_billing_radio_path = "checkout_different_billing_address_false"
    wait_by_id(same_billing_radio_path)
    same_billing_radio = driver.find_element_by_id(same_billing_radio_path)
    same_billing_radio.click()

    pay_btn_path = "continue_button"
    wait_by_id(pay_btn_path)
    pay_btn = driver.find_element_by_id(pay_btn_path)
    pay_btn.click()

    import time
    time.sleep(5)
    driver.close()

    task_completed(task_id)
    title_regex = re.compile('\\s*<title\>(.*)\<\/')
    return title_regex.findall(response.content.decode())[0].replace("&#39;", "'")


def culture_kings_bot(task_id, user_id):
    try:
        title = bot(task_id=task_id)
        successful_checkout(user_id, title)
    except MyException:
        pass
