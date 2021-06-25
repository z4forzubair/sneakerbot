import requests
from requests.exceptions import Timeout
import re
from bs4 import BeautifulSoup as bs
import json
import random
from churchaio.models import Profile
import time


class FootlockerBot:
    def __init__(self, url, task):
        self.task = task
        self.url = url
        # regex variables to be used
        self.sync_token_regex = re.compile('name=\"SynchronizerToken\"\s*value=\"(.*)\"/>')
        self.cart_url_regex = re.compile('class="fl-load-animation"\s*data-ajaxcontent-url=\"(.*)\"')
        self.id_regex = re.compile('v=(.*)')
        self.addressID_regex = re.compile('name="shipping_AddressID"\s*value=\"(.*)\"')

        self.response_status = True
        self.session = requests.Session()
        try:
            breakpoint()
            self.response = self.session.get(url, timeout=120)
            breakpoint()
            self.response_status = True if self.response.status_code == requests.codes.ok else False
        except Exception as ex:
            breakpoint()
            self.response_status = False

    # returns the status of the requests' response at any time
    def returnStatus(self):
        return self.response_status

    # sets the response status to false
    def exitProgram(self, ex):
        breakpoint()
        exit_error = ex
        self.response_status = False

    # get the list of available shoe sizes
    def __sizes_list(self, size_url, headers):
        try:
            breakpoint()
            size_resp = self.session.get(size_url, headers=headers, timeout=120)
            self.response_status = True if size_resp.status_code == requests.codes.ok else False
            breakpoint()
            html = json.loads(size_resp.content.decode()).get("content")
            parsed_html = bs(html, 'html.parser')  # parsing # and I have toled Beautiful to parse it as an html file
            upr_div = parsed_html.find_all('div', class_='fl-product-size')[1]
            buttons = upr_div.find_all('button', attrs={'data-form-field-target': 'SKU'})
            sizes = []
            SKUs = []
            for x in buttons:
                sizes.append(x.span.text)
                SKUs.append(x['data-form-field-value'])
            return sizes, SKUs
        except Exception as ex:
            breakpoint()
            self.exitProgram(ex)

    # get the shoe size to purchase
    def __get_size(self, sizes):
        shoe_size = self.task.shoe_size
        size = random.choice(sizes) if shoe_size == -1 or shoe_size not in sizes else shoe_size
        breakpoint()
        return size

    #  for that size, get SKU_id which is sent in the addToCart link
    def __get_SKU_id(self, SKUs, sizes, size):
        i = sizes.index(size)
        return SKUs[i]

    # add to cart helper
    def __addtocart(self, SKU_id, payload, headers):
        # obtain product id of the shoe from original
        prod_id = self.id_regex.findall(self.url)
        breakpoint()
        # Synchronizer Token
        global token
        token = self.sync_token_regex.findall(self.response.content.decode())
        breakpoint()
        cart_url = f"https://www.footlocker.com.au/en/addtocart?SynchronizerToken={token[0]}&Ajax=true&Relay42_Category=Product%20Pages&acctab-tabgroup-{prod_id[0]}=null&Quantity_{SKU_id}=1&SKU={SKU_id}"
        # time.sleep(5)  # to avoid captcha on add to cart
        try:
            breakpoint()
            cart_resp = self.session.request("POST", cart_url, headers=headers, data=payload, timeout=120)
            breakpoint()
            # to check the response is 200
            cart_resp_temp = cart_resp
            cart_resp.close()
            breakpoint()
            self.response_status = True if cart_resp_temp.status_code == requests.codes.ok else False
        except Exception as ex:
            breakpoint()
            # print('Exception addToCart: ', ex)
            self.exitProgram(ex)

    def addToCart(self):
        breakpoint()
        payload = {}
        headers = {
            'authority': 'www.footlocker.com.au',
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'accept-encoding': 'gzip, deflate, br',  # but to write
            'accept-language': 'en-US,en;q=0.9,ur;q=0.8',
            'content-length': '0',
            'origin': 'https://www.footlocker.com.au',
            'referer': self.url,  # contains the shoe id link
            'sec-ch-ua': '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36',
            'x-requested-with': 'XMLHttpRequest'
        }
        # the available sizes of the shoes are obtained from a separate api call
        # the link of the api is present in thr url response
        sizes_url = self.cart_url_regex.findall(self.response.content.decode())[0]
        sizes, SKUs = self.__sizes_list(sizes_url, headers)
        if not self.response_status:
            return self.returnStatus()
        size = self.__get_size(sizes)
        SKU_id = self.__get_SKU_id(SKUs, sizes, size)
        breakpoint()
        # print('Add to Cart')
        self.__addtocart(SKU_id, payload, headers)
        return self.returnStatus()

    # it gives attributes to be used in checkout Dispatch
    def __checkoutForm(self):
        payload = {}
        headers = {
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
        breakpoint()
        checkout_url = f'https://www.footlocker.com.au/en/checkout-overview?SynchronizerToken={token[0]}'
        # print('checkout Form')
        try:
            breakpoint()
            check_form_resp = self.session.request("GET", checkout_url, headers=headers, data=payload, timeout=120)
            breakpoint()
            # print(check_form_resp)
            if check_form_resp.status_code != requests.codes.ok:
                ex = 'Checkout Form Failed'
                self.exitProgram(ex)
            return check_form_resp
        except Exception as ex:
            breakpoint()
            # print('Exception Checkout Form: ', ex)
            self.exitProgram(ex)
            return False

    # makes the api call with shipping details to get the attributes for payment url
    def __checkoutDispatch(self, check_form_resp):
        headers = {
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
            # 'referer': f'https://www.footlocker.com.au/INTERSHOP/web/WFS/FootlockerAustraliaPacific-Footlocker_AU-Site/en_AU/-/AUD/ViewData-Start/489307239;pgid=wYRikOUTkohSRpKQX4t4PUhe0000Xg38xjVy?JumpTarget=ViewCheckoutOverview-Start&SynchronizerToken={token[0]}',
            'accept-language': 'en-US,en;q=0.9,ur;q=0.8',
        }
        # the shipping details are later to be taken from the user
        # hard coded here

        if self.task.profile.salutation == Profile.SALUTATION.MR:
            salutation = 'common.account.salutation.mr.text'
        else:
            salutation = 'common.account.salutation.ms.text'
        first_name = self.task.profile.first_name
        last_name = self.task.profile.last_name
        country_code = 'AU'  # as only Australia required here
        address1 = self.task.profile.address.address1
        address2 = str(self.task.profile.address.address2)
        city = self.task.profile.address.city
        postal_code = str(self.task.profile.address.postal_code)
        state = 'VIC'
        # state = self.task.profile.address.state
        phone_home = self.task.profile.contact.raw_input
        birthday_day = str(self.task.profile.day)
        birthday_month = str(self.task.profile.month)
        birthday_year = str(self.task.profile.year)
        addressID = self.addressID_regex.findall(check_form_resp.content.decode())[0]
        email = self.task.profile.email
        PaymentServiceSelection = 'B7.sFf0SCQgAAAFxGLiKmMSH'
        UserDeviceTypeForPaymentRedirect = 'Desktop'
        ShippingMethodUUID = 'q2qsFf0LKIIAAAFceVW0XjJJ'

        # salutation = 'common.account.salutation.mr.text' # 'common.account.salutation.ms.text' for Ms
        # first_name = 'Jacob'
        # last_name = 'Church'
        # country_code = 'AU'
        # address1 = '4 crain court harrington park'
        # address2 = '2567'
        # city = 'Melbourne'
        # postal_code = '3000'
        # state = 'VIC'
        # phone_home = '390355511'
        # birthday_day = '30'
        # birthday_month = '12'
        # birthday_year = '1990'
        # addressID = self.addressID_regex.findall(check_form_resp.content.decode())[0]
        # email = 'zubairpunjab786@gmail.com'
        # password = 'Abc123.'
        # PaymentServiceSelection = 'B7.sFf0SCQgAAAFxGLiKmMSH'
        # UserDeviceTypeForPaymentRedirect = 'Desktop'
        # ShippingMethodUUID = 'q2qsFf0LKIIAAAFceVW0XjJJ'

        payload = {
            'SynchronizerToken': token[0],
            'isshippingaddress': '',
            'billing_Title': salutation,
            'billing_FirstName': first_name,
            'billing_LastName': last_name,
            'billing_CompanyName': '',
            'billing_CountryCode': country_code,
            'billing_Address1': address1,
            'billing_Address2': address2,
            'billing_City': city,
            'billing_PostalCode': postal_code,
            'billing_State': state,
            'billing_PhoneHome': phone_home,
            'billing_BirthdayRequired': 'true',
            'billing_Birthday_Day': birthday_day,
            'billing_Birthday_Month': birthday_month,
            'billing_Birthday_Year': birthday_year,
            'billing_AddressID': addressID,
            'email_Email': email,
            'billing_ShippingAddressSameAsBilling': 'true',
            'isshippingaddress': '',
            'shipping_Title': salutation,
            'shipping_FirstName': first_name,
            'shipping_LastName': last_name,
            'shipping_CompanyName': '',
            'shipping_CountryCode': country_code,
            'shipping_Address1': address1,
            'shipping_Address2': address2,
            'shipping_City': city,
            'shipping_PostalCode': postal_code,
            'shipping_State': state,
            'shipping_PhoneHome': phone_home,
            # 'optionsForm_AccountCreation': 'true',
            # 'CheckoutRegisterForm_Password': password,
            'CheckoutRegisterForm_Password': '',
            'promotionCode': '',
            'PaymentServiceSelection': PaymentServiceSelection,
            'UserDeviceTypeForPaymentRedirect': UserDeviceTypeForPaymentRedirect,
            # not necessary 'UserDeviceFingerprintForPaymentRedirect' : '0400bpNfiPCR%2FAUNf94lis1ztp16088t6Mybnrp%2FXmcfWoVVgr%2BRt2dAZHTHKKElGtacqWYHG919cPZAs3w4eTjAAemnINQu20lpE6D%2BDwUuc%2FsxAoWvl5bTSDY887kVsVV4Cd8WIxXHiB6n7s4lwMbUt4S%2BQGiegQbHW1G32q0vK172li%2BP5kNt%2FhyJCeZV1Dbz8NEFL8dDGo13smrMz9i85BmnGpGk%2BPpzyAZ7syHQUqFApa%2FrRMlJ5QE9hgJV1EfL15362ubh5w%2BNn0RPTzA%2FkNxQl%2FaUuqWvSdu3DZ2D0kFMgGebJUzGiWPmsNMLCpfbYgiGUSUL4yVVjI2RJ6%2BNcGG%2FcdkIMFbm6Yf0%2FpTJUUwTWoMCQ0eYOQydKgnOIDKXq4HnEqNOos1c6njJgQh%2F4vXJiqy0MXMQOThNipDmXv9I185O%2ByC2f3lLEO0Tay66NZEyiLNePemJKSIdwO9O5ZtntuUkG6NTrhfKkelca2wtcERyjyNeULeOYKpDDGGH5mNV6QxgbcnqT3LYd4%2BPRZVd56Ict%2B1YIsTlyS1mz15Xmhm%2FqapvjPhUg2tzrFTFGHcAi%2BY8pEM%2BBzSiGEPrdzvSSW7wLSG9660b%2Bk2qutNhM2Ay367TndZi8nZ5OpdsDgoP5CMsPd5CSOP8F%2FeyAGlZmakw%2B7cndFvPrWIExT61SmUEojvMB%2FK25QSlST7dKULPxBs5mS%2BTR2OD1o9lFD7yEUx4rW%2BlGJnb6gtmCXf%2BmvvWgPnrWo530CaM8EgnsqIgGog%2BdLetTmUBU1%2ByioQonmwROuiCBJVw9IRDLb0JdqJazYFDTwyYua03pLNORh3o9%2BX24SE1WdmdLcJpGsyZh0oClnCJyAfUMZ5LKFoA4BbW41P4v%2Bi7kYvuVLUfVkXwXd4127YB84%2BPOrI4MlDvgCJ6XflMpM5YbymrVY7rLMnUY2Yy4xZkFqaUZegb%2BKaePAdj0dC1DOkZ9ybRxHxfYV3WeA0UYsMZmVY5fSMcCN0j9wmCHP1KIsusqkp7u6828R9GQm6kHLdnyFIQwcv2RovzmXNT1g9RJPeBNicb7yAKVlYU34%2FVcdsVtZ270iAXyzfkdDO%2FTDp0UzLYS%2BKjA5OTNopRQtncHmePC%2B1SwejOX5dhKGYrsu13rc4RCbryu9G8AaRxi%2FUgQBHzxwUkaRoD62ZVUGYGOlIpEBWlVkisSm0PDl1NDWoa%2Fz5zOlE21SSHNLtmpo%2FomlkT6OZX0dWa6jjzxvF3IPTuvasRoSbH0GHZiJHhCyhIDNcTfqYAndlMe7aRkDkd2CSCXDwxgWQHuVc06NDUWnOZYN7cE4nZ3meVnnb6dxDioksejgtHHqqE28hv5t2asbd8NQZ%2Bi8aFjp2buuK69Oy8ERl2acnO6ECFet8WnTRNo6m%2BqNyABHWwfsQsl2RE758GOsSWD8YuD89QLg81FSfhWxslLNWDPKUtbyQHfzuN4m6EiADt8M16DcJXub41RnJ%2FCgiXjad65osFSDG%2BzNqC2yc9rUH4ur27WLd4LjvTDOiKr3Psbd%2B0neYDQK1N4MtGzsYjNmX7PeQmnL28UjHOmZVf9RHlbCpTNyUHHAK1yGv0qCAU0Psot7aVT31SgfbGSWQ5umrETs00UqHTJAXHIvfocnEHwtZhjivy4GmCWCuOV%2FAtvb1TtQi94AZKWwmGtTFYZliFBpt9JMCAQDAy%2BESM%2F3oO4%2FCKFlmjcj4hzdL5yx37HUytO6KMByEu0rSiaU7b7rFP6MGMlrdzeNWV2gQ%3D'
            'ShippingMethodUUID': ShippingMethodUUID,
            'termsAndConditions': 'on',
            'GDPRDataComplianceRequired': 'false',
            'email_Newsletter': 'true',
            'sendOrder': ''
        }
        check_disptach_url = "https://www.footlocker.com.au/INTERSHOP/web/WFS/FootlockerAustraliaPacific-Footlocker_AU-Site/en_AU/-/AUD/ViewCheckoutOverview-Dispatch"
        # print('checkout-overview-Dispatch')
        try:
            breakpoint()
            cd_resp = self.session.request("POST", check_disptach_url, headers=headers, data=payload, timeout=120)
            breakpoint()
            # print(cd_resp)
            if cd_resp.status_code != requests.codes.ok:
                ex = 'Checkout Dispatch Failed'
                self.exitProgram(ex)
            breakpoint()
            return cd_resp
        except Exception as ex:
            breakpoint()
            # print('Exception Checkout Dispatch: ', ex)
            self.exitProgram(ex)
            return False

    # it will make the 'Make the Payment' call
    def __completeCard(self, pay_resp):
        html = pay_resp.text
        parsed_html = bs(html, 'html.parser')  # parsing # and I have toled Beautiful to parse it as an html file
        # all the info is present in input tags only, it also contains a lot of other html
        inputs = parsed_html.findAll('input')
        payload = {}
        for input in inputs:
            if input.has_attr('value'):  # 1 or 2 values are empty, and also, name is also empty
                payload[input.attrs['name']] = input.attrs['value']
        # these hard coded values to be taken from user later
        # cardNumber = '4739 4603 4239 1535'
        # expiryMonth = '08'
        # expiryYear = '2025'
        # cvcCode = '188'
        cc_number = self.task.profile.payment.cc_number
        cardNumber = ' '.join([cc_number[i:i + 4] for i in range(0, len(cc_number), 4)])
        # cardHolderName = 'Jacob Church'
        cardHolderName = self.task.profile.first_name + ' ' + self.task.profile.last_name
        cc_expiry = self.task.profile.payment.cc_expiry
        month = cc_expiry.month
        month = str(month)
        if len(month) == 1:
            month = month + month
            month = month[:0] + '0' + month[:1]
        expiryMonth = month
        year = cc_expiry.year
        year = str(year)
        expiryYear = year
        cvcCode = self.task.profile.payment.cc_code
        payload['displayGroup'] = 'card'
        # payload['paypal.storeOcDetails'] = 'false'	# this is by default false in the input tags
        payload['card.cardNumber'] = cardNumber
        payload['card.cardHolderName'] = cardHolderName
        payload['card.expiryMonth'] = expiryMonth
        payload['card.expiryYear'] = expiryYear
        payload['card.cvcCode'] = cvcCode
        # payload['card.storeOcDetails'] = 'true'	# this is by default true in the input tags
        headers = {
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
            # 'Cookie': 'hppsession=6a565a497a35334c367339596151675357502b746858656c437244516477336c4e59527a3172595135594d3d:0; JSESSIONID=44FECA23ACDF8D10EC348365C6BAA7CE.live12e; hppsession=617256347a75313078752b52436a3130484d4c546d44663831346b44376a32566b4b4864444936424767593d:1; JSESSIONID=7B06B46B335673CBCE474A0D75283A8E.live9e'
        }
        card_url = "https://live.adyen.com/hpp/completeCard.shtml"
        # print('Complete Card')
        # time.sleep(5)
        try:
            breakpoint()
            card_resp = self.session.request("POST", card_url, headers=headers, data=payload, timeout=120)
            breakpoint()
            # print(card_resp)
            # print('history')
            # print(card_resp.history)

            # the following for checking payment failed status, later
            # mydivs = soup.find_all("div", {"class": "fl-notification__error"})[0].text
            if card_resp.status_code != requests.codes.ok:
                ex = 'Not 200 response for card completion'
                self.exitProgram(ex)
        except Exception as ex:
            breakpoint()
            # print('Exception at Complete Card: ', ex)
            self.exitProgram(ex)
        return self.returnStatus()

    # it will open the payment page
    def __makePayment(self, cd_resp):
        html = cd_resp.text
        parsed_html = bs(html, 'html.parser')  # parsing # and I have toled Beautiful to parse it as an html file
        # all the required values are present in the input tags of the response
        # it actually contains input tags only, with few exceptions
        inputs = parsed_html.findAll('input')
        payload = {}
        for input in inputs:
            payload[input.attrs['name']] = input.attrs['value']
        headers = {
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
            # 'Cookie': 'hppsession=596b5365305241514c2b70724d664b6f485950512b2b6b36634677436d7a444e312b6830425a324c706b553d:0; JSESSIONID=B70B4853F38FC9B18B9F8DA9452C4360.live110e; hppsession=617256347a75313078752b52436a3130484d4c546d44663831346b44376a32566b4b4864444936424767593d:1; JSESSIONID=7B06B46B335673CBCE474A0D75283A8E.live9e'
        }
        pay_url = "https://live.adyen.com/hpp/pay.shtml"
        # print('Payment page')
        try:
            breakpoint()
            pay_resp = self.session.request("POST", pay_url, headers=headers, data=payload, timeout=120)
            breakpoint()
            # print(pay_resp)
            if pay_resp.status_code != requests.codes.ok:
                ex = 'Payment page failed'
                self.exitProgram(ex)
                return self.returnStatus()
            return self.__completeCard(pay_resp)
        except Exception as ex:
            breakpoint()
            # pay_issue = True
            # print('Exception payment page: ', ex)
            self.exitProgram(ex)
            return self.returnStatus()

    def checkout(self):
        check_form_resp = self.__checkoutForm()
        if not self.response_status:
            return self.returnStatus()
        cd_resp = self.__checkoutDispatch(check_form_resp)
        if not self.response_status:
            return self.returnStatus()
        final_resp = self.__makePayment(cd_resp)
        return self.returnStatus()

###################################
