from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import smtplib

options = webdriver.ChromeOptions()
options.add_argument("--headless")  
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")

# INITIALIZER
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# URL
url = 'https://www.amazon.com/Dymatize-Protein-Isolate-Gourmet-Vanilla/dp/B00G6QHYZ6?pd_rd_w=QLnO4&content-id=amzn1.sym.1c5f8f79-ee2f-4fb3-a1b5-3d8384cdfaf3&pf_rd_p=1c5f8f79-ee2f-4fb3-a1b5-3d8384cdfaf3&pf_rd_r=390MWH2T8EQV1DRCEQ5Z&pd_rd_wg=cQUrm&pd_rd_r=55e6860d-f432-4e8e-b439-6fca56853761&pd_rd_i=B00G6QHYZ6&psc=1&ref_=pd_bap_d_grid_rp_0_1_ec_scp_pd_nav_hcs_rp_1_t'
driver.get(url)

# Wait
driver.implicitly_wait(3)  

# Get and Parse page source
page_source = driver.page_source
soup = BeautifulSoup(page_source, 'lxml')

TARGET_PRICE = float(input("Enter the target price: "))

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

def send_email(product_name, product_price, url):
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        server.ehlo()

        server.login('williamli0610@gmail.com', 'qvbi vmsm ajne nhzm')

        subject = f"Price Drop Alert: {product_name}"
        body = f"The price for {product_name} has dropped to ${product_price}! You can use this link to head to the product page: {url}"
        msg = f"Subject: {subject}\n\n{body}"

        server.sendmail(
            'williamli0610@gmail.com',
            'williamli0610@gmail.com',
            msg
        )
        server.quit()
        print("Email has been sent!")

    except Exception as e:
        print(f"Failed to send email: {e}")

check_info()
driver.quit()