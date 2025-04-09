import json
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta
from time import sleep
options = webdriver.ChromeOptions()
options.add_argument("--no-headless")
options.add_argument("--disable-gpu")

source = "BOM"
dest = "DEL"
start_date = datetime(2025, 4, 1)
end_date = datetime(2025, 4, 30)
output_dir = f"air-irctc_scrape/{source}-{dest}/"
os.makedirs(output_dir, exist_ok=True)
driver = webdriver.Chrome(options=options)

try:
    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.strftime("%Y-%m-%d")
        url = (f"https://air.irctc.co.in/onewaytrip?type=O&origin={source}&destination={dest}" 
               f"&flight_depart_date={date_str}&ADT=1&CHD=0&INF=0&class=Economy&airlines="
               f"&ltc=0&searchtype=&isDefence=0&isSeniorCitizen=0&isStudent=0&bookingCategory=0&eType=0")
        
        driver.get(url)
        sleep(20)
        WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, '[class="right-searchbarbtm"]'))
        )
        
        cards = driver.find_elements(By.CSS_SELECTOR, '[class="right-searchbarbtm"]')
        mlist = []
        
        for card in cards:
            pp = card.text.split('\n')
            airline = pp[0].strip()
            id = pp[1]
            dept = pp[2]
            te = pp[3]
            fro = te[:-6]
            from_code = te[-4:-1]
            arriv = pp[4]
            te1 = pp[5]
            to = te1[:-6]
            to_code = te1[-4:-1]
            dur = pp[6]
            stop = pp[7]
            price = pp[8]
            
            mlist.append({
                "airline": airline,
                "flight_id": id,
                "departure": dept,
                "from": fro,
                "from_code": from_code,
                "arrival": arriv,
                "to": to,
                "to_code": to_code,
                "duration": dur,
                "stops": stop,
                "price": price
            })
            print(mlist)
        file_path = os.path.join(output_dir, f"{date_str}.json")
        with open(file_path, "w") as json_file:
            json.dump(mlist, json_file, indent=4)
        
        print(f"Saved data for {date_str}")
        current_date += timedelta(days=1)
        
finally:
    driver.quit()
