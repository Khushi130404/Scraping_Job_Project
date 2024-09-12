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

base_url = "https://www.freelancer.in/jobs/"
driver.get(base_url)

all_data = []
pagination_links = []

try:
    pagination_elements = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.Pagination-link"))
    )
    for elem in pagination_elements:
        pagination_links.append(elem.get_attribute('href'))
except Exception as e:
    print(f"Error getting pagination links: {e}")

# Step 2: Scrape the data from the current page
def scrape_page():
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    job_cards = soup.select("div.JobSearchCard-item")
    for job_card in job_cards:
        try:
            job_link = job_card.select_one("a.JobSearchCard-primary-heading-link").get('href')
            driver.get(job_link)
            time.sleep(5)

            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')

            title_element = soup.select_one("h1.JobDetailsHeader-title")
            title = title_element.get_text(strip=True) if title_element else "No Title Available"

            employer_element = soup.select_one("a.JobDetailsHeader-employer-name-link")
            employer = employer_element.get_text(strip=True) if employer_element else "No Employer Name Available"

            location_element = soup.select_one("span.Location-label")
            location = location_element.get_text(strip=True) if location_element else "No Location Available"

            budget_element = soup.select_one("span.JobDetailsHeader-budget")
            budget = budget_element.get_text(strip=True) if budget_element else "Not Disclosed"

            description_element = soup.select_one("div.JobDetails-description-content")
            description = description_element.get_text(strip=True) if description_element else "No Description Available"

            job_data = {
                "Job Title": title,
                "Employer Name": employer,
                "Location": location,
                "Budget": budget,
                "Job Description": description,
            }
            all_data.append(job_data)

            driver.back()
            time.sleep(5)
        except Exception as e:
            print(f"Error processing job card: {e}")
            driver.back()
            time.sleep(5)

for i, page_url in enumerate(pagination_links[:3]):
    try:
        driver.get(page_url)
        time.sleep(5)
        scrape_page()
        print(f"Page {i + 1} data collected")
    except Exception as e:
        print(f"Error scraping page {i + 1}: {e}")

driver.quit()

# Save data to CSV, Excel, and JSON files
csv_file = "freelancer_job_data.csv"
keys = all_data[0].keys() if all_data else []
with open(csv_file, "w", newline="", encoding="utf-8") as output_file:
    dict_writer = csv.DictWriter(output_file, fieldnames=keys)
    dict_writer.writeheader()
    dict_writer.writerows(all_data)

excel_file = "freelancer_job_data.xlsx"
df = pd.DataFrame(all_data)
df.to_excel(excel_file, index=False)

json_file = "freelancer_job_data.json"
with open(json_file, "w", encoding="utf-8") as json_output_file:
    json.dump(all_data, json_output_file, ensure_ascii=False, indent=4)

print("Data saved to CSV, Excel, and JSON files.")