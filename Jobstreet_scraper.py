from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import csv
import os

# Set up Edge options
options = Options()
service = Service(log_pathos=os.devnull)
options.use_chromium = True
#options.add_argument("--headless")
options.add_argument("--disable-gpu")

# Point to Edge driver (skip path if it's in PATH)
driver = webdriver.Edge(service=service, options=options)

# Load JobStreet page
url = "https://ph.jobstreet.com/junior-data-scientist-jobs/in-Metro-Manila?sortmode=ListedDate"
driver.get(url)
   
try:
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "a[data-automation='jobTitle']"))
    )
except:
    print("Job listings did not load in time.")
    input("Press enter to continue")
    driver.quit()
    exit()
  
# Parse page content
soup = BeautifulSoup(driver.page_source, 'html.parser')
job_cards = soup.find_all('a', attrs={'data-automation': 'jobTitle'})

for job in job_cards:
    print(job.prettify())

driver.quit()

