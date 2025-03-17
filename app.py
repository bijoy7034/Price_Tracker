from flask import Flask, render_template, request
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

app = Flask(__name__)

def get_price_history(amazon_link):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    
    driver = webdriver.Chrome(options=options)
    driver.get("https://pricehistory.app/")
    
    search_box = driver.find_element(By.ID, "search")
    search_box.send_keys(amazon_link)
    search_box.send_keys(Keys.RETURN)  

    time.sleep(10)  

    price_data = driver.execute_script("return chart.data.datasets[1].data;")
    history = [{"x": str(i["x"]), "y": i["y"]} for i in price_data]  

    try:
        product_details_div = driver.find_element(By.ID, "product-info")
        product_details = product_details_div.get_attribute("innerHTML")  
        product_image = driver.find_element(By.CSS_SELECTOR, ".card-img img").get_attribute("src")

        # Extract supporting text
        supporting_text_elements = driver.find_elements(By.CLASS_NAME, "supporting-text.mb-0")
        supporting_text = [el.text for el in supporting_text_elements]

        # Extract the whole table
        table_element = driver.find_element(By.CLASS_NAME, "table")
        table_html = table_element.get_attribute("outerHTML")

    except:
        product_details = "No product details found"
        supporting_text = []
        table_html = ""

    driver.quit()

    return history, product_details, product_image, supporting_text, table_html

@app.route("/", methods=["GET", "POST"])
def index():
    price_history = None
    min_price = None
    max_price = None
    product_details = None
    product_image = None 
    supporting_text = None
    table_html = None

    if request.method == "POST":
        amazon_link = request.form["amazon_link"]
        price_history, product_details, product_image, supporting_text, table_html = get_price_history(amazon_link)

        if price_history:
            prices = [entry["y"] for entry in price_history]
            min_price = min(prices)
            max_price = max(prices)

    return render_template(
        "index.html",
        price_history=price_history,
        min_price=min_price,
        max_price=max_price,
        product_details=product_details,
        product_image=product_image,
        supporting_text=supporting_text,
        table_html=table_html
    )

if __name__ == "__main__":
    app.run(debug=True)
