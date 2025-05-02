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
current_time = time.localtime()
formatted_time = time.strftime("%Y-%m-%d %H:%M:%S", current_time)

# Point to Edge driver (skip path if it's in PATH)
driver = webdriver.Edge(service=service, options=options)

# Load JobStreet page
url = "https://ph.jobstreet.com/junior-data-scientist-jobs/in-Metro-Manila?sortmode=ListedDate"
driver.get(url)
   
try:
    WebDriverWait(driver, 60).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "article[data-automation='normalJob']"))
    )
except:
    print("Job listings did not load in time.")
    input("Press enter to continue")
    driver.quit()
    exit()
  
# Parse page content
soup = BeautifulSoup(driver.page_source, 'html.parser')
job_cards = soup.find_all('article', attrs={'data-automation': 'normalJob'})
print(f"Got {len(job_cards)} job listings. Displaying Results..")
for job in job_cards:
    job_title = job.find('a', attrs={'data-automation': 'jobTitle'}).text.strip()
    
    job_company = job.find('a', attrs={'data-automation': 'jobCompany'})
    if not job_company:
        job_company = job.find('span', attrs={'data-automation': 'jobCompany'})
    if job_company:
        company = job_company.text.strip()
    else:
        company = 'N/A'
    
    #job_location_spans = job.find_all('span', attrs={'data-automation': 'jobLocation'})
    #location = ', '.join([span.text.strip() for span in job_location_spans])
    
    job_listing_date = job.find('span', attrs={'data-automation': 'jobListingDate'}).text.strip()
    print("Date Obtained:", formatted_time)
    print(f"Company Name: {company}")
    print(f"Position: {job_title}")
    #print(f"Location: {location}")
    print(f"Listing date: {job_listing_date}")
    print('')


input("Press Enter to continue")
driver.quit()

