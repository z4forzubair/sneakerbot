import requests
from requests.exceptions import Timeout
import re
from bs4 import BeautifulSoup as bs
import json
import inquirer
import random
import sys
import time

# exit program at any point
def exitProgram():
	print('Exiting...')
	sys.exit()

# for taking url of the shoe
def get_url():
	questions = [
		inquirer.Text('url', message="Enter the url"),
	]
	answers = inquirer.prompt(questions)
	return answers['url']

# regex variables to be used
sync_token_regex = re.compile('name=\"SynchronizerToken\"\s*value=\"(.*)\"/>')
cart_url_regex = re.compile('class="fl-load-animation"\s*data-ajaxcontent-url=\"(.*)\"')
id_regex = re.compile('v=(.*)')
addressID_regex = re.compile('name="shipping_AddressID"\s*value=\"(.*)\"')

session = requests.Session()
url = get_url()
try:
	response = session.get(url, timeout=120)
except Timeout as ex:
	print('Main url: ', ex)
	exitProgram()

# get url of the api for shoe sizes
def get_sizes_url():
	return cart_url_regex.findall(response.content.decode())[0]

# get the list of available shoe sizes 
def sizes_list(size_url, headers):
	try:
		size_resp = session.get(size_url, headers = headers, timeout=120)
		html = json.loads(size_resp.content.decode()).get("content")
		parsed_html = bs(html, 'html.parser')  # parsing # and I have toled Beautiful to parse it as an html file
		upr_div = parsed_html.find_all('div', class_='fl-product-size')[1]
		buttons = upr_div.find_all('button', attrs={'data-form-field-target':'SKU'})
		sizes = []
		SKUs = []
		for x in buttons:
			sizes.append(x.span.text)
			SKUs.append(x['data-form-field-value'])
		return sizes, SKUs
	except Timeout as ex:
		print('Exception at getting Sizes: ', ex)
		exitProgram()

# get the shoe size to purchase
def get_size(sizes):
	# questions = [
	# 	inquirer.List('size',
	# 		message="What size do you need?",
	# 		choices=sizes,
	# 		),
	# ]
	# answers = inquirer.prompt(questions)
	# return answers['size']
	return random.choice(sizes)		# choose a random shoe size from the list

#  for that size, get SKU_id which is sent in the addToCart link
def get_SKU_id(SKUs, sizes, size):
	i = sizes.index(size)
	return SKUs[i]

def addtocart(SKU_id, payload, headers):
	# obtain product id of the shoe from original
	prod_id = id_regex.findall(url)
	print('prod_id')
	print(prod_id)
	# Synchronizer Token
	global token
	token = sync_token_regex.findall(response.content.decode())
	print('token')
	print(token)
	cart_url = f"https://www.footlocker.com.au/en/addtocart?SynchronizerToken={token[0]}&Ajax=true&Relay42_Category=Product%20Pages&acctab-tabgroup-{prod_id[0]}=null&Quantity_{SKU_id}=1&SKU={SKU_id}"
	print('cart_url')
	print(cart_url)
	time.sleep(5)	# to avoid captcha on add to cart
	try:
		cart_resp = session.request("POST", cart_url, headers = headers, data=payload, timeout=120)
		print('Cart response')
		print(cart_resp)
		# to check the response is 200
		return True if cart_resp.status_code == requests.codes.ok else False
	except Timeout as ex:
		print('Exception addToCart: ', ex)
		exitProgram()

def addToCart():
	payload = {}
	headers = {
	  'authority': 'www.footlocker.com.au',
	  'accept': 'application/json, text/javascript, */*; q=0.01',
	  'accept-encoding': 'gzip, deflate, br',          # but to write
	  'accept-language': 'en-US,en;q=0.9,ur;q=0.8',
	  'content-length': '0',
	  'origin': 'https://www.footlocker.com.au',
	  'referer': url,     #contains the shoe id link
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
	sizes_url = get_sizes_url()
	sizes, SKUs = sizes_list(sizes_url, headers)
	size = get_size(sizes)
	SKU_id = get_SKU_id(SKUs, sizes, size)
	print('purchaing size')
	print(size)
	print('SKU_id')
	print(SKU_id)
	print('Add to Cart')
	return addtocart(SKU_id, payload, headers)

# it gives attributes to be used in checkout Dispatch
def checkoutForm():
	payload={}
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
	checkout_url = f'https://www.footlocker.com.au/en/checkout-overview?SynchronizerToken={token[0]}'
	print('checkout Form')
	try:
		check_form_resp = session.request("GET", checkout_url, headers=headers, data=payload, timeout=120)
		print(check_form_resp)
		if check_form_resp.status_code != requests.codes.ok:
			print('Checkout Form Failed')
			exitProgram()
		return check_form_resp
	except Timeout as ex:
		print('Exception Checkout Form: ', ex)
		exitProgram()

# makes the api call with shipping details to get the attributes for payment url
def checkoutDispatch(check_form_resp):
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
	salutation = 'common.account.salutation.mr.text' # 'common.account.salutation.ms.text' for Ms
	first_name = 'Jacob'
	last_name = 'Church'
	country_code = 'AU'
	address1 = '4 crain court harrington park'
	address2 = '2567'
	city = 'Melbourne'
	postal_code = '3000'
	state = 'VIC'
	phone_home = '390355511'
	birthday_day = '30'
	birthday_month = '12'
	birthday_year = '1990'
	addressID = addressID_regex.findall(check_form_resp.content.decode())[0]
	email = 'zubairpunjab786@gmail.com'
	password = 'Abc123.'
	PaymentServiceSelection = 'B7.sFf0SCQgAAAFxGLiKmMSH'
	UserDeviceTypeForPaymentRedirect = 'Desktop'
	ShippingMethodUUID = 'q2qsFf0LKIIAAAFceVW0XjJJ'
	payload = {
	  'SynchronizerToken' : token[0],
	  'isshippingaddress': '',
	  'billing_Title' : salutation,
	  'billing_FirstName' : first_name,
	  'billing_LastName' : last_name,
	  'billing_CompanyName' : '',
	  'billing_CountryCode' : country_code,
	  'billing_Address1' : address1,
	  'billing_Address2' : address2,
	  'billing_City' : city,
	  'billing_PostalCode' : postal_code,
	  'billing_State' : state,
	  'billing_PhoneHome' : phone_home,
	  'billing_BirthdayRequired' : 'true',
	  'billing_Birthday_Day' : birthday_day,
	  'billing_Birthday_Month' : birthday_month,
	  'billing_Birthday_Year' : birthday_year,
	  'billing_AddressID' : addressID,
	  'email_Email' : email,
	  'billing_ShippingAddressSameAsBilling' : 'true',
	  'isshippingaddress' : '',
	  'shipping_Title' : salutation,
	  'shipping_FirstName' : first_name,
	  'shipping_LastName' : last_name,
	  'shipping_CompanyName' : '',
	  'shipping_CountryCode' : country_code,
	  'shipping_Address1' : address1,
	  'shipping_Address2' : address2,
	  'shipping_City' : city,
	  'shipping_PostalCode' : postal_code,
	  'shipping_State' : state,
	  'shipping_PhoneHome' : phone_home,
	  'optionsForm_AccountCreation' : 'true',
	  'CheckoutRegisterForm_Password' : password,
	  'promotionCode' : '',
	  'PaymentServiceSelection' : PaymentServiceSelection,
	  'UserDeviceTypeForPaymentRedirect' : UserDeviceTypeForPaymentRedirect,
	  # not necessary 'UserDeviceFingerprintForPaymentRedirect' : '0400bpNfiPCR%2FAUNf94lis1ztp16088t6Mybnrp%2FXmcfWoVVgr%2BRt2dAZHTHKKElGtacqWYHG919cPZAs3w4eTjAAemnINQu20lpE6D%2BDwUuc%2FsxAoWvl5bTSDY887kVsVV4Cd8WIxXHiB6n7s4lwMbUt4S%2BQGiegQbHW1G32q0vK172li%2BP5kNt%2FhyJCeZV1Dbz8NEFL8dDGo13smrMz9i85BmnGpGk%2BPpzyAZ7syHQUqFApa%2FrRMlJ5QE9hgJV1EfL15362ubh5w%2BNn0RPTzA%2FkNxQl%2FaUuqWvSdu3DZ2D0kFMgGebJUzGiWPmsNMLCpfbYgiGUSUL4yVVjI2RJ6%2BNcGG%2FcdkIMFbm6Yf0%2FpTJUUwTWoMCQ0eYOQydKgnOIDKXq4HnEqNOos1c6njJgQh%2F4vXJiqy0MXMQOThNipDmXv9I185O%2ByC2f3lLEO0Tay66NZEyiLNePemJKSIdwO9O5ZtntuUkG6NTrhfKkelca2wtcERyjyNeULeOYKpDDGGH5mNV6QxgbcnqT3LYd4%2BPRZVd56Ict%2B1YIsTlyS1mz15Xmhm%2FqapvjPhUg2tzrFTFGHcAi%2BY8pEM%2BBzSiGEPrdzvSSW7wLSG9660b%2Bk2qutNhM2Ay367TndZi8nZ5OpdsDgoP5CMsPd5CSOP8F%2FeyAGlZmakw%2B7cndFvPrWIExT61SmUEojvMB%2FK25QSlST7dKULPxBs5mS%2BTR2OD1o9lFD7yEUx4rW%2BlGJnb6gtmCXf%2BmvvWgPnrWo530CaM8EgnsqIgGog%2BdLetTmUBU1%2ByioQonmwROuiCBJVw9IRDLb0JdqJazYFDTwyYua03pLNORh3o9%2BX24SE1WdmdLcJpGsyZh0oClnCJyAfUMZ5LKFoA4BbW41P4v%2Bi7kYvuVLUfVkXwXd4127YB84%2BPOrI4MlDvgCJ6XflMpM5YbymrVY7rLMnUY2Yy4xZkFqaUZegb%2BKaePAdj0dC1DOkZ9ybRxHxfYV3WeA0UYsMZmVY5fSMcCN0j9wmCHP1KIsusqkp7u6828R9GQm6kHLdnyFIQwcv2RovzmXNT1g9RJPeBNicb7yAKVlYU34%2FVcdsVtZ270iAXyzfkdDO%2FTDp0UzLYS%2BKjA5OTNopRQtncHmePC%2B1SwejOX5dhKGYrsu13rc4RCbryu9G8AaRxi%2FUgQBHzxwUkaRoD62ZVUGYGOlIpEBWlVkisSm0PDl1NDWoa%2Fz5zOlE21SSHNLtmpo%2FomlkT6OZX0dWa6jjzxvF3IPTuvasRoSbH0GHZiJHhCyhIDNcTfqYAndlMe7aRkDkd2CSCXDwxgWQHuVc06NDUWnOZYN7cE4nZ3meVnnb6dxDioksejgtHHqqE28hv5t2asbd8NQZ%2Bi8aFjp2buuK69Oy8ERl2acnO6ECFet8WnTRNo6m%2BqNyABHWwfsQsl2RE758GOsSWD8YuD89QLg81FSfhWxslLNWDPKUtbyQHfzuN4m6EiADt8M16DcJXub41RnJ%2FCgiXjad65osFSDG%2BzNqC2yc9rUH4ur27WLd4LjvTDOiKr3Psbd%2B0neYDQK1N4MtGzsYjNmX7PeQmnL28UjHOmZVf9RHlbCpTNyUHHAK1yGv0qCAU0Psot7aVT31SgfbGSWQ5umrETs00UqHTJAXHIvfocnEHwtZhjivy4GmCWCuOV%2FAtvb1TtQi94AZKWwmGtTFYZliFBpt9JMCAQDAy%2BESM%2F3oO4%2FCKFlmjcj4hzdL5yx37HUytO6KMByEu0rSiaU7b7rFP6MGMlrdzeNWV2gQ%3D'
	  'ShippingMethodUUID' : ShippingMethodUUID,
	  'termsAndConditions' : 'on',
	  'GDPRDataComplianceRequired' : 'false',
	  'email_Newsletter' : 'true',
	  'sendOrder' : ''
	}
	check_disptach_url = "https://www.footlocker.com.au/INTERSHOP/web/WFS/FootlockerAustraliaPacific-Footlocker_AU-Site/en_AU/-/AUD/ViewCheckoutOverview-Dispatch"
	print('checkout-overview-Dispatch')
	try:
		cd_resp = session.request("POST", check_disptach_url, headers=headers, data=payload, timeout=120)
		print(cd_resp)
		if cd_resp.status_code != requests.codes.ok:
			print('Checkout Dispatch Failed')
			exitProgram()
		return cd_resp
	except Timeout as ex:
		print('Exception Checkout Dispatch: ', ex)
		exitProgram()	

# it will make the 'Make the Payment' call
def completeCard(pay_resp):
	html = pay_resp.text
	parsed_html = bs(html, 'html.parser')  # parsing # and I have toled Beautiful to parse it as an html file
	# all the info is present in input tags only, it also contains a lot of other html
	inputs = parsed_html.findAll('input')
	payload = {}
	for input in inputs:
		if input.has_attr('value'):		# 1 or 2 values are empty, and also, name is also empty
			payload[input.attrs['name']] = input.attrs['value']
	# these hard coded values to be taken from user later
	cardNumber = '4739 4603 4239 1535'
	cardHolderName = 'Jacob Church'
	expiryMonth = '08'
	expiryYear = '2025'
	cvcCode = '188'
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
	print('Complete Card')
	time.sleep(5)
	try:
		card_resp = session.request("POST", card_url, headers=headers, data=payload, timeout=120)
		print(card_resp)
		f = open("card_resp_content.txt", "wb")
		f.write(card_resp.content)
		f.close()
		print('history')
		with open('card_resp_history.txt', 'w') as filehandle:
			for listitem in card_resp.history:
				filehandle.write('%s\n' % listitem)
		print(card_resp.history)
		print('headers')
		with open('card_resp_headers.txt', 'w') as filehandle:
			for listitem, val in sorted(card_resp.headers.items()):
				print(listitem, val)
				filehandle.write('%s: %s\n' % (listitem, val))
		print(card_resp.headers)
		print(card_resp.history)
		print(card_resp.status_code)
		# the following for checking payment failed status, later
		# mydivs = soup.find_all("div", {"class": "fl-notification__error"})[0].text
		if card_resp.status_code != requests.codes.ok:
			print('Not 200 response for card completion')
			exitProgram()
	except Timeout as ex:
		print('Exception at Complete Card: ', ex)
		exitProgram()

# it will open the payment page
def makePayment(cd_resp):
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
	print('Payment page')
	try:
		pay_resp = session.request("POST", pay_url, headers=headers, data=payload, timeout=120)
		print(pay_resp)
		if pay_resp.status_code != requests.codes.ok:
			print('Payment page failed')
			exitProgram()
		completeCard(pay_resp)
	except Timeout as ex:
		print('Exception payment page: ', ex)
		exitProgram()		


def checkout():
	check_form_resp = checkoutForm()
	cd_resp = checkoutDispatch(check_form_resp)
	makePayment(cd_resp)


#Main
if addToCart():
	print('Added to Cart Successfully')
	print('Checkout')
	checkout()
	print('Checkout Completed Successfully')
else:
	print('Add to card failed')

##############################
