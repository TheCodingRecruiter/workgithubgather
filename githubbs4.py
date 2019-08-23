from bs4 import BeautifulSoup as bs
import time
import pandas as pd
import xlrd
import requests
import datetime
from lxml import html
from random import randint
from selenium import webdriver

now = datetime.date.today().strftime("%b-%d-%Y")
print(now)

mygithubusername = 'username'
mygithubpassword = 'password'

def rsleep():
        time.sleep(randint(1,4))

def longpause():
    time.sleep(15)

def shortpause():
    time.sleep(5)

def githubusernames(location, language):
        #### GET LIST OF USERS AND CONVERT TO EXCEL ####

        #### BUILD INITIAL URL USING DEFINED VARIABLE DATA TO GET INITAL USERCOUNT TO FIND NUMBER OF USERS AND PAGE COUNT ####
        urlcount = 1
        url = 'https://github.com/search?p=1&q=location%3Axxxx+language%3Axxxx&type=Users'
        url = url.split('xxxx')
        url = str(url[0] + location + url[1] + language + url[2])
        page = requests.get(url)
        tree = html.fromstring(page.content)
        soup = bs(page.text, "html.parser")
       
        ### GET NUMBER OF USERS/IF LETTER IN TEXT AND NOT JUST INTENGERS, SET TO CERTAIN NUMBER (INTENGER) ####
        usercount = tree.xpath('//*[@id="js-pjax-container"]/div/div[2]/nav[1]/a[9]/span/text()')
        try:
                usercount = int(usercount[0])
        except:
                usercount = 2000
        
        print(usercount)
        ### GET THE NUMBER OF PAGES BASED ON NUMBER OF USERS ####
        startingusercount = usercount
        page_numbers = round(startingusercount/10) + 1
        print(page_numbers)

        ### CREATE LIST TO USE LATER ###
        dev_names = []

        #### MAKE THE FILENAME BASED ON VARIABLES AND SET THE FILE PATH OF WHERE TO STORE THE FILE ####
        def makefilenameandpath():
                new_filename = (location + '_' + language + '_' + now)
                ext = 'xlsx'
                final_filename = '{new_filename}.{ext}'.format(new_filename=new_filename, ext=ext)
                print(final_filename)
                return 'C:/Users/dj/Desktop/Work_Dev/Githubscrapper/{final_filename}'.format(new_filename=new_filename, final_filename=final_filename)
        
        #### DEFINE VARIABLE FOR FILENAME/PATH ####
        filenameandpath = makefilenameandpath()

        #### BUILD EACH PAGE AND SCRAPE THE USERNAMES AND STORE THEM INTO A LIST TO CONVERT TO DATAFRAME THEN EXCEL ####
        for i in range(page_numbers):
                #### CREATE THE URL ####
                urlcount = urlcount + 1
                first_part_url = 'https://github.com/search?p='
                second_part_url = '&q=location%3A'
                thrid_part_url = '+language%3A'
                fourth_part_url = '&type=Users'

                url = (first_part_url + str(urlcount) + second_part_url + location + thrid_part_url + language + fourth_part_url)

                #### SCRAPE USERNAMES FROM EACH PAGE ####
                page = requests.get(url)
                soup = bs(page.text, "html.parser")
                data = soup.findAll('div', {'class' :'user-list-info ml-2 min-width-0'})
                print(url)
                
                #### PAUSE BETWEEN EACH INSTANCE RANDOMLY TO SIMULATE HUMAN INTERACTION, NOT COMPUTER ####
                rsleep()
                for thenames in data:
                        dev_names.append(thenames.get_text().split())

        #### GET THE FIRST PAGE OF DATA SINCE IT STARTS ON PAGE TWO ####
        urlcount = 1
        first_part_url = 'https://github.com/search?p='
        second_part_url = '&q=location%3A'
        thrid_part_url = '+language%3A'
        fourth_part_url = '&type=Users'
        url = (first_part_url + str(urlcount) + second_part_url + location + thrid_part_url + language + fourth_part_url)
        page = requests.get(url)
        soup = bs(page.text, "html.parser")
        data = soup.findAll('div', {'class' :'user-list-info ml-2 min-width-0'})
        print(url)

        for thenames in data:
                dev_names.append(thenames.get_text().split())
        
        time.sleep(5)     
      
        #### CONVERT TO DATAFRAME AND TO EXCEL ####
        pd.DataFrame(dev_names).to_excel(filenameandpath, header=False, index=False)
        
        #### CONVERT THE NEW FILE TO A USEABLE VARIABLE ####
        developerdatafile = (filenameandpath)

        ##### LOAD SELENIUM WEB DRIVER TO OPEN BROWSER TO GRAB EMAILS ####
        driver = webdriver.Chrome('C:\\Users\\dj\\Desktop\\Work_Dev\\Githubscrapper\\chromedriver.exe')   
        github_pro = 'https://github.com/'
        loc = (developerdatafile)
        wb = xlrd.open_workbook(loc)
        sheet = wb.sheet_by_index(0)
        sheet.cell_value(0,0)
        driver.get('https://github.com/login')
        time.sleep(3)
        username = driver.find_element_by_id('login_field')
        username.send_keys(mygithubusername)
        password = driver.find_element_by_id('password')
        password.send_keys(mygithubpassword)
        driver.find_element_by_xpath('//*[@id="login"]/form/div[3]/input[7]').click()
        shortpause()
        country = []
        dev_emails = []
        developer_name = []
        contributions = []
        gitprofile = []
        for i in range(sheet.nrows):
                print(usercount)
                rsleep()
                username = sheet.cell_value(i,0)
                githubprofile = (github_pro + username)
                driver.get(githubprofile)
                
                ### IF THEY HAVE AN EMAIL, STORE EMAIL, NAME, NUMBER OF COMMITS, AND GITHUB PROFILE TO A LIST TO MANIPULATE DATA LATER ###
                try:
                        email = driver.find_element_by_class_name('u-email ').text
                        devname = driver.find_element_by_xpath('//*[@id="js-pjax-container"]/div/div[1]/div[2]/div[2]/div[2]/h1/span[1]').text
                        commits = driver.find_element_by_xpath('//*[@id="js-pjax-container"]/div/div[3]/div[3]/div[2]/div[1]/div/h2').text
                        

       
                        dev_emails.append(email)
                        developer_name.append(devname)
                        contributions.append(commits)
                        gitprofile.append(githubprofile)
                        country.append("United States")
                        
                except:
                        pass
                ### CONVERT THE LIST TO A DATAFRAME > EXCEL ###
                collected_data = pd.DataFrame()
                collected_data['Developer Name'] = developer_name
                collected_data['Location'] = location
                collected_data['Language'] = language
                collected_data['Developer Email'] = dev_emails
                collected_data['Contributions/year'] = contributions
                collected_data['Country'] = country
                collected_data['Github Profile'] = gitprofile
                collected_data.to_excel(filenameandpath, index=False)
                usercount = usercount - 1
                time.sleep(2)
             
### CALL LOCATION AND LANGUAGE AND RUN THE PROGRAM ####
# githubusernames('boston', 'rust')




searchlocation = ['Los+Angeles', 'Houston', 'Austin', 'Raleigh', 'Charlotte', 'Dallas', 'Orlando']
for i in searchlocation:
        githubusernames(i, 'Php')
        githubusernames(i, 'Python')
        githubusernames(i, 'Javascript')
        githubusernames(i, 'Java')
        githubusernames(i, 'C++')
        githubusernames(i, 'Kotlin')
        githubusernames(i, 'Swift')
        githubusernames(i, 'Objective-c')
        githubusernames(i, 'Ruby')