from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import smtplib
import os
from dotenv import load_dotenv
import time 


load_dotenv()

EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS')
APP_PASSWORD = os.getenv('APP_PASSWORD')

options = webdriver.ChromeOptions()
options.add_argument("--headless")  
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")

# INITIALIZER
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# URL
url = input("Enter the amazon product page URL to start:")
driver.get(url)

# Wait
driver.implicitly_wait(3)  

# Get and Parse page source
page_source = driver.page_source
soup = BeautifulSoup(page_source, 'lxml')

TARGET_PRICE = float(input("Enter the target price: "))
EMAIL = input("Enter your email address: ")

def check_info():
    try:
        product_name = soup.find(id='productTitle').get_text().strip()  # PRODUCT_NAME
        price_whole = soup.find(class_='a-price-whole').get_text().strip()  # PRODUCT_PRICE IN DOLLARS
        price_fraction = soup.find(class_='a-price-fraction').get_text().strip()  # PRODUCT_PRICE IN CENTS
        product_price = float(f'{price_whole}{price_fraction}')

        # Handle list price
        list_price_element = soup.find(class_='a-size-small aok-offscreen')  # PRODUCT_ORIGINAL_PRICE OR PRICE PER OUNCE
        if list_price_element and 'list price:' in list_price_element.get_text().strip().lower():
            list_price = list_price_element.get_text().strip()
        else:
            list_price = product_price

        # Check if Subscribe & Save is available
        subscription_available = any("subscribe & save" in element.get_text().lower() for element in soup.find_all())

        if product_price < TARGET_PRICE:
            send_email(product_name, product_price, url)

        # Output results
        print(f"Product Name: {product_name}")
        print(f"Product Price: {product_price}")
        print(f"Originally Listed Price: {list_price}")
        print(f"Subscribe & Save Available: {subscription_available}")
        
    except Exception as e:
        print(f"An error occurred: {e}")

def send_email(product_name, product_price, url, EMAIL):
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        server.ehlo()

        server.login(EMAIL_ADDRESS, APP_PASSWORD)

        subject = f"Price Drop Alert: {product_name}"
        body = f"The price for {product_name} has dropped to ${product_price}! You can use this link to head to the product page: {url}"
        msg = f"Subject: {subject}\n\n{body}"

        server.sendmail(
            EMAIL_ADDRESS,
            EMAIL,
            msg
        )
        server.quit()
        print("Email has been sent!")

    except Exception as e:
        print(f"Failed to send email: {e}")

while True:
    if check_info():
        break

    time.sleep(86400)
driver.quit()