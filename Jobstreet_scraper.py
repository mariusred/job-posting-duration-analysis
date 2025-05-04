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
import math

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
url_parts = url.partition('?')

driver.get(url)
 
#Let the webpage load and look for job posts in article tag. If none, initiate timeout.  
try:
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "article[data-automation='normalJob']"))
    )
except:
    print("Job listings did not load in time.")
    time.sleep(5)
    driver.quit()
    exit()

filename = 'jobstreet_jobs.csv'
job_data = []

# Parse page content
soup = BeautifulSoup(driver.page_source, 'html.parser')

job_cards = soup.find_all('article', attrs={'data-automation': 'normalJob'})
job_total = soup.find('span', attrs={'data-automation': 'totalJobsCount'}).text.strip()
search_pages = math.ceil(int(job_total) / len(job_cards))
#Verify amount of job posts found
print(f"Got {int(job_total)} job listings across {search_pages} pages. Displaying {len(job_cards)} Results..")
print(f'Number of jobs in page 1: {len(job_cards)}')

def extract_job_data(job):
    job_title = job.find('a', attrs={'data-automation': 'jobTitle'}).text.strip()
    
    job_company = job.find('a', attrs={'data-automation': 'jobCompany'})
    if not job_company:
        job_company = job.find('span', attrs={'data-automation': 'jobCompany'})
    if job_company:
        company = job_company.text.strip()
    else:
        company = 'N/A'
    
    job_location_spans = job.find_all('span', attrs={'data-automation': 'jobLocation'})
    location_parts = []
    for span in job_location_spans:
        location_parts.append(span.text.strip())
    location = ', '.join(location_parts)
    
    job_classification = job.find('span', attrs={'data-automation':'jobSubClassification'})
    if not job_classification:
        job_classification = 'N/A'
    else:
        job_classification = job_classification.text.strip()
    
    job_industry = job.find('span', attrs={'data-automation':'jobClassification'})
    if not job_industry:
        job_industry = 'N/A'
    else:
        job_industry = job_industry.text.strip()[1:-1]
    
    job_salary = job.find('span', attrs={'data-automation':'jobSalary'})
    if not job_salary:
        job_salary = 'N/A'
    else:
        job_salary = job_salary.text.strip()
    
    job_setup = job.find('span', attrs={'data-testid':'work-arrangement'})
    if not job_setup:
        job_setup = 'N/A'
    else:
        job_setup = job_setup.text.strip()[1:-1]
        
    job_listing_date = job.find('span', attrs={'data-automation': 'jobListingDate'}).text.strip()
    
    job_link = job.find('a', attrs={'data-automation':'job-list-view-job-link'})
    link_href = job_link.get('href')
    job_url = "https://ph.jobstreet.com" + link_href if link_href else 'N/A'
    
    job_data_entry = job_data.append({
        'Date Obtained': formatted_time,
        'Link' : job_url,
        'Company' : company,
        'Position' : job_title,
        'Location' : location,
        'Classification' : job_classification,
        'Industry' : job_industry,
        'Salary' : job_salary,
        'Work Arrangement' : job_setup,
        'Day Posted' : job_listing_date
    })
    print(f'Current data rows: {len(job_data)}')
    return

for job in job_cards:
    extract_job_data(job)
time.sleep(5)

if search_pages > 1:
    for page in range(2, search_pages + 1):
        next_page = url_parts[0] + url_parts[1] + 'page=' + str(page) + '&' + url_parts[2]
        driver.get(next_page)
 
        #Let the webpage load and look for job posts in article tag. If none, initiate timeout.  
        try:
            WebDriverWait(driver, 20).until(
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
        print(f'Number of jobs in page {page}: {len(job_cards)}')
        for job in job_cards:
            extract_job_data(job)
        time.sleep(5)

field_names = job_data[0].keys()
with open(filename, mode = 'w', newline = '', encoding = 'utf-8-sig') as file:
        writer = csv.DictWriter(file, fieldnames = field_names)
        writer.writeheader()
        writer.writerows(job_data)
        
print(f'Done saving {len(job_data)} job listings on {filename}')
time.sleep(10)
driver.quit()


'''
#Extract relevant information from each job post
for job in job_cards:
    #Name of the job opening
    job_title = job.find('a', attrs={'data-automation': 'jobTitle'}).text.strip()
    
    #Company name. Some job posts have private advertisers which are under span tags
    #the if statement checks for those instances
    job_company = job.find('a', attrs={'data-automation': 'jobCompany'})
    if not job_company:
        job_company = job.find('span', attrs={'data-automation': 'jobCompany'})
    if job_company:
        company = job_company.text.strip()
    else:
        company = 'N/A'
    
    #Job locations are divided into two span tags under one span parent tag. 
    #Loop on each tag to output one location data
    job_location_spans = job.find_all('span', attrs={'data-automation': 'jobLocation'})
    location_parts = []
    for span in job_location_spans:
        location_parts.append(span.text.strip())
    location = ', '.join(location_parts)
    
    #Job role department
    job_classification = job.find('span', attrs={'data-automation':'jobSubClassification'})
    if not job_classification:
        job_classification = 'N/A'
    else:
        job_classification = job_classification.text.strip()
    
    #Job role industry
    job_industry = job.find('span', attrs={'data-automation':'jobClassification'})
    if not job_industry:
        job_industry = 'N/A'
    else:
        job_industry = job_industry.text.strip()[1:-1]
    
    #Monthly salary of job role (if specified)
    job_salary = job.find('span', attrs={'data-automation':'jobSalary'})
    if not job_salary:
        job_salary = 'N/A'
    else:
        job_salary = job_salary.text.strip()
    
    #Indicates work arrangement if on-site, remote, or hybrid
    job_setup = job.find('span', attrs={'data-testid':'work-arrangement'})
    if not job_setup:
        job_setup = 'N/A'
    else:
        job_setup = job_setup.text.strip()[1:-1]
    
    #Time posted relative to date of scraping
    job_listing_date = job.find('span', attrs={'data-automation': 'jobListingDate'}).text.strip()
    
    #Parse the gathered href to jobstreet website. For later use in gathering required skills
    job_link = job.find('a', attrs={'data-automation':'job-list-view-job-link'})
    link_href = job_link.get('href')
    job_url = "https://ph.jobstreet.com" + link_href if link_href else 'N/A'
    
    
    driver.get(job_url)
 
    #Let the webpage load and look for job posts in article tag. If none, initiate timeout.  
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
    
    
    print("Date Obtained:", formatted_time)
    print(f"Link: {job_url}")
    print(f"Company Name: {company}")
    print(f"Position: {job_title}")
    print(f"Location: {location}")
    print(f"Classification: {job_classification}")
    print(f"Industry: {job_industry}")
    print(f"Salary: {job_salary}")
    print(f"Work Arrangement: {job_setup}")
    print(f"Listing date: {job_listing_date}")
    print('')

    #Get a key-value pair for each result and attach the resulting pair to the overall job data
    job_data_entry = job_data.append({
        'Date Obtained': formatted_time,
        'Link' : job_url,
        'Company' : company,
        'Position' : job_title,
        'Location' : location,
        'Classification' : job_classification,
        'Industry' : job_industry,
        'Salary' : job_salary,
        'Work Arrangement' : job_setup,
        'Day Posted' : job_listing_date
    })
    print('')    
'''   

