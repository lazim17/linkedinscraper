from flask import Flask, request
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pymongo import MongoClient
import time
import os

app = Flask(__name__)


#mongo_client = MongoClient(f"mongodb://{os.getenv("MONGO_USER")}:{os.getenv("MONGO_PASSWORD")}@{os.getenv("MONGO_HOST")}:{os.getenv("MONGO_PORT")}/")
mongo_client = MongoClient("mongodb://localhost:27017/")


db = mongo_client["linkedin_data"]
companies_collection = db["companies"]

firefox_options = Options()
firefox_options.add_argument("--headless")

service = Service("/usr/bin/geckodriver")  
driver = webdriver.Firefox(service=service, options=firefox_options)

@app.route('/linkedin/data', methods=['GET'])
def get_profile_data():
    company = request.args.get('company')
    if not company:
        return "Missing company parameter", 400

    url = f"https://www.linkedin.com/company/{company}/"
    driver.get(url)
    time.sleep(5)

    try:
        sign_in_button = driver.find_element(By.XPATH, "//button[contains(@class, 'sign-in-modal__outlet-btn')]")
        sign_in_button.click()
        try:
            email_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "base-sign-in-modal_session_key"))
            )
            email_field.send_keys(os.getenv("EMAIL"))

            password_field = driver.find_element(By.ID, "base-sign-in-modal_session_password")
            password_field.send_keys(os.getenv("PASS"))

            signin_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Sign in')]")
            ))
            signin_button.click()
            time.sleep(5)
        except Exception as e:
            print("Login failed:", e)
    except Exception:
        pass  

    try:
        name = driver.find_elements(By.CLASS_NAME, "org-top-card-summary__title")[0].text
        first_subline = driver.find_elements(By.CLASS_NAME, "org-top-card-summary-info-list")[0].text
        parts = first_subline.split()

        industry = " ".join(parts[:2])
        location = " ".join(parts[2:4])
        followers = parts[4]
        company_size = " ".join(parts[-2:])

        driver.get(f'https://www.linkedin.com/company/{company}/about/')
        time.sleep(5)

        desc = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "p.break-words.white-space-pre-wrap.t-black--light.text-body-medium"))
        ).text

        company_data = {
            "name": name,
            "industry": industry,
            "location": location,
            "followers": followers,
            "company_size": company_size,
            "description": desc
        }

        companies_collection.insert_one(company_data)

        print(f"Company: {name}")
        print(f"Industry: {industry}")
        print(f"Location: {location}")
        print(f"Followers: {followers}")
        print(f"Company Size: {company_size}")
        print(f"Description: {desc}")

        return "Data fetched and saved successfully", 200
    except Exception as e:
        print("Data extraction failed:", e)
        return "Data extraction failed", 500

if __name__ == '__main__':
    app.run(debug=True)
