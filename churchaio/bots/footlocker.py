import requests
from requests.exceptions import Timeout
from bs4 import BeautifulSoup as bs
import json
import random
from churchaio.bots.utils.utils_footlocker import *
from churchaio.models import Profile
import time


class FootlockerBot:
    def __init__(self, url, task):
        self.task = task
        self.url = url

        self.sizes = []
        self.SKUs = []
        self.size = None
        self.SKU_id = None

        self.response_status = True
        self.session = requests.Session()
        try:
            self.response = self.session.get(url, timeout=120)
            self.response.raise_for_status()
        except Exception as ex:
            self.response_status = False

    # returns the status of the requests' response at any time
    def returnStatus(self):
        return self.response_status

    # sets the response status to false
    def exitProgram(self, ex):
        exit_error = ex
        self.response_status = False

    # get the list of available shoe sizes
    def __sizes_list(self, size_url):
        try:
            size_resp = self.session.get(size_url, headers=CART_HEADERS, timeout=120)
            size_resp.raise_for_status()
            html = json.loads(size_resp.content.decode()).get("content")
            parsed_html = bs(html, 'html.parser')  # parsing # and I have toled Beautiful to parse it as an html file
            upr_div = parsed_html.find_all('div', class_='fl-product-size')[1]
            buttons = upr_div.find_all('button', attrs={'data-form-field-target': 'SKU'})
            for x in buttons:
                self.sizes.append(x.span.text)
                self.SKUs.append(x['data-form-field-value'])
        except Exception as ex:
            self.exitProgram(ex)

    # get the shoe size to purchase
    def __set_size(self):
        shoe_size = self.task.shoe_size
        self.size = random.choice(self.sizes) if shoe_size == -1 or shoe_size not in self.sizes else shoe_size

    #  for that size, get SKU_id which is sent in the addToCart link
    def __set_SKU_id(self):
        i = self.sizes.index(self.size)
        self.SKU_id = self.SKUs[i]

    # add to cart helper
    def __addtocart(self, payload):
        # obtain product id of the shoe from original
        prod_id = ID_REGEX.findall(self.url)
        # Synchronizer Token
        global token
        token = SYNC_TOKEN_REGEX.findall(self.response.content.decode())
        cart_url = CART_URL.format(token=token[0], prod_id=prod_id[0], SKU_id=self.SKU_id)
        # time.sleep(5)  # to avoid captcha on add to cart
        try:
            cart_resp = self.session.request("POST", cart_url, headers=CART_HEADERS, data=payload, timeout=120)
            # to check the response is 200
            cart_resp.raise_for_status()
            cart_resp.close()
        except Exception as ex:
            # print('Exception addToCart: ', ex)
            self.exitProgram(ex)

    def addToCart(self):
        payload = {}
        CART_HEADERS['referer'] = self.url
        # the available sizes of the shoes are obtained from a separate api call
        # the link of the api is present in thr url response
        sizes_url = CART_URL_REGEX.findall(self.response.content.decode())[0]
        self.__sizes_list(sizes_url)
        if not self.response_status:
            return self.returnStatus()
        self.__set_size()
        self.__set_SKU_id()
        # print('Add to Cart')
        self.__addtocart(payload)
        return self.returnStatus()

    # it gives attributes to be used in checkout Dispatch
    def __checkoutForm(self):
        payload = {}
        checkout_url = CHECKOUT_URL.format(token=token[0])
        try:
            check_form_resp = self.session.request("GET", checkout_url, headers=CHECKOUT_FORM_HEADERS, data=payload,
                                                   timeout=120)
            check_form_resp.raise_for_status()
            return check_form_resp
        except Exception as ex:
            self.exitProgram(ex)
            return False

    # makes the api call with shipping details to get the attributes for payment url
    def __checkoutDispatch(self, check_form_resp):
        # payload data
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
        state = self.task.profile.address.state
        phone_home = self.task.profile.contact.raw_input
        birthday_day = str(self.task.profile.day)
        birthday_month = str(self.task.profile.month)
        birthday_year = str(self.task.profile.year)
        addressID = ADDRESS_ID_REGEX.findall(check_form_resp.content.decode())[0]
        email = self.task.profile.email
        PaymentServiceSelection = 'B7.sFf0SCQgAAAFxGLiKmMSH'
        UserDeviceTypeForPaymentRedirect = 'Desktop'
        ShippingMethodUUID = 'q2qsFf0LKIIAAAFceVW0XjJJ'

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
            # shipping_AddressID: 'tsSsFf0S.9AAAAF664xvY0ep',
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
            'CheckoutRegisterForm_Password': '',
            'promotionCode': '',
            'PaymentServiceSelection': PaymentServiceSelection,
            'UserDeviceTypeForPaymentRedirect': UserDeviceTypeForPaymentRedirect,
            'ShippingMethodUUID': ShippingMethodUUID,
            'termsAndConditions': 'on',
            'GDPRDataComplianceRequired': 'false',
            'email_Newsletter': 'true',
            'sendOrder': ''
        }
        # print('checkout-overview-Dispatch')
        try:
            cd_resp = self.session.request("POST", CHECK_DISPATCH_URL, headers=CHECKOUT_DISPATCH_HEADERS, data=payload,
                                           timeout=120)
            cd_resp.raise_for_status()
            return cd_resp
        except Exception as ex:
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

        try:
            card_resp = self.session.request("POST", CARD_URL, headers=COMPLETE_CARD_HEADERS, data=payload, timeout=120)
            card_resp.raise_for_status()
        except Exception as ex:
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

        try:
            pay_resp = self.session.request("POST", PAY_URL, headers=MAKE_PAYMENT_HEADERS, data=payload, timeout=120)
            pay_resp.raise_for_status()
            return self.__completeCard(pay_resp)
        except Exception as ex:
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
