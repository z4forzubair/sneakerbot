import re

# regex variables to be used
SYNC_TOKEN_REGEX = re.compile('name=\"SynchronizerToken\"\s*value=\"(.*)\"/>')
CART_URL_REGEX = re.compile('class="fl-load-animation"\s*data-ajaxcontent-url=\"(.*)\"')
ID_REGEX = re.compile('v=(.*)')
ADDRESS_ID_REGEX = re.compile('name="shipping_AddressID"\s*value=\"(.*)\"')

# headers
CART_HEADERS = {
    'authority': 'www.footlocker.com.au',
    'accept': 'application/json, text/javascript, */*; q=0.01',
    'accept-encoding': 'gzip, deflate, br',  # but to write
    'accept-language': 'en-US,en;q=0.9,ur;q=0.8',
    'content-length': '0',
    'origin': 'https://www.footlocker.com.au',
    'referer': '',  # contains the shoe id link
    'sec-ch-ua': '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36',
    'x-requested-with': 'XMLHttpRequest'
}

CHECKOUT_FORM_HEADERS = {
    'authority': 'www.footlocker.com.au',
    'sec-ch-ua': '"Google Chrome";v="90", "Chromium";v="90", ";Not A Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.128 Safari/537.36',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-user': '?1',
    'sec-fetch-dest': 'document',
    'referer': 'https://www.footlocker.com.au/INTERSHOP/web/WFS/FootlockerAustraliaPacific-Footlocker_AU-Site/en_AU/-/AUD/ViewCart-Dispatch',
    'accept-language': 'en-US,en;q=0.9,ur;q=0.8'
}

CHECKOUT_DISPATCH_HEADERS = {
    'authority': 'www.footlocker.com.au',
    'cache-control': 'max-age=0',
    'sec-ch-ua': '"Google Chrome";v="90", "Chromium";v="90", ";Not A Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'upgrade-insecure-requests': '1',
    'origin': 'https://www.footlocker.com.au',
    'content-type': 'application/x-www-form-urlencoded',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.128 Safari/537.36',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-user': '?1',
    'sec-fetch-dest': 'document',
    'accept-language': 'en-US,en;q=0.9,ur;q=0.8',
}

COMPLETE_CARD_HEADERS = {
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
    'sec-ch-ua': '"Google Chrome"90", "Chromium";v="90", ";Not A Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'Upgrade-Insecure-Requests': '1',
    'Origin': 'https://live.adyen.com',
    'Content-Type': 'application/x-www-form-urlencoded',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.128 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-User': '?1',
    'Sec-Fetch-Dest': 'document',
    'Referer': 'https://live.adyen.com/hpp/pay.shtml',
    'Accept-Language': 'en-US,en;q=0.9'
}

MAKE_PAYMENT_HEADERS = {
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
    'sec-ch-ua': '"Google Chrome"90", "Chromium";v="90", ";Not A Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'Upgrade-Insecure-Requests': '1',
    'Origin': 'https://www.footlocker.com.au',
    'Content-Type': 'application/x-www-form-urlencoded',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.128 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Sec-Fetch-Site': 'cross-site',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Dest': 'document',
    'Referer': 'https://www.footlocker.com.au/',
    'Accept-Language': 'en-US,en;q=0.9,ur;q=0.8'
}

# urls
CART_URL = 'https://www.footlocker.com.au/en/addtocart?SynchronizerToken={token}&Ajax=true&Relay42_Category=Product%20Pages&acctab-tabgroup-{prod_id}=null&Quantity_{SKU_id}=1&SKU={SKU_id}'
CHECKOUT_URL = 'https://www.footlocker.com.au/en/checkout-overview?SynchronizerToken={token}'
CHECK_DISPATCH_URL = 'https://www.footlocker.com.au/INTERSHOP/web/FLE/FootlockerAustraliaPacific-Footlocker_AU-Site/en_AU/-/AUD/ViewCheckoutOverview-Dispatch'
CARD_URL = 'https://live.adyen.com/hpp/completeCard.shtml'
PAY_URL = 'https://live.adyen.com/hpp/pay.shtml'
