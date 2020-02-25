from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import requests
import urllib.request
import csv
import numpy as np
import pandas as pd

#
#Sets original URL and pulls the html code
#
webpage_url = 'http://hurricanes.ice.nhl.com/club/gamelog.htm'
url = requests.get(webpage_url)
html_text= url.text
html = BeautifulSoup(html_text,'lxml')
#print(html_text)

#Used to print out a copy of the HTML text to an outside text editor
#Should remain commented out unless a copy is needed in the future
#
#html_file = open("Hockey HTML Text","w")
#html_file.write(html_text)
#html_file.close()
#

#Loops through the season selector dropdown to grab all available years
#Appends them to seasonlist to be used with the dropdown selector later
season_list = []
for season_finder in html.find_all("option"):
    season_selector = season_finder.text
    if season_selector not in season_list: 
        season_list.append(season_selector)
season_list.remove("Regular")
season_list.remove("Playoff")
#print(season_list)

#opens up Chrome to specified webpage
driver = webdriver.Chrome()
driver.get(webpage_url)
driver.maximize_window()


def load_season_page(season_year):
    driver.find_element_by_xpath("//*[@id='PropertySelection']").send_keys(season_year)
    go_button = driver.find_element_by_xpath("//*[@id='Submit']")
    go_button.click()
           
    #       
    #Waits until url is updated after selecting specific season from dropdown
    #Grabs current URL and appends the home-game selector information on the end
    #Navigates to the new url
    #
    first_year = season_year[:3]
    url_wait_for = webpage_url + "?season=" + first_year 
    WebDriverWait(driver, 10).until(EC.url_contains(url_wait_for))
    season_specific_url = driver.current_url
    home_game_url = '&srt=date&venue=H'
    view_home_games = season_specific_url + home_game_url
    driver.get(view_home_games)

def scrape_for_attendance():
	#
	#Iterates through the attendance column and appends the value to the attendance list
	#Stores list in a dictionary with the season year set as the key value
	#
	yearly_att = []
	att_column = list(range(3,44))
	for column_position in att_column:
		try:
		    xpath_grid_marker = '/html/body/div[1]/div[2]/div[1]/div/div[1]/div[3]/div/table/tbody/tr[{}]/td[18]'.format(column_position)
		    att_number = driver.find_element_by_xpath(xpath_grid_marker).text
		    yearly_att.append(att_number)
		except:
			print("No xpath for column {} in years {}".format(column_position, season_list[season_year]))
			yearly_att.append("NULL")
	dict_by_season[season_list[season_year]]= yearly_att


#pass in season year
num_of_seasons = len(season_list)
season_year = 0
dict_by_season = {}

#Continues looping until you collect attendance info on every year in dropdown
while season_year < num_of_seasons:
    load_season_page(season_list[season_year])
    scrape_for_attendance()
    season_year +=1

#Stores dictionary data in a dataframe
#Exports df to file specified
df = pd.DataFrame(data=dict_by_season)
df.to_csv(r'C:\Users\Emily\Documents\Python Notebooks\Attendance_by_Year_DF.csv')

#closes out webbrowser
driver.close()

