import time
import csv
import os
import math

from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from bs4 import BeautifulSoup

# Set up Edge options
options = Options()
service = Service(log_pathos=os.devnull)
options.use_chromium = True
#options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument('--log-level=3')
options.add_experimental_option('excludeSwitches', ['enable-logging'])

current_time = time.localtime()
formatted_time = time.strftime('%Y-%m-%d %H:%M:%S', current_time)

# Point to Edge driver (skip path if it's in PATH)
driver = webdriver.Edge(service=service, options=options)

# Load JobStreet page and divide it into sections that will be concatenated when accessing other pages
url = 'https://ph.jobstreet.com/junior-data-scientist-jobs/in-Metro-Manila?sortmode=ListedDate'

#filename = 'jobstreet_jobs.csv'
job_data = []                    

def initialize_csv(filename):
    """ Creates a blank csv file to save results
    
    Args:
        filename: string of csv file name .
    Returns:
        None
    """
    file_existing = os.path.exists(filename)
    
    if not file_existing:
        print(f'No filename found. Creating {filename}...')
        with open(filename, mode = 'w', newline = '', encoding = 'utf-8-sig') as file:
            pass
    else:
        print(f'Filename found. Results to be saved in {filename}' )
        return

def append_to_file (job_data, filename):
    """ Appends scraping results to an existing csv filename.

        If csv is empty, create headers according to job_data keys

    Args:
        job_data: list of dictionaries of job listing information
        filename: string of csv name that will contain scraped job posts.
    Returns:
        saved_jobs: int of total number of jobs appended
    """
    saved_jobs = len(job_data)
    if not job_data:
        print('No data found.')
    else:
        field_names = job_data[0].keys()
        file_is_empty = os.stat(filename).st_size == 0
        print(f'Attaching {len(job_data)} job listings on {filename}')

        with open(filename, mode = 'a', newline = '', encoding = 'utf-8-sig') as file:
            writer = csv.DictWriter(file, fieldnames = field_names)
            if file_is_empty:
                writer.writeheader()
            writer.writerows(job_data)
        #saved_jobs = len(job_data)
        job_data.clear()
    
    return saved_jobs
  
def wait_for_website(web_url):
    """ Waits for a website to load contents that are classified as normal jobs.

    Args:
        web_url: string of website url to load.
    Returns:
       bool: True if website properly loads.
             False if website did not load.
    """
    driver.get(web_url)  
    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "article[data-automation='normalJob']"))
        )
        return True
    except:
        print('Job listings did not load in time.')
        return False

def parse_page_contents(web_url, first_page = True):
    """ Parses website contents for all job postings.
       
        When used on the first page of a search result url, 
        include total search results and number of search pages.
       
        When used on succeeding pages, return job postings only.

    Args:
        web_url: string of website url to load.
        first_page: Boolean for separting return values of first web search
                    and next pages.
    Returns:
        job_cards: iterable query result for all job postings in a page
        job_total: integer total amount of jobs found
        search_pages: integer number of search pages for total amount of jobs
    """
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    job_cards = soup.find_all('article', attrs={'data-automation': 'normalJob'})
    
    if first_page:
        job_total = soup.find('span', attrs={'data-automation': 'totalJobsCount'}).text.strip()
        search_pages = math.ceil(int(job_total) / len(job_cards))
    
        #Verify amount of job posts found
        print(f'Got {int(job_total)} job listings across {search_pages} pages. Displaying {len(job_cards)} Results..')
        print(f'Number of jobs in this page: {len(job_cards)}')
        
        return job_cards, job_total, search_pages
    else:
        return job_cards, None, None
    
def parse_multiple_pages(search_pages, web_url, saved_jobs_count):
    """ Parses website contents for all job postings in succeeding search pages.
       
        Partitions the url into segments to include the page number segment in url.
        Loops through each page to collect job posts

    Args:
        search_pages: integer number of search pages for total amount of jobs
        web_url: string of website url to load.
        saved_jobs_count: int amount of jobs saved to csv on first page
    Returns:
        saved_jobs_count: int running total amount of jobs saved to csv
    """

    url_parts = web_url.partition('?')
    for page in range(2, search_pages + 1):
        next_page = f'{url_parts[0]}{url_parts[1]}page={str(page)}&{url_parts[2]}'
        wait_for_website(next_page)
        if not wait_for_website:
            print(f'No job posting found on page {page}.')
            break
        else:
            job_cards, _, _ = parse_page_contents(next_page, first_page = False)
            print(f'Number of jobs in page {page}: {len(job_cards)}')
            page_job_data = extract_job_data(job_cards)
            saved_jobs_count += append_to_file(page_job_data, filename)
            time.sleep(5)
    return saved_jobs_count

def extract_job_data(job_cards):
    """ Parses website contents for all job postings in succeeding search pages.
       
        Partitions the url into segments to include the page number segment in url.
        Loops through each page to collect job posts and stores them in a job data
        dictionary.

    Args:
        job_cards: iterable query result for all job postings in a page
    Returns:
        job_data: list of dictionaries for job data infornmation in a page
    """
    for job in job_cards:
        job_title = job.find('a', attrs={'data-automation': 'jobTitle'}).text.strip()
        
        #Some jobs lists the company name in <span> tags to indicate private advertisers.
        #Otherwise, <a> tags contain company's name
        job_company = job.find('a', attrs={'data-automation': 'jobCompany'})
        if not job_company:
            job_company = job.find('span', attrs={'data-automation': 'jobCompany'})
        if job_company:
            company = job_company.text.strip()
        else:
            company = 'N/A'
        
        #Location is divided into two parts, name and region, under <span> tag   
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
        job_url = 'https://ph.jobstreet.com' + link_href if link_href else 'N/A'
        
        #Each job result is logged into a dictionary to be appended in list.    
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
    return job_data

initialize_csv(filename)
       
wait_for_website(url)
job_cards, job_total, search_pages = parse_page_contents(url)
page_job_data = extract_job_data(job_cards)
saved_jobs_count = append_to_file(page_job_data, filename)
time.sleep(5)

if search_pages > 1:
    total_saved_jobs = parse_multiple_pages(search_pages,url,saved_jobs_count)

print(f'Done saving {total_saved_jobs} job listings on {filename}')
time.sleep(5)
driver.quit()