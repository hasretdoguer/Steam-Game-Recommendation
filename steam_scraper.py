from selenium import webdriver
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import csv
import pandas as pd


PATH = "C:\Program Files\chromedriver.exe"
options = webdriver.ChromeOptions()
chrome_prefs = {}
options.experimental_options["prefs"] = chrome_prefs
chrome_prefs["profile.default_content_settings"] = {"images": 2}
chrome_prefs["profile.managed_default_content_settings"] = {"images": 2}
options.add_argument('headless')
driver = webdriver.Chrome(PATH,options=options)
#driver.get("https://store.steampowered.com/search/?sort_by=Reviews_DESC&ignore_preferences=1")
#driver.get("https://store.steampowered.com/search/?sort_by=Reviews_DESC&ignore_preferences=1&tags=3813%2C4182")
driver.get("https://store.steampowered.com/search/?sort_by=Reviews_DESC&ignore_preferences=1&tags=21&untags=19%2C4182%2C597%2C492&category1=998")#1.2.1
#driver.get("https://store.steampowered.com/search/?sort_by=Reviews_DESC&ignore_preferences=1&tags=19%2C21%2C4182%2C4166&untags=1742%2C492&category1=998")#1.2.2

class element_has_css_class(object):
  """An expectation for checking that an element has a particular css class.

  locator - used to find the element
  returns the WebElement once it has the particular css class
  """
  def __init__(self, locator, css_class):
    self.locator = locator
    self.css_class = css_class

  def __call__(self, driver):
    element = driver.find_element(*self.locator)   # Finding the referenced element
    if self.css_class in element.get_attribute("style"):
        return element
    else:
        return False

# Get scroll height.
last_height = driver.execute_script("return document.body.scrollHeight")

while True:
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load the page.
    wait = WebDriverWait(driver, 10)
    element = wait.until(element_has_css_class((By.XPATH, "//div[@id='search_results_loading']"), "display: none;"))

        # Calculate new scroll height and compare with last scroll height.
    new_height = driver.execute_script("return document.body.scrollHeight")

    if new_height == last_height:
        break

    last_height = new_height

#driver.find_element_by_id("language_pulldown").click()
#driver.find_element_by_xpath("//a[@onclick='ChangeLanguage( 'english' ); return false;']").click()
elements = []

try:
    elements = driver.find_elements_by_xpath("//div[@class='responsive_search_name_combined']")
except Exception as e:
    print(e)
    driver.quit()


data = {}
data.setdefault("game_name", [])
data.setdefault("platform_names", [])
data.setdefault("release_date", [])
data.setdefault("rating", [])
data.setdefault("price", [])
data.setdefault("game_tags", [])
count = 0
 
for element in elements:

    hover = ActionChains(driver).move_to_element(element).perform()
    time.sleep(0.5)
    
    try:
        game_names = element.find_elements_by_xpath("//span[@class='title']")[count]
        data["game_name"].append(game_names.text)

    except:
        data["game_name"].append(None)
        
    try:
        platform = element.find_elements_by_xpath("//div[@class='col search_name ellipsis']")[count]
        platform_p = platform.find_element_by_tag_name("p")
        platform_names = platform_p.find_elements_by_tag_name("span")
        p_name = []
        for k in platform_names:
            p_names = k.get_attribute("class")
            p_name.append(p_names)
        data["platform_names"].append(p_name)
    except:
        data["platform_names"].append(None)
        
    try:
        release_dates = element.find_elements_by_xpath("//div[@class='col search_released responsive_secondrow']")[count]
        data["release_date"].append(release_dates.text)

    except:
        data["release_date"].append(None)

    try:

        rating_name = element.find_elements_by_xpath("//div[@class='col search_reviewscore responsive_secondrow']")[count]
        ratings = rating_name.find_element_by_tag_name("span").get_attribute("data-tooltip-html")
        data["rating"].append(ratings)

    except:
        data["rating"].append(None)    
    
    try:
        price = element.find_elements_by_xpath("//div[@class='col search_price_discount_combined responsive_secondrow']")[count].get_attribute('data-price-final')
        data["price"].append(price)
    except:
        data["price"].append(None)
    
    try:
        user_tag = driver.find_element_by_xpath("//div[@id='global_hover_content']")
        tag_hover = user_tag.find_elements_by_xpath("//div[starts-with(@id,'hover_')]")
        print(len(tag_hover))
        tags = tag_hover[-1].find_elements_by_class_name("app_tag") 
        tag_list = []
        for x in tags:
             tag_list.append(x.get_attribute("textContent"))   
        data["game_tags"].append(tag_list)
        
    except Exception as e:
        data["game_tags"].append(None)
        print(e)       
    
    count += 1
    
df = pd.DataFrame(data=data)
compression_opts = dict(method='zip', archive_name='steam111.csv')
df.to_csv('steam111.zip', index=False,
          compression=compression_opts)
