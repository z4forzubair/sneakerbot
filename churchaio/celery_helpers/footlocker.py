from selenium import webdriver
from time import sleep
from selenium.webdriver.chrome.options import Options  # not used
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import os
import datetime
from webdriver_manager.chrome import ChromeDriverManager

from churchaio.celery_helpers.task_data import get_task_attr


def footlocker_bot(task_id):
    task_attr = get_task_attr(task_id=task_id)
    # to get proxies later

    print(task_attr)

    page = "followers"  # from following or followers

    # account = input('Enter username of the Influencer: ')  # account from
    # yourusername = input('Enter your instagram username: ') #your IG username
    # yourpassword = input('Enter your instagram password: ')  #your IG password

    account = 'clothes_onlline'  # account from
    yourusername = 'z_zzubair'  # your IG username
    yourpassword = ''  # your IG password

    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument(
        '--user-agent="Mozilla/5.0 (iPhone; CPU iPhone OS 12_1_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/16D57"')

    driver = webdriver.Chrome(ChromeDriverManager().install())

    driver.get('https://www.instagram.com/accounts/login/')
    sleep(3)
    sleep(1)
    username_input = driver.find_element_by_css_selector("input[name='username']")
    password_input = driver.find_element_by_css_selector("input[name='password']")
    username_input.send_keys(yourusername)
    password_input.send_keys(yourpassword)
    login_button = driver.find_element_by_xpath("//button[@type='submit']")
    login_button.click()
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(.,'Not Now')]"))).click()
    sleep(3)

    driver.get('https://www.instagram.com/%s' % account)
    sleep(2)
    driver.find_element_by_xpath('//a[contains(@href, "%s")]' % page).click()
    followers_elem = driver.find_element_by_xpath(
        '//*[@id="react-root"]/section/main/div/header/section/ul/li[2]/a/span')
    sleep(2)
    count_str = followers_elem.get_attribute('title')
    count = int(count_str.replace(',', ''))
    print(count)

    x = datetime.datetime.now()
    print('start time: ')
    print(x)
    user_list = []
    sleep(2)

    for i in range(1, count):
        scr1 = driver.find_element_by_xpath('/html/body/div[5]/div/div/div[2]/ul/div/li[%s]' % i)
        driver.execute_script("arguments[0].scrollIntoView();", scr1)
        sleep(1)
        text = scr1.text
        text_split = text.split('\n')  # username at text_split[0]

        # file operation starting
        dirname = os.path.dirname(os.path.abspath(__file__))
        csvfilename = os.path.join(dirname, account + "-" + page + ".txt")
        file_exists = os.path.isfile(csvfilename)
        f = open(csvfilename, 'a')
        f.write(str(i) + ' ' + text_split[0] + '\n')
        f.close()
        print('Follower ' + str(i) + ' ' + text_split[0])
        user_list.append(text_split[0])
        # file write operation ends here

        if i == (count - 1):
            print('Followers noted')
            print(x)

    fake_count = 0
    for i in range(0, (count - 1)):
        print('Noting followers/following count for user ' + user_list[i])
        driver.get('https://www.instagram.com/%s' % user_list[i])
        fol_fol = driver.find_elements_by_xpath(
            '//*[contains(concat( " ", @class, " " ), concat( " ", "g47SY", " " ))]')
        # driver.find_element_by_xpath("//span[@class='g47SY']")
        # driver.find_elements_by_css_selector('span.g47SY')

        fol_str = fol_fol[1].get_attribute('title')
        fol_str1 = fol_str.replace(',', '')
        fo_count = int(fol_str1)
        fol_str = fol_fol[2].text
        fol_str1 = fol_str.replace(',', '')
        fg_count = int(fol_str1)
        if ((fg_count - fo_count) >= 1000):
            fake_count += 1

    print('Influencer: ' + account)
    print('Total Followers: ' + str(count))
    print('Fake Followers: ' + str(fake_count))

    driver.quit()

# def footlocker_bot(task_id):
#     # breakpoint()
#     # print(task_id)
#     aaa = 22
