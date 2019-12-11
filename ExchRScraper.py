from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.firefox.options import Options
import pandas as pd
import datetime

#Take time stamp for creating the csv file, later we will format it and name the file.
now = datetime.datetime.now()

#Window size for the options to webdriver for firefox browser window
WINDOW_SIZE = "1920,1080"

#Now let's create firefox options attributes for a headless operation
firefox_options = Options()
firefox_options.headless = True
firefox_options.add_argument("--window-size=%s" % WINDOW_SIZE)

#This is the path of the firefox web driver, shipped into this package and should be in the same directory where this script is residing.
#If you change the path of the driver binary, you must change the below path variable either with absolute or relative file path
path = "./geckodriver"
try:
    driver = webdriver.Firefox(executable_path = path, options=firefox_options )
except WebDriverException as e:
    print("Aborting due to Error " + format(e))
    exit(4)

#Here the source code for an entire web page is retrieved and stored in driver object. Request is made through firefox driver.
driver.get('https://www.wsj.com/market-data/currencies/exchangerates')

#This is the most important line of the script. The class name is used to retrieve the exchange rates from the webpage.
#If there is a web page structure change happens, we need to change this class name if necessary
tbody = driver.find_elements_by_class_name("WSJTables--table__body--3yD9HkB1")
if len(tbody) == 0:
    print("Exchange Rates CSS class/structure might have been changed. Please contact the creator of the script to resolve.")
    driver.close()
    exit(1)

#Here we will retrieve only the exchange rates rows source code in html format
html_src = ""
for section in tbody:
    html_src = html_src + section.get_attribute('innerHTML')

try:
    #Below statement reads html code, the <table> and </table> manually added to avoid the format error in read_html function
    bodyFrame = pd.read_html("<table>" + html_src.__str__() + "</table>")
    with open('MarketRate_'+now.strftime("%m-%d-%Y")+'.csv',"w+", newline='') as file:
        for df in bodyFrame:
            df.to_csv(file, index=False, header=["Exchange Rate",now.strftime("%m-%d-%Y")], columns=[0,1], line_terminator='')
except IOError as e:
    print(format(e))
    print("IO Exception occurred while opening the file. Please close the file if opened.")
    driver.close()
    exit(2)
except Exception as e:
    print("-----------------------DATA FRAME START-----------------------")
    print(bodyFrame)
    print("-----------------------DATA FRAME END-----------------------")
    print(format(e))
    print("Error in parsing the scrapped exchange rate table data. Please contact the creator of the script to resolve.")
    driver.close()
    exit(3)

#Finally close the driver
driver.close()