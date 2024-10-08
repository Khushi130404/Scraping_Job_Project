from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import csv
import json
import pandas as pd
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

chrome_options = Options()

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# Use IT job category on Freelancer India
query = "it-jobs"
base_url = f"https://www.freelancer.in/jobs/{query}"
driver.get(base_url)

all_data = []
pagination_links = []

try:
    # Extract pagination links
    pagination_elements = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.Pagination-link"))
    )
    for elem in pagination_elements:
        pagination_links.append(elem.get_attribute('href'))
except Exception as e:
    print(f"Error getting pagination links: {e}")

# Function to scrape job data from each page
def scrape_page():
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    job_cards = soup.select("div.JobSearchCard-item")
    for job_card in job_cards:
        try:
            job_link = job_card.select_one("a.JobSearchCard-primary-heading-link").get('href')
            full_job_link = "https://www.freelancer.in" + job_link
            driver.get(full_job_link)
            time.sleep(5)

            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')

            # Extract job details
            title_element = soup.select_one("h1.ng-star-inserted")
            title = title_element.get_text(strip=True) if title_element else "No Title Available"

            employer_element = soup.select_one("a.JobDetailsHeader-employer-name-link")
            employer = employer_element.get_text(strip=True) if employer_element else "No Employer Name Available"

            location_element = soup.select_one("app-project-view-logged-out-client-info div.NativeElement")
            location = location_element.get_text(strip=True) if location_element else "No Location Available"

            proposal_element = soup.select_one("fl-col.IconText div.NativeElement")
            proposal = proposal_element.get_text(strip=True) if proposal_element else "No Location Available"

            budget_element = soup.select_one("h2.ng-star-inserted")
            budget = budget_element.get_text(strip=True) if budget_element else "Not Disclosed"

            description_element = soup.select_one("fl-text.Project-description div.NativeElement")
            description = description_element.get_text(strip=True) if description_element else "No Description Available"

            # Save job data
            job_data = {
                "Job Title": title,
                "Employer Name": employer,
                "Budget": budget,
                "Proposal": proposal,
                "Client_Location": location,
                "Job Description": description,
            }

            print(json.dumps(job_data, ensure_ascii=False, indent=4))

            driver.back()
            time.sleep(5)
        except Exception as e:
            print(f"Error processing job card: {e}")
            driver.back()
            time.sleep(5)

# Loop through pagination links to scrape data from multiple pages
for i, page_url in enumerate(pagination_links[:3]):
    try:
        driver.get(page_url)
        time.sleep(5)
        scrape_page()
        print(f"Page {i + 1} data collected")
    except Exception as e:
        print(f"Error scraping page {i + 1}: {e}")

driver.quit()
