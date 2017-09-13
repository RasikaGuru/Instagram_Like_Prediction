####
## Script to crawl https://influence.iconosquare.com/
## and get instagram profile information of top 100 influencers
####

from selenium import webdriver
import time
import pandas as pd
import datetime

day_index = {0: 'Monday',
             1: 'Tuesday',
             2: 'Wednesday',
             3: 'Thursday',
             4: 'Friday',
             5: 'Saturday',
             6: 'Sunday'}

driver = webdriver.Chrome("chromedriver.exe")
account_list = []
count = 0
page = 1
while(count <400):
    driver.get("https://influence.iconosquare.com/category/all/{}/followers/USA".format(page))
    time.sleep(5)
    table = driver.find_element_by_class_name("top-followers ")
    rows = table.find_elements_by_tag_name('tr')
    for row in rows:
        items = row.find_elements_by_tag_name('td')
        temp_dict = dict()
        temp_dict['Account_Name'] = items[0].find_element_by_tag_name("p").text
        temp_dict['Categories'] = items[2].text.split("\n")
        account_list.append(temp_dict)
        count+=1
    page+=1

posts =[]

count = 0

for account in account_list:
    try:
        count+=1
        print(count, account['Account_Name'])

        driver.get("https://www.instagram.com/{}/".format(account['Account_Name']))
        time.sleep(2)
        prof_details = driver.find_element_by_tag_name("ul").text.split("\n")
        prof_details = [detail.split(' ')[0] for detail in prof_details]
        if prof_details[1][-1] == 'm':
            prof_details[1] = float(prof_details[1][0:-1]) * 1000000
        elif prof_details[1][-1] == 'k':
            prof_details[1] = float(prof_details[1][0:-1]) * 1000
        else:
            prof_details[1] = float(prof_details[1])

        pic_rows = driver.find_elements_by_class_name("_70iju")
        post_links = []
        for row in pic_rows:
            pics = row.find_elements_by_tag_name("a")
            for pic in pics:
                post_links.append(pic.get_attribute("href"))

        for link in post_links:
            temp_post_dict = {'link'     : link,
                              'account'  : account['Account_Name'],
                              'followers': int(prof_details[1]),
                              'following': int(prof_details[2].replace(',','')),
                              'no_posts' : int(prof_details[0].replace(',',''))
                              }
            driver.get(link)
            time.sleep(2)

            temp_post_dict['caption'] = driver.find_element_by_class_name('_ezgzd').text.replace(temp_post_dict['account'],'')
            temp_post_dict['hashtags'] = temp_post_dict['caption'].count('#')
            temp_post_dict['mentions'] = temp_post_dict['caption'].count('@')
            try:
                likesorviews = driver.find_element_by_class_name('_m5zti').text
            except:
                likesorviews = driver.find_element_by_class_name('_nzn1h').text
            if 'likes' in likesorviews:
                temp_post_dict['isvideo'] = False
                temp_post_dict['target_lv'] = int(likesorviews.replace(' likes','').replace(',',''))
            if 'views' in likesorviews:
                temp_post_dict['isvideo'] = True
                temp_post_dict['target_lv'] = int(likesorviews.replace(' views','').replace(',',''))

            date_time = driver.find_element_by_tag_name('time').get_attribute("datetime")
            dt = datetime.datetime.strptime(date_time[:-5], "%Y-%m-%dT%H:%M:%S")
            temp_post_dict['datetime'] = date_time
            temp_post_dict['day'] = day_index[dt.weekday()]
            if dt.hour > 4 and dt.hour<11:
                temp_post_dict['timeofday'] = 'morning'
            elif dt.hour >= 11 and dt.hour<16:
                temp_post_dict['timeofday'] = 'midday'
            elif dt.hour >=16  and dt.hour<19:
                temp_post_dict['timeofday'] = 'evening'
            else:
                temp_post_dict['timeofday'] = 'night'

            posts.append(temp_post_dict)
    except:
        continue
driver.close()
df = pd.DataFrame(posts)
df.to_csv("posts.csv", index=False)