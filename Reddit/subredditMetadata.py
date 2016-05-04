'''
Scrape subreddits from a list for the meta data: number of subscribers, creation time, mod table.
'''
#----------IMPORTS
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import time
import json

#----------SETTINGS
uname = ''
passw = ''

sub = ['destinythegame', 'nsfw', 'gonewild', 'askreddit', 'horsey', 'ferguson']

#----------FUNCTIONS
def html_to_file(sname, html_source):
        out_file = 'sub_html/'+sname+'.html'
        with open(out_file, 'w') as fo:
                fo.write(html_source.encode('utf8'))
        return

def json_to_file(sname, sub_dict):
        out_file = 'sub_html/'+sname+'_info.json'
        with open(out_file, 'w') as fo:
                json.dump(sub_dict, fo)
                fo.write('\n')
        return

def get_info(sname, driver, quarantined):
        sub_dict = {}
        sub_dict['sub'] = sname

        #-----MOD-TABLE
        mods = []
	mod_table = driver.find_element_by_class_name("moderator-table")
        trs = mod_table.find_elements(By.TAG_NAME, "tr")
        for tr in trs:
                tds = tr.find_elements(By.TAG_NAME, "td")
                user = tds[0].find_element_by_tag_name('a').text
                a_time = tds[1].find_element_by_tag_name('time').get_attribute("datetime")
                permission = tds[2].find_element_by_class_name('permission-bit').text
                mod_dict = {'name': user, 'time': a_time, 'perm': permission}
                mods.append(mod_dict)
        sub_dict['mods'] = mods

        #-----CREATOR
        bottom = driver.find_element_by_class_name("bottom")
        creator = bottom.text.split()[2]
        c_time = bottom.find_element_by_tag_name('time').get_attribute("datetime")
        sub_dict['creator'] = creator
        if creator == 'for':
                sub_dict['creator'] = None
        sub_dict['c_time'] = c_time

        #-----SUBSCRIBERS
        if not quarantined:
                subs = driver.find_element_by_class_name("subscribers")
                sub_num = subs.find_element_by_class_name("number").text
                sub_dict['num_sub'] = sub_num
        else:
                sub_dict['num_sub'] = None

        return sub_dict

def crawl_sub(sname):
        baseurl = 'https://www.reddit.com/r/'+sname+'/about/moderators'
        driver.get(baseurl)
	time.sleep(1)

        #get page title
        page_title = driver.title
        print page_title

        #get sub type
        if page_title.split()[-1] in ['banned', 'private']:
                return

        if page_title in ['reddit.com: page not found', 'search results']:
                return

        if page_title in ['reddit.com: over 18?', 'reddit.com: quarantined']:
                driver.find_element_by_xpath("/html/body/div[2]/div/form/div/button[2]").click()
                time.sleep(1)

        #get page source
        page_source = driver.page_source

        #check if sub is quarantined
        quarantined = True
        try:
                driver.find_element_by_class_name('quarantine-notice')
        except NoSuchElementException:
                quarantined = False

        #get sub info
        sub_dict = get_info(sname, driver, quarantined)

        #write info to file
        json_to_file(sname, sub_dict)

	return


#----------INIT
driver = webdriver.Firefox()
start_url = 'https://www.reddit.com/login'
driver.get(start_url)
time.sleep(1)

#----------LOGIN
log_form = driver.find_element_by_id("login-form")
username = log_form.find_element_by_id("user_login")
password = log_form.find_element_by_id("passwd_login")
username.send_keys(uname)
password.send_keys(passw)
log_form.find_element_by_xpath("/html/body/div[2]/div/div/div[2]/form/div[4]/button").click()
time.sleep(2)


#----------GET-HTML
for sname in sub:
        crawl_sub(sname)

driver.quit()
